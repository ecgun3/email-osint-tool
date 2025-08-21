from typing import Any, List
import json
import shlex
import subprocess
import os
import shutil
import re
from time import perf_counter

def _try_parse_json(text: str) -> Any:
    text = text.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        pass
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
    env_bin = os.getenv("HOLEHE_BIN")
    if env_bin and os.path.isfile(env_bin) and os.access(env_bin, os.X_OK):
        return env_bin
    path_bin = shutil.which("holehe")
    if path_bin:
        return path_bin
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

def run_holehe(target: str, timeout_seconds: int = 15) -> Any:
    bin_path = _resolve_holehe_bin()
    if not bin_path:
        return {"error": "Holehe binary not found"}

    cmd = [bin_path, target, "--json"]
    try:
        start_ts = perf_counter()
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds
        )
        elapsed_ms = int((perf_counter() - start_ts) * 1000)
        output = _strip_ansi(result.stdout)
        error_output = _strip_ansi(result.stderr)
        parsed = _try_parse_json(output)
        return {
            "parsed": parsed,
            "raw_stdout": output,
            "raw_stderr": error_output,
            "returncode": result.returncode,
            "elapsedMs": elapsed_ms
        }
    except subprocess.TimeoutExpired:
        return {"error": "Holehe request timed out", "elapsedMs": timeout_seconds * 1000}
    except Exception as exc:
        return {"error": str(exc)}
