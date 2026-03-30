"""
DAST Crawl Engine – SPA-Aware Selenium Crawler
Crawls React/Angular/Vue apps, extracts forms, inputs, buttons, links, query params.
Returns structured endpoint map: [{endpoint, method, parameters}]
"""

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from urllib.parse import urljoin, urlparse, parse_qs
import time
import logging

logger = logging.getLogger(__name__)


def _create_driver():
    """Create a headless Chrome WebDriver instance."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    try:
        from webdriver_manager.chrome import ChromeDriverManager
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options,
        )
    except Exception:
        driver = webdriver.Chrome(options=chrome_options)

    driver.set_page_load_timeout(30)
    return driver


def _is_same_domain(base_url, target_url):
    """Check if target URL belongs to the same domain as base URL."""
    base_domain = urlparse(base_url).netloc
    target_domain = urlparse(target_url).netloc
    return target_domain == base_domain or target_domain == ""


def _extract_query_params(url):
    """Extract query parameters from a URL."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return {k: v[0] if len(v) == 1 else v for k, v in params.items()}


def _scroll_page(driver):
    """Scroll through the entire page to trigger lazy-loaded content."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    driver.execute_script("window.scrollTo(0, 0);")


def _extract_forms(driver, page_url):
    """Extract all forms from the current page."""
    forms_data = []
    try:
        forms = driver.find_elements(By.TAG_NAME, "form")
        for form in forms:
            try:
                action = form.get_attribute("action") or page_url
                method = (form.get_attribute("method") or "get").upper()
                full_action = urljoin(page_url, action)

                parameters = []

                # Extract input fields
                inputs = form.find_elements(By.TAG_NAME, "input")
                for inp in inputs:
                    name = inp.get_attribute("name")
                    input_type = inp.get_attribute("type") or "text"
                    if name:
                        parameters.append({
                            "name": name,
                            "type": input_type,
                            "element": "input",
                        })

                # Extract textarea fields
                textareas = form.find_elements(By.TAG_NAME, "textarea")
                for ta in textareas:
                    name = ta.get_attribute("name")
                    if name:
                        parameters.append({
                            "name": name,
                            "type": "textarea",
                            "element": "textarea",
                        })

                # Extract select fields
                selects = form.find_elements(By.TAG_NAME, "select")
                for sel in selects:
                    name = sel.get_attribute("name")
                    if name:
                        parameters.append({
                            "name": name,
                            "type": "select",
                            "element": "select",
                        })

                # Check for CSRF token fields
                has_csrf = any(
                    p["name"].lower() in [
                        "csrf_token", "_token", "csrfmiddlewaretoken",
                        "_csrf", "csrf", "xsrf_token", "_xsrf",
                        "authenticity_token",
                    ]
                    for p in parameters
                )

                forms_data.append({
                    "endpoint": full_action,
                    "method": method,
                    "parameters": parameters,
                    "source_page": page_url,
                    "has_csrf_token": has_csrf,
                })
            except Exception as e:
                logger.debug(f"Error extracting form: {e}")
    except Exception as e:
        logger.debug(f"Error finding forms: {e}")

    return forms_data


def _extract_links(driver, base_url):
    """Extract all internal links from the current page."""
    links = set()
    try:
        anchors = driver.find_elements(By.TAG_NAME, "a")
        for anchor in anchors:
            href = anchor.get_attribute("href")
            if href and not href.startswith(("javascript:", "mailto:", "tel:", "#")):
                full_url = urljoin(base_url, href)
                if _is_same_domain(base_url, full_url):
                    # Strip fragment
                    parsed = urlparse(full_url)
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    if parsed.query:
                        clean_url += f"?{parsed.query}"
                    links.add(clean_url)
    except Exception as e:
        logger.debug(f"Error extracting links: {e}")
    return links


def _extract_buttons(driver, page_url):
    """Extract standalone buttons (outside forms) that may trigger actions."""
    buttons_data = []
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            try:
                # Check if button is inside a form
                parent_form = driver.execute_script(
                    "return arguments[0].closest('form');", btn
                )
                if parent_form is None:
                    btn_text = btn.text.strip()
                    btn_id = btn.get_attribute("id") or ""
                    btn_onclick = btn.get_attribute("onclick") or ""
                    btn_type = btn.get_attribute("type") or "button"

                    if btn_text or btn_id or btn_onclick:
                        buttons_data.append({
                            "endpoint": page_url,
                            "method": "POST",
                            "parameters": [{
                                "name": btn_id or btn_text or "button",
                                "type": btn_type,
                                "element": "button",
                            }],
                            "source_page": page_url,
                            "has_csrf_token": False,
                        })
            except Exception:
                pass
    except Exception as e:
        logger.debug(f"Error extracting buttons: {e}")
    return buttons_data


def _extract_url_endpoints(links):
    """Create endpoint entries for links with query parameters."""
    endpoints = []
    for link in links:
        params = _extract_query_params(link)
        if params:
            parameters = [
                {"name": k, "type": "query", "element": "url"}
                for k in params
            ]
            endpoints.append({
                "endpoint": link.split("?")[0],
                "method": "GET",
                "parameters": parameters,
                "source_page": link,
                "has_csrf_token": False,
            })
    return endpoints


def crawl_site(url, max_depth=3, max_pages=50):
    """
    Crawl a website and build a complete endpoint map.

    Args:
        url: Target URL to crawl
        max_depth: Maximum crawl depth for link following
        max_pages: Maximum number of pages to visit

    Returns:
        dict with:
            - endpoints: [{endpoint, method, parameters, source_page, has_csrf_token}]
            - links: [list of discovered URLs]
            - cookies: [list of response cookies]
            - total_forms: int
            - total_links: int
            - pages_crawled: int
    """
    if not SELENIUM_AVAILABLE:
        logger.warning("Selenium not available — returning fallback endpoint")
        return {
            "endpoints": [{"endpoint": url, "method": "GET", "parameters": [], "source_page": url, "has_csrf_token": False}],
            "links": [url],
            "cookies": [],
            "total_forms": 0,
            "total_links": 1,
            "pages_crawled": 0,
        }

    driver = None
    all_endpoints = []
    all_links = set()
    visited = set()
    cookies = []

    try:
        driver = _create_driver()

        # BFS crawl
        queue = [(url, 0)]  # (url, depth)
        visited.add(url)

        while queue and len(visited) <= max_pages:
            current_url, depth = queue.pop(0)

            try:
                logger.info(f"Crawling: {current_url} (depth={depth})")
                driver.get(current_url)

                # Wait for SPA content to render
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                # Additional wait for JavaScript frameworks to render
                time.sleep(3)

                # Scroll to trigger lazy-loaded content
                _scroll_page(driver)

                # Extract forms
                forms = _extract_forms(driver, current_url)
                all_endpoints.extend(forms)

                # Extract standalone buttons
                buttons = _extract_buttons(driver, current_url)
                all_endpoints.extend(buttons)

                # Extract links
                page_links = _extract_links(driver, url)
                all_links.update(page_links)

                # Extract link-based endpoints (with query params)
                url_endpoints = _extract_url_endpoints(page_links)
                all_endpoints.extend(url_endpoints)

                # Add pages to crawl queue
                if depth < max_depth:
                    for link in page_links:
                        if link not in visited and len(visited) < max_pages:
                            visited.add(link)
                            queue.append((link, depth + 1))

                # Collect cookies
                try:
                    page_cookies = driver.get_cookies()
                    for cookie in page_cookies:
                        cookie_info = {
                            "name": cookie.get("name", ""),
                            "domain": cookie.get("domain", ""),
                            "path": cookie.get("path", "/"),
                            "secure": cookie.get("secure", False),
                            "httpOnly": cookie.get("httpOnly", False),
                            "sameSite": cookie.get("sameSite", "None"),
                            "expiry": cookie.get("expiry"),
                        }
                        if cookie_info not in cookies:
                            cookies.append(cookie_info)
                except Exception:
                    pass

            except Exception as e:
                logger.warning(f"Error crawling {current_url}: {e}")
                continue

        # If no endpoints found via Selenium, add base URL as a GET endpoint
        if not all_endpoints:
            all_endpoints.append({
                "endpoint": url,
                "method": "GET",
                "parameters": [],
                "source_page": url,
                "has_csrf_token": False,
            })

    except Exception as e:
        logger.error(f"Crawl engine error: {e}")
        # Fallback: return base URL endpoint
        all_endpoints.append({
            "endpoint": url,
            "method": "GET",
            "parameters": [],
            "source_page": url,
            "has_csrf_token": False,
        })

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    # Deduplicate endpoints
    seen = set()
    unique_endpoints = []
    for ep in all_endpoints:
        key = (ep["endpoint"], ep["method"], str(ep["parameters"]))
        if key not in seen:
            seen.add(key)
            unique_endpoints.append(ep)

    return {
        "endpoints": unique_endpoints,
        "links": list(all_links),
        "cookies": cookies,
        "total_forms": sum(1 for e in unique_endpoints if e["method"] == "POST"),
        "total_links": len(all_links),
        "pages_crawled": len(visited),
    }