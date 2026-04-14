<p align="center">
  <img src="https://img.shields.io/badge/WebSec_AI-DAST_Scanner-8B5CF6?style=for-the-badge&logo=shield&logoColor=white" alt="WebSec AI" />
</p>

<h1 align="center">🛡️ WebSec AI — Web Application Security Scanner</h1>

<p align="center">
  <strong>A dual-mode DAST security testing platform with AI-powered analysis.</strong><br/>
  Scan any website for vulnerabilities or run specialized ecommerce security audits — all from a single interface.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react" />
  <img src="https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask" />
  <img src="https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat-square&logo=typescript" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-4.0-06B6D4?style=flat-square&logo=tailwindcss" />
  <img src="https://img.shields.io/badge/Gemini_AI-Powered-4285F4?style=flat-square&logo=google" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Scan Modules](#-scan-modules)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Deployment](#-deployment)
- [Security Disclaimer](#-security-disclaimer)

---

## 🧭 Overview

**WebSec AI** is a production-grade, browser-based DAST (Dynamic Application Security Testing) platform that combines automated vulnerability scanning with AI-driven analysis. It offers two distinct scanning engines:

| Mode | Target | Theme | Checks |
|------|--------|-------|--------|
| **General DAST** | Any web application | 🟣 Purple | SQL Injection, XSS, CSRF, Auth, SSL/TLS, Headers |
| **Ecommerce Scanner** | Online stores | 🟠 Amber | Price Tampering, Cart Security, Coupon Abuse, IDOR, API Exposure, Bot Defense |

Users can register for full features (scan history, deep scans, stress testing) or use guest mode for quick scans — no installation required.

---

## ✨ Features

### 🔍 Scanning Engine
- **6 DAST scanner modules** running concurrently via `ThreadPoolExecutor`
- **8 ecommerce security check categories** aligned with OWASP guidelines
- **3 depth modes** — Quick (2 pages), Standard (5 pages), Deep (15 pages)
- **Concurrent execution** — Scanners run in parallel, not sequentially
- **Load/Stress testing** — Controlled concurrent request testing with stability metrics

### 🤖 AI Analysis
- **Gemini API integration** for intelligent vulnerability summarization
- Auto-generated risk summaries, priority actions, and security grades (A+ to F)
- Context-aware recommendations tailored to each finding

### 🔐 User System
- **JWT authentication** with secure token management
- **Scan history** — All scans saved and viewable for logged-in users
- **Access control** — Guests limited to quick scans, registered users get full access
- **Guest mode** — No signup required for basic scanning

### 🎨 UI/UX
- **Glassmorphism design system** — Premium dark mode with glass-card effects
- **Animated mode switcher** — Smooth Framer Motion transitions between DAST & Ecom modes
- **Real-time scan terminal** — Live mode-specific log output during scans
- **Responsive layout** — Works on desktop, tablet, and mobile

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  React 18 + TypeScript + Vite + Tailwind CSS v4              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │ Landing    │  │ Scan Setup │  │ Results    │              │
│  │ Page       │→ │ (Mode Pick)│→ │ Dashboard  │              │
│  └────────────┘  └────────────┘  └────────────┘              │
│         ↕              ↕              ↕                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │ Login /    │  │ Scan       │  │ History    │              │ 
│  │ Register   │  │ Progress   │  │ Page       │              │
│  └────────────┘  └────────────┘  └────────────┘              │
├──────────────────────────────────────────────────────────────┤
│                     REST API (Flask)                         │
│  POST /api/scan  │  POST /api/login  │  GET /api/history     │
├──────────────────────────────────────────────────────────────┤
│                      BACKEND ENGINE                          │
│  ┌─────────────────────────────────────────────────────┐     │
│  │              AsyncScanEngine                        |     │
│  │         ThreadPoolExecutor (3-8 workers)            |     │
│  │  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐            |     │
│  │  │ SQLi  │ │  XSS  │ │ CSRF  │ │ Auth  │            |     │
│  │  └───────┘ └───────┘ └───────┘ └───────┘            │     │
│  │  ┌───────┐ ┌───────┐ ┌──────────────────┐           │     │
│  │  │  SSL  │ │Headers│ │  EcomScanner (8) │           │     │
│  │  └───────┘ └───────┘ └──────────────────┘           │     │
│  └─────────────────────────────────────────────────────┘     │
│        ↓                                                     │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │  Scorer  │  │ Gemini AI    │  │   SQLite DB  │            │
│  │ (0-100)  │  │  Analysis    │  │  (History)   │            │
│  └──────────┘  └──────────────┘  └──────────────┘            │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | Component-based UI |
| TypeScript | Type safety |
| Vite | Build tool & dev server |
| Tailwind CSS v4 | Utility-first styling with custom design tokens |
| Framer Motion | Animations & page transitions |
| Lucide React | Icon library |
| React Router v6 | Client-side routing |
| Recharts | Vulnerability charts |

### Backend
| Technology | Purpose |
|------------|---------|
| Flask | REST API framework |
| Python `requests` | HTTP scanning & payload delivery |
| `concurrent.futures` | Parallel scanner execution |
| `ssl` / `socket` | TLS handshake & certificate analysis |
| BeautifulSoup | HTML parsing for crawling |
| PyJWT | JSON Web Token authentication |
| Google Generative AI | Gemini-powered scan analysis |
| SQLite | User accounts & scan history storage |

---

## 🔬 Scan Modules

### General DAST Scanners

| Scanner | File | What It Detects |
|---------|------|-----------------|
| **SQL Injection** | `sqli_scanner.py` | Error-based, time-based blind, auth bypass |
| **XSS** | `xss_scanner.py` | Reflected, DOM-based, context-aware detection |
| **CSRF** | `csrf_scanner.py` | Missing tokens, insecure SameSite cookies |
| **Auth & Session** | `auth_scanner.py` | Cookie flags, session fixation, JWT leakage |
| **SSL/TLS** | `ssl_scanner.py` | Weak TLS, expired certs, missing HSTS, HTTPS downgrade |
| **Security Headers** | `headers_scanner.py` | CSP, X-Frame-Options, Referrer-Policy, Permissions-Policy |
| **Stress Test** | `stress_scanner.py` | Concurrent load test with stability metrics |

### Ecommerce Security Checks

| Category | What It Checks |
|----------|----------------|
| **Auth & Account** | Weak passwords, brute-force, account lockout, MFA |
| **Access Control** | IDOR, admin panel exposure, role-based access |
| **Session & Cookies** | HttpOnly, Secure, SameSite, session rotation |
| **Ecom Logic** | Price manipulation, cart tampering, coupon abuse, predictable order IDs |
| **Data Exposure** | `.env` files, `.git` folders, API keys, backup files |
| **Misconfiguration** | Directory listing, debug mode, default credentials |
| **API Security** | Unauthenticated endpoints, verbose errors, rate limiting |
| **Bot Protection** | CAPTCHA presence, rate limiting, automation defenses |

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.10+
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/kunal-csq/web_security_scanner.git
cd web_security_scanner
```

### 2. Frontend Setup
```bash
npm install
npm run dev
```
Frontend runs at `http://localhost:5173`

### 3. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Environment Variables

Create `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
JWT_SECRET=your_jwt_secret_here
```

### 5. Run the Backend
```bash
cd backend
python app.py
```
Backend runs at `http://localhost:5000`

### 6. Update API Base URL

In `src/config/api.ts`, set the backend URL:
```typescript
const BASE = "http://localhost:5000/api";
```

---

## 📡 API Reference

### Scan
```http
POST /api/scan
Content-Type: application/json
Authorization: Bearer <token>  (optional)

{
  "url": "https://example.com",
  "scans": ["sqli", "xss", "csrf", "auth", "ssl", "headers"],
  "depth": "standard",
  "stress_test": false,
  "scan_mode": "general"
}
```

**Response:**
```json
{
  "url": "https://example.com",
  "score": 65,
  "grade": "C",
  "severity_counts": { "critical": 1, "high": 2, "medium": 3, "low": 2 },
  "results": [ { "name": "SQL Injection", "severity": "Critical", ... } ],
  "ai_analysis": { "summary": "...", "priority_actions": [...] },
  "scan_log": [...],
  "timing": { "total_time": 12.5 }
}
```

### Auth
```http
POST /api/auth/register    { "name", "email", "password" }
POST /api/auth/login       { "email", "password" }
```

### History
```http
GET    /api/history         (requires auth)
DELETE /api/history/:id     (requires auth)
```

### Health
```http
GET /api/health
GET /api/scanners
```

---

## 📂 Project Structure

```
web_security_scanner/
├── src/                          # Frontend (React + TypeScript)
│   ├── app/
│   │   ├── components/           # Reusable UI components
│   │   │   ├── Navbar.tsx
│   │   │   ├── HeroSection.tsx
│   │   │   ├── FeatureSection.tsx
│   │   │   ├── HowItWorks.tsx
│   │   │   ├── CTASection.tsx
│   │   │   └── Footer.tsx
│   │   ├── pages/                # Route-level pages
│   │   │   ├── LandingPage.tsx
│   │   │   ├── ScanSetup.tsx     # Mode switcher + URL input
│   │   │   ├── ScanProgress.tsx  # Real-time scan terminal
│   │   │   ├── ScanResults.tsx   # Results dashboard
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   └── HistoryPage.tsx
│   │   └── routes.tsx
│   ├── config/
│   │   ├── api.ts                # Backend URL config
│   │   └── auth.ts               # JWT token helpers
│   └── styles/
│       ├── tailwind.css          # Tailwind v4 design tokens
│       └── theme.css             # Glassmorphism design system
│
├── backend/                      # Backend (Python Flask)
│   ├── app.py                    # Flask app entry point
│   ├── db.py                     # SQLite database setup
│   ├── api/
│   │   ├── scan_routes.py        # /api/scan endpoint
│   │   ├── auth_routes.py        # /api/auth/* endpoints
│   │   └── history_routes.py     # /api/history endpoints
│   ├── core/
│   │   ├── async_engine.py       # Concurrent scan engine
│   │   └── scorer.py             # Score calculator (0-100, A+ to F)
│   ├── scanners/
│   │   ├── sqli_scanner.py       # SQL Injection scanner
│   │   ├── xss_scanner.py        # XSS scanner
│   │   ├── csrf_scanner.py       # CSRF scanner
│   │   ├── auth_scanner.py       # Auth & session scanner
│   │   ├── ssl_scanner.py        # SSL/TLS scanner
│   │   ├── headers_scanner.py    # HTTP headers scanner
│   │   ├── stress_scanner.py     # Load tester
│   │   ├── ecom_scanner.py       # Ecommerce security scanner
│   │   └── selenium_crawler.py   # Website crawler
│   └── ai/
│       └── analysis.py           # Gemini AI analysis
│
├── netlify.toml                  # Netlify deployment config
├── vite.config.ts                # Vite build config
├── tailwind.config.ts            # Tailwind configuration
└── package.json
```

---


## ⚠️ Security Disclaimer

> **This tool is designed for authorized security testing only.**
>
> - Only scan websites you own or have explicit permission to test
> - The scanner sends payloads (SQL, XSS) to test for vulnerabilities — this is intrusive by nature
> - Unauthorized scanning of third-party websites may violate laws in your jurisdiction
> - The ecommerce scanner uses non-destructive heuristic probes — it does NOT attempt actual purchases or payment manipulation
> - The developers assume no liability for misuse of this tool

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Built by <a href="https://github.com/kunal-csq"><strong>Kunal Bhardwaj</strong></a>
</p>
