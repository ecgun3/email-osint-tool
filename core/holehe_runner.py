from typing import Any, Dict, List
import json
import shlex
import subprocess
import os
import shutil
import re


def _try_parse_json(text: str) -> Any:
	text = text.strip()
	if not text:
		return None
	# Try full JSON first
	try:
		return json.loads(text)
	except Exception:
		pass
	# Try line-delimited JSON
	items: List[Any] = []
	for line in text.splitlines():
		line = line.strip()
		if not line:
			continue
		try:
			items.append(json.loads(line))
		except Exception:
			continue
	return items if items else None


def _resolve_holehe_bin() -> str:
	# Prefer explicit env var
	env_bin = os.getenv("HOLEHE_BIN")
	if env_bin and os.path.isfile(env_bin) and os.access(env_bin, os.X_OK):
		return env_bin
	# Try PATH
	path_bin = shutil.which("holehe")
	if path_bin:
		return path_bin
	# Try common venv path
	venv = os.getenv("VIRTUAL_ENV")
	if venv:
		candidate = os.path.join(venv, "bin", "holehe")
		if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
			return candidate
	return ""


_ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


def _strip_ansi(text: str) -> str:
	if not isinstance(text, str):
		return text
	return _ANSI_ESCAPE_RE.sub("", text)


# Best-effort list of services where email enumeration typically requires login or
# employs strong anti-enumeration patterns. This is used only to annotate UI.
LOGIN_BEHIND_DOMAINS = {
	"docker.com",
	"lastpass.com",
	"office365.com",
	"slack.com",
	"trello.com",
	"hubspot.com",
	"mail.ru",
	"wordpress.com",
	"wattpad.com",
	"laposte.fr",
}


def _parse_symbol_lines(stdout: str) -> Dict[str, Any]:
	positive: List[Dict[str, Any]] = []
	negative: List[Dict[str, Any]] = []
	unknown: List[Dict[str, Any]] = []
	for raw in stdout.splitlines():
		line = raw.strip()
		# Match lines like: [+] domain.com
		m = re.match(r"^\[([+\-x])\]\s+([^\s]+)$", line)
		if not m:
			continue
		symbol, site = m.group(1), m.group(2)
		item = {"site": site, "loginBehind": site.lower() in LOGIN_BEHIND_DOMAINS}
		if symbol == "+":
			positive.append(item)
		elif symbol == "-":
			negative.append(item)
		else:
			unknown.append(item)
	return {
		"positive": positive,
		"negative": negative,
		"unknown": unknown,
		"totals": {
			"positive": len(positive),
			"negative": len(negative),
			"unknown": len(unknown),
		},
	}


def run_holehe(email: str, timeout_seconds: int = 60, prefer_text: bool = False) -> Dict[str, Any]:
	holehe_bin = _resolve_holehe_bin()
	if not holehe_bin:
		return {"error": "holehe is not installed or not in PATH. Install with: pip install 'holehe==1.61'", "hint": "You can set HOLEHE_BIN to the full path of the holehe binary."}

	if prefer_text:
		commands: List[List[str]] = [[holehe_bin, email]]
	else:
		commands: List[List[str]] = [
			[holehe_bin, email, "-o", "json"],
			[holehe_bin, email, "--output", "json"],
			[holehe_bin, "-j", email],
			# Fallback: run without JSON flags to capture human-readable output
			[holehe_bin, email],
		]

	last_result: Dict[str, Any] = {"error": "holehe produced no JSON output"}
	for cmd in commands:
		try:
			proc = subprocess.run(
				cmd,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				check=False,
				timeout=timeout_seconds,
				text=True,
			)
			# Strip ANSI before any parsing/display
			clean_stdout = _strip_ansi(proc.stdout)
			clean_stderr = _strip_ansi(proc.stderr)
			parsed = _try_parse_json(clean_stdout)
			if parsed is not None:
				return {
					"ok": True,
					"command": " ".join(shlex.quote(c) for c in cmd),
					"data": parsed,
					"stderr": clean_stderr[-2000:],
					"returncode": proc.returncode,
				}
			# If not JSON, but we have any stdout/stderr, return it so UI can show it
			if clean_stdout or clean_stderr:
				parsed_symbols = _parse_symbol_lines(clean_stdout)
				last_result = {
					"ok": False,
					"command": " ".join(shlex.quote(c) for c in cmd),
					"stdout": clean_stdout[-4000:],
					"stderr": clean_stderr[-4000:],
					"parsed": parsed_symbols if any(parsed_symbols.values()) else None,
					"returncode": proc.returncode,
				}
				continue
			last_result = {
				"ok": False,
				"command": " ".join(shlex.quote(c) for c in cmd),
				"stdout": clean_stdout[-2000:],
				"stderr": clean_stderr[-2000:],
				"returncode": proc.returncode,
			}
		except FileNotFoundError:
			return {"error": f"holehe binary not found: {cmd[0]}", "hint": "Set HOLEHE_BIN env var to the holehe executable path."}
		except subprocess.TimeoutExpired:
			last_result = {"error": "holehe timed out"}
			continue
		except Exception as exc:  # noqa: BLE001
			last_result = {"error": str(exc)}
			continue

	return last_result