"""
Email OSINT Scanner - Main Flask Application

This module provides a web interface for OSINT analysis including:
- Domain MX record analysis
- Technology stack detection via BuiltWith
- Email account enumeration via Holehe
- SMTP mailbox probing
"""

import logging
from typing import Any, Dict, Optional, Union
from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import BadRequest

from config import get_config
from core.orchestrator import analyze_workflow
from utils.validators import is_valid_email, is_valid_domain
from utils.helpers import extract_domain, now_utc_iso

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
    return {"status": "ok"}, 200

@app.route("/health")
def health():
    return {"ok": True}



@app.route("/", methods=["GET"])
def index() -> str:
    """Main page with analysis form."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST", "GET"])
def analyze() -> Union[str, tuple[Dict[str, Any], int]]:
    """
    Analyze endpoint for both form submissions and API calls.
    
    Supports:
    - POST form data
    - GET query parameters
    - JSON API responses
    """
    try:
        # Parse input based on request method
        if request.method == "GET":
            domain = request.args.get("domain", "").strip()
            email = request.args.get("email", "").strip()
            want_json = request.args.get("format", "").lower() == "json"
        else:
            domain = request.form.get("domain", "").strip()
            email = request.form.get("email", "").strip()
            want_json = request.headers.get("Accept", "").lower().find("application/json") != -1

        # Validate input
        validation_result = _validate_input(domain, email)
        if not validation_result["valid"]:
            return _handle_validation_error(validation_result["message"], want_json)

        # Extract domain from email if needed
        if email and not domain:
            domain = extract_domain(email)

        # Perform analysis
        logger.info(f"Starting analysis for domain: {domain}, email: {email}")
        results = analyze_workflow(
            domain=domain or None,
            email=email or None,
            first_name=None,  # Removed from UI
            last_name=None,   # Removed from UI
            request_timeout=config.request_timeout_seconds,
            builtwith_api_key=config.builtwith_api_key,
        )

        logger.info(f"Analysis completed successfully for domain: {domain}")

        # Return appropriate response format
        if want_json:
            return jsonify({
                "ok": True,
                "timestamp": now_utc_iso(),
                "results": results
            })

        return render_template("result.html", results=results, timestamp=now_utc_iso())

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        error_message = "An unexpected error occurred during analysis."
        
        if want_json:
            return jsonify({"ok": False, "error": error_message}), 500
        
        return render_template("index.html", error=error_message), 500


def _validate_input(domain: str, email: str) -> Dict[str, Any]:
    """
    Validate input parameters.
    
    Args:
        domain: Domain string to validate
        email: Email string to validate
        
    Returns:
        Dict with validation result and message
    """
    if not domain and not email:
        return {
            "valid": False,
            "message": "Please provide a domain or email to analyze."
        }

    if email and not is_valid_email(email):
        return {
            "valid": False,
            "message": "Invalid email address format."
        }

    if domain and not is_valid_domain(domain):
        # Try to extract domain if user provided email-like input
        extracted = extract_domain(domain)
        if extracted and is_valid_domain(extracted):
            return {"valid": True, "domain": extracted}
        else:
            return {
                "valid": False,
                "message": "Invalid domain format."
            }

    return {"valid": True, "domain": domain}


def _handle_validation_error(message: str, want_json: bool) -> Union[str, tuple[Dict[str, Any], int]]:
    """
    Handle validation errors consistently.
    
    Args:
        message: Error message to display
        want_json: Whether to return JSON response
        
    Returns:
        Appropriate error response
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
