# Email OSINT Tool

A simple Flask-based Email OSINT tool that performs MX analysis, optional BuiltWith technology lookup, integrates with Holehe for email usage checks, and generates email address patterns.

## Features
- MX analysis using dnspython
- BuiltWith API integration (optional, set `BUILTWITH_API_KEY` in `.env`)
- Holehe integration via subprocess (`holehe` CLI must be installed)
- Email pattern generation from first/last names
- HTML UI with Bootstrap and JSON API output

## Setup
1. Create and activate a virtual environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file (optional):

```bash
cp .env.example .env  # create and edit
```

Available env vars:
- `FLASK_SECRET_KEY` (default: change-this-in-production)
- `BUILTWITH_API_KEY` (optional)
- `REQUEST_TIMEOUT_SECONDS` (default: 15)
- `DEBUG` (default: false)
- `HOST` (default: 0.0.0.0)
- `PORT` (default: 5000)

## Run
```bash
python app.py
```

Open `http://localhost:5000`.

## JSON API
Use GET to query and receive JSON:

```
/analyze?domain=example.com&format=json
/analyze?email=user@example.com&first_name=John&last_name=Doe&format=json
```

## Notes
- Holehe results require the `holehe` CLI in PATH. If not installed, the app will return an informative error in the Holehe section.
- BuiltWith API usage requires a valid API key. Without it, the BuiltWith section is omitted.
