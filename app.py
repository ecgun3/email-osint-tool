from flask import Flask, render_template, request
from core.mx_analyzer import resolve_mx

app = Flask(__name__)


@app.get("/")
def index():
	return render_template("index.html")


@app.post("/mx")
def mx_lookup():
	domain = request.form.get("domain", "").strip()
	if not domain:
		return render_template("result.html", result={
			"status": "error",
			"error": "Domain is required"
		})
	result = resolve_mx(domain)
	return render_template("result.html", result=result, domain=domain)


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8000, debug=True)
