import dns.resolver
from typing import List, Tuple, Dict, Any


def resolve_mx(domain: str) -> Dict[str, Any]:
	"""Resolve MX records for a given domain. Returns structured result.

	Args:
		domain: Domain name to resolve

	Returns:
		{"status": "ok"|"error", "records": List[Tuple[int, str]], "error": Optional[str], "provider": str}
	"""
	try:
		answers = dns.resolver.resolve(domain, "MX")
		records: List[Tuple[int, str]] = sorted(
			[(r.preference, str(r.exchange).rstrip(".")) for r in answers],
			key=lambda x: x[0],
		)
		providers = [host for _, host in records]
		provider = infer_provider(providers)
		return {"status": "ok", "records": records, "provider": provider}
	except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers) as e:
		return {"status": "error", "records": [], "error": str(e), "provider": "Unknown"}
	except Exception as e:  # Catch-all to keep UI resilient
		return {"status": "error", "records": [], "error": str(e), "provider": "Unknown"}


def infer_provider(mx_hosts: List[str]) -> str:
	joined = " ".join(mx_hosts).lower()
	if "aspmx.l.google.com" in joined or ".google.com" in joined:
		return "Google Workspace"
	if "mail.protection.outlook.com" in joined:
		return "Microsoft 365"
	if "protonmail.ch" in joined or "protonmail.com" in joined:
		return "Proton"
	if "yahoodns" in joined or "yahoo.com" in joined:
		return "Yahoo"
	return "Unknown"

# MX record analysis