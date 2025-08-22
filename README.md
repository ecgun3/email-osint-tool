# 🔍 Domain OSINT

A lightweight OSINT (Open Source Intelligence) tool for analyzing domains. Built with Flask and a modern, responsive UI.

## ✨ Features

- **Domain Analysis**: MX record lookup and provider hints
- **Technology Stack**: BuiltWith integration with vendor/category grouping, variants, and live search filtering
- **Smart Details**: Shows Details toggle only for groups with multiple variants (count > 1)
- **Live Search**: Built-in search box to filter technologies by name or category
- **Modern UI**: Centered, clean form; responsive; loading states; expandable details
- **JSON API**: Simple GET endpoint for automation with pretty-printed output
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
- `GET /health` → `{ "status": "ok" }` (Render compatibility)

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

- **Centered Domain Form**: Single input field for clean, focused experience
- **Live Search**: Built-in search box in Technology Stack section to filter results
- **Smart Details**: 
  - Groups with count > 1 show count badge and Details toggle
  - Single-item groups (count = 1) hide Details toggle for cleaner display
- **Responsive Cards**: MX and BuiltWith results in organized, expandable cards
- **Category Badges**: Technology categories displayed as colored badges
- **Variant Examples**: Expandable details show example URLs for technology variants

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

- **Smart Grouping**: Groups technologies by vendor/framework
- **Variant Aggregation**: Combines versions/editions with counts
- **Live Search**: Filter technologies by name or category in real-time
- **Example URLs**: Shows sample URLs for each technology variant
- **Count Logic**: Only shows Details toggle for groups with multiple variants

## 🚀 Deploy (Render)

- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --worker-class gthread --threads 8 --timeout 120`
- Health Check Path: `/health` (Render compatibility)
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
│   └── result.html        # MX & BuiltWith results with search
├── tests/                 # Test suite
│   ├── test_app.py
│   ├── test_simulation.py
│   └── test_integrations_live.py
└── utils/
    ├── validators.py      # Input validation (domain)
    └── helpers.py         # Helpers (timestamps, domain extraction)
```

## 🔍 BuiltWith Search Features

- **Live Filtering**: Search box filters technologies in real-time
- **Multi-field Search**: Searches both technology names and categories
- **Clear Function**: Easy reset of search filters
- **Empty State**: Shows helpful message when no results match search
- **Responsive Design**: Search box adapts to different screen sizes

## 🙌 Notes

- Email input, Holehe account enumeration, and SMTP probing were removed to keep the app fast and simple
- BuiltWith API key is optional; without it, only MX results are shown
- Technology groups with single variants automatically hide Details toggle for cleaner UI
- Search functionality works client-side for instant results

## 🚧 Future Improvements

### High Priority
- **Enhanced Unit Tests**: Expand test coverage for edge cases and error scenarios
- **User API Key Management**: Allow users to input their own BuiltWith API keys to avoid consuming the main API quota
- **Email Validation Integration**: Re-add Holehe email testing capabilities with user-provided API keys

### Medium Priority  
- **Rate Limiting**: Implement per-user rate limiting to prevent abuse
- **Caching**: Add Redis/Memory caching for repeated domain lookups
- **Export Options**: CSV/Excel export for analysis results
- **Batch Processing**: Analyze multiple domains at once

### Low Priority
- **User Authentication**: Optional user accounts to save analysis history
- **API Documentation**: Interactive API docs with Swagger/OpenAPI
- **Mobile App**: React Native or Flutter mobile application
- **Advanced Analytics**: Technology trend analysis and reporting

### Development Status
- **Current Branch**: `development` - Active development with latest features
- **Main Branch**: `main` - Stable release (not yet merged)
- **Next Steps**: Complete testing, add user API key management, then merge to main

## 📞 Support

- Open an issue on GitHub if you need help or have feature requests.

---

**Built with ❤️ for security research**