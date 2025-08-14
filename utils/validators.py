import re
from typing import Optional


# Simplified yet practical email regex (does not cover 100% RFC cases)
_EMAIL_RE = re.compile(
	r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$",
	re.IGNORECASE,
)

# Domain validation: labels 1-63 chars, overall <=253, TLD >= 2
_DOMAIN_RE = re.compile(
	r"^(?=.{1,253}$)(?!-)([A-Z0-9-]{1,63}\.)+[A-Z]{2,}$",
	re.IGNORECASE,
)


def is_valid_email(value: str) -> bool:
	if not value or "@" not in value:
		return False
	return _EMAIL_RE.fullmatch(value) is not None


def is_valid_domain(value: str) -> bool:
	if not value or "." not in value:
		return False
	return _DOMAIN_RE.fullmatch(value) is not None


def sanitize_name(value: Optional[str]) -> str:
	if not value:
		return ""
	# Keep letters only; strip spaces and punctuation
	return re.sub(r"[^a-z]", "", value.lower())