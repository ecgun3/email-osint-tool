import re
from datetime import datetime, timezone
from typing import Optional


def extract_domain(value: Optional[str]) -> Optional[str]:
	if not value:
		return None
	value = value.strip()
	if "@" in value:
		parts = value.rsplit("@", 1)
		candidate = parts[1]
	else:
		candidate = value
	# Remove scheme and path if accidentally included
	candidate = re.sub(r"^https?://", "", candidate, flags=re.IGNORECASE)
	candidate = candidate.split("/")[0].split(":")[0]
	candidate = candidate.strip().strip(".")
	return candidate or None


def now_utc_iso() -> str:
	return datetime.now(timezone.utc).isoformat()