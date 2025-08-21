# 🔍 Domain OSINT

A lightweight OSINT (Open Source Intelligence) tool for analyzing domains. Built with Flask and a modern, responsive UI.

## ✨ Features

- **Domain Analysis**: MX record lookup and provider hints
- **Technology Stack**: BuiltWith integration with vendor/category grouping and variants
- **Modern UI**: Centered, clean form; responsive; loading states; details toggles
- **JSON API**: Simple GET endpoint for automation
- **Tests**: Unit and integration tests (MX + BuiltWith)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- BuiltWith API key (optional, required only for tech stack results)

### Installation

1. Clone and enter the project
```bash
git clone https://github.com/ecgun3/email-osint-tool.git
cd email-osint-tool
```

2. Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set environment variables
```bash
# Optional: only needed if you want BuiltWith tech stack results
export BUILTWITH_API_KEY=your_builtwith_api_key
```

5. Run the app
```bash
export FLASK_APP=app:app
export FLASK_DEBUG=1
flask run --host 127.0.0.1 --port 5000
```

Health checks:
- `GET /healthz` → `{ "status": "ok" }`
- `GET /health` → `{ "ok": true }`

## 🌐 API Usage

### Endpoint
```bash
GET /analyze?domain=example.com&format=json
```

### Response (example)
```json
{
  "ok": true,
  "timestamp": "2025-08-20T14:30:00Z",
  "results": {
    "resolved_domain": "example.com",
    "mx": {
      "provider": "Google Workspace",
      "mx_records": [
        { "exchange": "mx1.example.com", "preference": 10 }
      ],
      "warnings": []
    },
    "builtwith": {
      "elapsedMs": 477,
      "grouped": [
        {
          "name": "WordPress",
          "count": 5,
          "categories": ["CMS"],
          "variants": [
            { "name": "WordPress 6.0", "count": 3, "examples": ["https://example.com"] }
          ]
        }
      ]
    }
  }
}
```

## 🎨 UI/UX

- Centered, single-field domain form
- Responsive cards for MX and BuiltWith results
- Grouped technology list with small “Details” toggles for variants/examples
- Toast-style alerts for empty or invalid input

## 🧪 Testing

Run all tests:
```bash
pytest
```

Coverage:
```bash
pytest --cov=core --cov=app --cov=utils --cov-report=term-missing
```

Test layout:
- `tests/test_app.py` – Flask routes and validation
- `tests/test_simulation.py` – Core simulation (MX + BuiltWith)
- `tests/test_integrations_live.py` – Live tests (MX + BuiltWith, opt-in via env)

## 🔧 Code Quality

- Type hints, structured logging
- Black / Flake8 / MyPy configured via `requirements.txt`

Useful commands:
```bash
black .
flake8 .
mypy .
```

## 📊 BuiltWith Integration

- Groups technologies by vendor/framework
- Aggregates variants (versions/editions) and example URLs
- Returns `grouped` data for UI and a flat fallback where available

## 🚀 Deploy (Render)

- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --worker-class gthread --threads 8 --timeout 120`
- Health Check Path: `/healthz`
- Environment:
```bash
BUILTWITH_API_KEY=your_api_key_here  # required for tech stack
FLASK_APP=app:app
FLASK_DEBUG=false
```

## 📁 Project Structure

```
email-osint-tool/
├── app.py                 # Flask application (routes: /, /healthz, /health, /analyze)
├── config.py              # Configuration (env vars)
├── requirements.txt       # Dependencies
├── pytest.ini             # Pytest config
├── core/
│   ├── orchestrator.py    # Main workflow (MX + BuiltWith)
│   ├── builtwith_client.py# BuiltWith API integration + grouping
│   ├── mx_analyzer.py     # MX record analysis
│   └── email_patterns.py  # Legacy helper (not used in UI)
├── templates/
│   ├── base.html          # Base layout & styles
│   ├── index.html         # Centered domain form
│   └── result.html        # MX & BuiltWith results
├── tests/                 # Test suite
│   ├── test_app.py
│   ├── test_simulation.py
│   └── test_integrations_live.py
└── utils/
    ├── validators.py      # Input validation (domain)
    └── helpers.py         # Helpers (timestamps, domain extraction)
```

## 🙌 Notes

- Email input, Holehe account enumeration, and SMTP probing were removed to keep the app fast and simple.
- BuiltWith API key is optional; without it, only MX results are shown.

## 📞 Support

- Open an issue on GitHub if you need help or have feature requests.

---

**Built with ❤️ for security research**