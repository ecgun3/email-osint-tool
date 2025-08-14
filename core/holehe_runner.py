from typing import Any, Dict, List
import json
import shlex
import subprocess


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


def run_holehe(email: str, timeout_seconds: int = 60) -> Dict[str, Any]:
	commands: List[List[str]] = [
		["holehe", email, "-o", "json"],
		["holehe", email, "--output", "json"],
		["holehe", "-j", email],
		["python3", "-m", "holehe", email, "-o", "json"],
	]

	last_result: Dict[str, Any] = {}
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
			# Keep last_result for debugging
			last_result = {
				"ok": False,
				"command": " ".join(shlex.quote(c) for c in cmd),
				"stdout": proc.stdout[-2000:],
				"stderr": proc.stderr[-2000:],
				"returncode": proc.returncode,
			}
		except FileNotFoundError:
			last_result = {"error": "holehe is not installed or not in PATH"}
			continue
		except subprocess.TimeoutExpired:
			last_result = {"error": "holehe timed out"}
			continue
		except Exception as exc:  # noqa: BLE001
			last_result = {"error": str(exc)}
			continue

	return last_result or {"error": "Unknown error running holehe"}