<img width="1419" height="753" alt="Linkedn foto" src="https://github.com/user-attachments/assets/ddd69c8e-bda7-4f90-af2c-6ec82106032b" />


# 🔍 Domain OSINT

A lightweight OSINT (Open Source Intelligence) tool for analyzing domains. Built with **Flask** and a modern, responsive UI.

## 🌐 Live Demo

**Try it now:** [https://emailosint.onrender.com](https://emailosint.onrender.com)

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

### Unit Tests (Pytest)

Run all unit tests:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/test_app.py -v
pytest tests/test_simulation.py -v
```

Run with coverage:
```bash
pytest --cov=core --cov=app --cov=utils --cov-report=term-missing
```

Generate HTML coverage report:
```bash
pytest --cov=core --cov=app --cov=utils --cov-report=html
# Open htmlcov/index.html in browser
```

### Cypress End-to-End Tests

**Prerequisites:**
- Node.js 16+ and npm 8+
- Flask app running on localhost:5000

**Install Cypress:**
```bash
npm install
```

**Run Cypress tests:**
```bash
# Run all Cypress tests in headless mode
npm run test:cypress

# Open Cypress Test Runner (interactive)
npm run test:cypress:open

# Run tests with browser visible
npm run test:cypress:headed
```

**Run all tests (Unit + Cypress):**
```bash
npm run test:all
```

### Test Structure

**Unit Tests:**
- `tests/test_app.py` – Flask routes, validation, error handling
- `tests/test_simulation.py` – Core workflow (MX + BuiltWith)
- `tests/test_integrations_live.py` – Live integration tests (optional)

**Cypress Tests:**
- `cypress/e2e/domain-osint.cy.js` – End-to-end UI testing
- `cypress/fixtures/analysis-result.json` – Test data
- `cypress/support/commands.js` – Custom Cypress commands

### Test Categories

**Unit Tests Cover:**
- ✅ Route handling (`/`, `/healthz`, `/health`, `/analyze`)
- ✅ Input validation (domain format, empty input)
- ✅ Response formats (HTML, JSON)
- ✅ Error handling (400, 404, 500, exceptions)
- ✅ Core workflow (MX analysis, BuiltWith integration)
- ✅ Edge cases (timeouts, large results, empty data)

**Cypress Tests Cover:**
- ✅ UI functionality (forms, buttons, navigation)
- ✅ User interactions (domain input, search, details toggle)
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ BuiltWith search and filtering
- ✅ Error scenarios and edge cases
- ✅ Performance metrics

### Running Tests in CI/CD

**GitHub Actions Example:**
```yaml
- name: Run Unit Tests
  run: |
    pip install -r requirements.txt
    pytest --cov=core --cov=app --cov=utils --cov-report=xml

- name: Run Cypress Tests
  run: |
    npm install
    npm run test:cypress
```

**Local Development:**
```bash
# Start Flask app in background
export FLASK_APP=app:app
export FLASK_DEBUG=1
flask run --host 127.0.0.1 --port 5000 &

# Run tests
npm run test:all

# Stop Flask app
pkill -f "flask run"
```

### Test Data and Fixtures

**Mock Data:**
- Unit tests use `unittest.mock` for external dependencies
- Cypress tests use fixture files for consistent test data
- BuiltWith API calls are mocked to avoid rate limits

**Live Testing:**
- Set environment variables for live integration tests
- Use `tests/test_integrations_live.py` for real API testing
- Requires valid BuiltWith API key

### Test Commands (package.json)

**Available Scripts:**
```bash
npm run test              # Run pytest
npm run test:unit         # Run unit tests with verbose output
npm run test:coverage     # Run tests with coverage report
npm run test:cypress      # Run Cypress tests headless
npm run test:cypress:open # Open Cypress Test Runner
npm run test:cypress:headed # Run Cypress with browser visible
npm run test:all          # Run both unit and Cypress tests
npm run lint              # Run flake8 linting
npm run format            # Run black code formatting
npm run type-check        # Run mypy type checking
npm run quality           # Run all quality checks
```

### Test Coverage Details

**Unit Test Coverage:**
- **Flask App**: Routes, validation, error handlers, response formats
- **Core Logic**: MX analysis, BuiltWith integration, workflow orchestration
- **Utils**: Helper functions, validators, timestamp handling
- **Edge Cases**: Invalid input, network errors, timeout handling

**Cypress Test Coverage:**
- **Homepage**: Main elements, form positioning, feature cards
- **Domain Analysis**: Input validation, form submission, loading states
- **Results Page**: MX display, BuiltWith search, Details toggle
- **Navigation**: Back button, View JSON, Print functionality
- **Responsive Design**: Mobile, tablet, desktop viewports
- **Error Handling**: Network errors, 404 pages, validation errors
- **Performance**: Page load times, interaction responsiveness

### Test Environment Setup

**For Unit Tests:**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run tests
pytest
```

**For Cypress Tests:**
```bash
# Install Node.js dependencies
npm install

# Start Flask app (required for Cypress)
export FLASK_APP=app:app
export FLASK_DEBUG=1
flask run --host 127.0.0.1 --port 5000

# In another terminal, run Cypress
npm run test:cypress:open
```

**Environment Variables for Testing:**
```bash
# Optional: for live integration tests
export BUILTWITH_API_KEY=your_test_key
export LIVE_MX=true
export LIVE_BUILTWITH=true
```

### Continuous Integration

**GitHub Actions Workflow:**
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install Python dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest --cov=core --cov=app --cov=utils --cov-report=xml
      - name: Install Node.js dependencies
        run: npm install
      - name: Start Flask app
        run: |
          export FLASK_APP=app:app
          flask run --host 127.0.0.1 --port 5000 &
          sleep 10
      - name: Run Cypress tests
        run: npm run test:cypress
```

### Test Best Practices

**Unit Testing:**
- Use `@patch` decorator for external dependencies
- Test both success and failure scenarios
- Mock BuiltWith API calls to avoid rate limits
- Test edge cases and boundary conditions

**Cypress Testing:**
- Use custom commands for common operations
- Test responsive design across viewports
- Verify user interactions and state changes
- Check accessibility and usability features

**Test Data Management:**
- Use fixtures for consistent test data
- Mock external API responses
- Test with realistic domain examples
- Validate both HTML and JSON outputs

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

This application is built with **Flask** and deployed on **Render** as a web service.

- **Framework**: Flask (Python web framework)
- **Platform**: Render (Cloud hosting)
- **Build**: `pip install -r requirements.txt`
- **Start**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --worker-class gthread --threads 8 --timeout 120`
- **Health Check Path**: `/health` (Render compatibility)
- **Environment**:
```bash
BUILTWITH_API_KEY=your_api_key_here  # required for tech stack
FLASK_APP=app:app
FLASK_DEBUG=false
```

**Live Website**: [https://emailosint.onrender.com](https://emailosint.onrender.com)

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
