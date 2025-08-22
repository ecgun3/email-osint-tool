"""
Email OSINT Scanner - Main Flask Application

This module provides a web interface for OSINT analysis including:
- Domain MX record analysis
- Technology stack detection via BuiltWith
"""

import logging
import json
from typing import Any, Dict, Union
from flask import Flask, render_template, request, jsonify

from config import get_config
from core.orchestrator import analyze_workflow
from utils.validators import is_valid_domain
from utils.helpers import now_utc_iso

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize configuration
config = get_config()

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = config.secret_key
app.config["TEMPLATES_AUTO_RELOAD"] = config.templates_auto_reload


@app.route("/healthz")
def healthz() -> tuple[Dict[str, str], int]:
    """Health check endpoint for monitoring."""
    response = {"status": "ok"}, 200
    return response


@app.route("/health")
def health() -> tuple[Dict[str, str], int]:
    """Health check endpoint for Render compatibility."""
    response = {"status": "ok"}, 200
    return response


@app.route("/", methods=["GET"])
def index() -> str:
    """Main page with analysis form."""
    response = app.make_response(render_template("index.html"))
    response.headers['Cache-Control'] = 'public, max-age=300'  # 5 minutes cache
    return response


@app.route("/analyze", methods=["POST", "GET"])
def analyze() -> Union[str, tuple[Dict[str, Any], int]]:
    """
    Analyze endpoint for both form submissions and API calls.

    Input: domain (required)
    Output: HTML or JSON
    """
    try:
        # Parse input based on request method
        if request.method == "GET":
            domain = request.args.get("domain", "").strip()
            want_json = request.args.get("format", "").lower() == "json"
        else:
            domain = request.form.get("domain", "").strip()
            want_json = request.headers.get("Accept", "").lower().find("application/json") != -1

        # Validate input (domain-only)
        if not domain:
            return _handle_validation_error("Please provide a domain to analyze.", want_json)
        if not is_valid_domain(domain):
            return _handle_validation_error("Invalid domain format.", want_json)

        # Perform analysis (email and names removed)
        logger.info(f"Starting analysis for domain: {domain}")
        results = analyze_workflow(
            domain=domain,
            email=None,
            first_name=None,
            last_name=None,
            request_timeout=config.request_timeout_seconds,
            builtwith_api_key=config.builtwith_api_key,
        )

        logger.info(f"Analysis completed successfully for domain: {domain}")

        # Return appropriate response format
        if want_json:
            payload = {
                "ok": True,
                "timestamp": now_utc_iso(),
                "results": results,
            }
            return app.response_class(
                json.dumps(payload, indent=2, ensure_ascii=False),
                mimetype="application/json",
            )

        return render_template("result.html", results=results, timestamp=now_utc_iso())

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        error_message = "An unexpected error occurred during analysis."

        if want_json:
            return jsonify({"ok": False, "error": error_message}), 500

        return render_template("index.html", error=error_message), 500


def _handle_validation_error(message: str, want_json: bool) -> Union[str, tuple[Dict[str, Any], int]]:
    """
    Handle validation errors consistently.
    """
    if want_json:
        return jsonify({"ok": False, "error": message}), 400

    return render_template("index.html", error=message), 400


@app.errorhandler(404)
def not_found(error: Any) -> tuple[str, int]:
    """Handle 404 errors."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error: Any) -> tuple[str, int]:
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return render_template("500.html"), 500


if __name__ == "__main__":
    logger.info(f"Starting Email OSINT Scanner on {config.host}:{config.port}")
    app.run(
        host=config.host,
        port=config.port,
        debug=config.debug
    )
