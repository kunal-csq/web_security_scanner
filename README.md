# WebGuard — Web Security Testing Platform

<div align="center">

![License](https://img.shields.io/badge/license-MIT-8B5CF6?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![React](https://img.shields.io/badge/react-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![Flask](https://img.shields.io/badge/flask-3.x-000000?style=flat-square&logo=flask)
![Gemini](https://img.shields.io/badge/AI-Gemini_2.0-F59E0B?style=flat-square)

**Enterprise-grade DAST + Ecommerce security scanner with AI-powered analysis.**

[Live Demo](https://webguardd.netlify.app) · [Report Bug](https://github.com/kunal-csq/web_security_scanner/issues)

</div>

---

## Overview

WebGuard is a dual-mode web security testing platform that combines Dynamic Application Security Testing (DAST) with specialized ecommerce vulnerability scanning. It features an async scan engine, AI-powered risk analysis via Google Gemini, and a built-in security chatbot for remediation guidance.

## Features

### General DAST Scanner
- **SQL Injection** — Error-based, time-based blind, auth bypass
- **Cross-Site Scripting (XSS)** — Reflected, DOM-based, context-aware payloads
- **CSRF Detection** — Missing tokens, SameSite cookies, origin validation
- **Security Headers** — CSP, HSTS, X-Frame-Options, Permissions-Policy
- **SSL/TLS Analysis** — Protocol versions, cipher strength, certificate health
- **Authentication Flaws** — Cookie flags, session rotation, JWT leakage
- **Load Testing** — Concurrent requests with stability metrics

### Ecommerce Scanner
- **Price Manipulation** — Client-side price/amount field detection
- **Cart Tampering** — Hidden quantity/total fields in forms
- **Coupon Abuse** — Unlimited coupon application vectors
- **Predictable Order IDs** — Sequential ID enumeration
- **Admin Panel Exposure** — Common admin path probing
- **IDOR Checks** — Insecure direct object reference patterns
- **API Security** — Unauthenticated endpoints, missing rate limiting, GraphQL introspection
- **Bot Protection** — CAPTCHA, anti-automation, security header coverage

### Platform Features
- **AI Chat Assistant** — Gemini-powered security expert for remediation help
- **User Authentication** — JWT-based auth with registration and login
- **Scan History** — Persistent scan results for authenticated users
- **Tiered Access** — Guest (quick scan only) vs authenticated (full access)
- **AI Analysis** — Automated severity scoring, risk summaries, and fix priorities

## Architecture

```
├── src/                    # React frontend (Vite + TypeScript)
│   ├── app/
│   │   ├── components/     # UI components (Navbar, ChatWidget, etc.)
│   │   └── pages/          # Route pages (LandingPage, ScanSetup, etc.)
│   ├── config/             # API config, auth utilities
│   └── styles/             # Theme, Tailwind config
│
├── backend/                # Flask API server
│   ├── api/                # Route handlers (scan, auth, history, chat)
│   ├── core/               # Scan engine, async orchestrator, scorer
│   ├── scanners/           # Scanner modules (sqli, xss, csrf, ecom, etc.)
│   ├── ai/                 # AI analysis module
│   └── db.py               # SQLite database (users, scan history)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Tailwind CSS, Framer Motion |
| Backend | Python 3.10+, Flask, Gunicorn |
| Database | SQLite (WAL mode) |
| AI | Google Gemini 2.0 Flash |
| Auth | JWT (PyJWT), bcrypt via Werkzeug |
| Hosting | Netlify (frontend), Render (backend) |

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

### Frontend

```bash
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
python app.py
```

### Environment Variables

Create `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET=your_jwt_secret_key
```

Frontend `.env.production`:
```env
VITE_API_URL=https://your-backend.onrender.com
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/scan` | Run security scan (general or ecommerce mode) |
| `POST` | `/api/chat` | AI security chat assistant |
| `POST` | `/api/auth/register` | Create user account |
| `POST` | `/api/auth/login` | Login and get JWT |
| `GET` | `/api/auth/me` | Get current user profile |
| `GET` | `/api/history` | Get scan history (auth required) |
| `GET` | `/api/history/:id` | Get specific scan result |
| `GET` | `/api/health` | Health check |

## Scan Request Example

```json
POST /api/scan
{
  "url": "https://example.com",
  "scans": ["sqli", "xss", "csrf", "headers", "ssl", "auth"],
  "depth": "standard",
  "scan_mode": "general",
  "stress_test": false
}
```

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -m 'Add your feature'`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for details.

---

<div align="center">
Built by <a href="https://github.com/kunal-csq">Kunal Bhardwaj</a>
</div>
