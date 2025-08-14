from typing import Dict, List, Optional

from utils.validators import sanitize_name


def _unique(seq: List[str]) -> List[str]:
	seen = set()
	out = []
	for item in seq:
		if item not in seen:
			seen.add(item)
			out.append(item)
	return out


def generate_email_patterns(first_name: str, last_name: str, domain: Optional[str] = None) -> Dict[str, List[Dict[str, str]]]:
	first = sanitize_name(first_name)
	last = sanitize_name(last_name)

	if not first and not last:
		return {"patterns": []}

	f = first[:1] if first else ""
	l = last[:1] if last else ""

	candidates: List[Dict[str, str]] = []

	def add(label: str, local: str):
		email = f"{local}@{domain}" if domain else local
		candidates.append({"label": label, "local": local, "email": email})

	# Common patterns
	if first and last:
		for sep in [".", "_", "-"]:
			add(f"first{sep}last", f"{first}{sep}{last}")
			add(f"f{sep}last", f"{f}{sep}{last}")
			add(f"first{sep}l", f"{first}{sep}{l}")
		add("firstlast", f"{first}{last}")
		add("flast", f"{f}{last}")
		add("firstl", f"{first}{l}")
		add("first", first)
		add("last", last)
		add("f.last", f"{f}.{last}")
		add("first.l", f"{first}.{l}")
	else:
		name = first or last
		add("name", name)

	# Remove duplicates by local part
	unique_locals = _unique([c["local"] for c in candidates])
	final: List[Dict[str, str]] = []
	for local in unique_locals:
		for c in candidates:
			if c["local"] == local:
				final.append(c)
				break

	return {"patterns": final}