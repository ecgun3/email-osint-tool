from typing import Any, Dict, List
import json
import shlex
import subprocess
import os
import shutil


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


def run_holehe(email: str, timeout_seconds: int = 60) -> Dict[str, Any]:
	holehe_bin = _resolve_holehe_bin()
	if not holehe_bin:
		return {"error": "holehe is not installed or not in PATH. Install with: pip install 'holehe==1.61'", "hint": "You can set HOLEHE_BIN to the full path of the holehe binary."}

	commands: List[List[str]] = [
		[holehe_bin, email, "-o", "json"],
		[holehe_bin, email, "--output", "json"],
		[holehe_bin, "-j", email],
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
			parsed = _try_parse_json(proc.stdout)
			if parsed is not None:
				return {
					"ok": True,
					"command": " ".join(shlex.quote(c) for c in cmd),
					"data": parsed,
					"stderr": proc.stderr[-2000:],
					"returncode": proc.returncode,
				}
			last_result = {
				"ok": False,
				"command": " ".join(shlex.quote(c) for c in cmd),
				"stdout": proc.stdout[-2000:],
				"stderr": proc.stderr[-2000:],
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