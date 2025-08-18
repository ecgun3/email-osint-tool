from flask import Flask, render_template, request, redirect, url_for, jsonify
from typing import Any, Dict

from config import get_config
from core.orchestrator import analyze_workflow
from utils.validators import is_valid_email, is_valid_domain
from utils.helpers import extract_domain, now_utc_iso


config = get_config()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = config.secret_key
app.config["TEMPLATES_AUTO_RELOAD"] = config.templates_auto_reload


@app.route("/healthz")
def healthz():
	return {"status": "ok"}, 200


@app.route("/", methods=["GET"])
def index():
	return render_template("index.html")


@app.route("/analyze", methods=["POST", "GET"])
def analyze():
	if request.method == "GET":
		# Allow simple query usage: /analyze?domain=...&email=...&first_name=...&last_name=...&format=json
		domain = request.args.get("domain", "").strip()
		email = request.args.get("email", "").strip()
		first_name = request.args.get("first_name", "").strip()
		last_name = request.args.get("last_name", "").strip()
		want_json = request.args.get("format", "").lower() == "json"
	else:
		domain = request.form.get("domain", "").strip()
		email = request.form.get("email", "").strip()
		first_name = request.form.get("first_name", "").strip()
		last_name = request.form.get("last_name", "").strip()
		want_json = request.headers.get("Accept", "").lower().find("application/json") != -1

	if not domain and not email:
		message = "Please provide a domain or email to analyze."
		if want_json:
			return jsonify({"ok": False, "error": message}), 400
		return render_template("index.html", error=message), 400

	if email and not is_valid_email(email):
		message = "Invalid email address format."
		if want_json:
			return jsonify({"ok": False, "error": message}), 400
		return render_template("index.html", error=message), 400

	if domain and not is_valid_domain(domain):
		# If a user provided something that looks like an email in domain field, try to extract
		extracted = extract_domain(domain)
		if extracted and is_valid_domain(extracted):
			domain = extracted
		else:
			message = "Invalid domain format."
			if want_json:
				return jsonify({"ok": False, "error": message}), 400
			return render_template("index.html", error=message), 400

	# Ensure we always have a domain if email is present
	if email and not domain:
		domain = extract_domain(email)

	results = analyze_workflow(
		domain=domain or None,
		email=email or None,
		first_name=first_name or None,
		last_name=last_name or None,
		request_timeout=config.request_timeout_seconds,
		builtwith_api_key=config.builtwith_api_key,
	)

	if want_json:
		return jsonify({"ok": True, "timestamp": now_utc_iso(), "results": results})

	return render_template("result.html", results=results, timestamp=now_utc_iso())


if __name__ == "__main__":
	app.run(host=config.host, port=config.port, debug=config.debug)
