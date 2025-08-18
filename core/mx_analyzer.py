from typing import Any, Dict, List

import dns.resolver
from time import perf_counter


_PROVIDER_MAP = [
	("Google Workspace", [".google.com", "aspmx.l.google.com", "googlemail.com"]),
	("Microsoft 365", [
		"mail.protection.outlook.com",
		"protection.outlook.com",
		"outlook.com",
		"ppe-hosted.com",
		"exchangeonline",
		"microsoft.com",
	]),
	("Zoho Mail", [".zoho.com", ".zoho.in", ".zoho.eu", ".zoho.com.cn"]),
	("Proton Mail", ["protonmail.ch", "protonmail.com"]),
	("Fastmail", [".fastmail.", "messagingengine.com"]),
	("Yandex Mail", [".yandex.net", ".yandex.ru", ".yandex.com"]),
	("IONOS (1&1)", ["kundenserver.de", "ionos.com", "ionos.de", "ui-dns.de", "ui-dns.com"]),
	("OVH", ["mail.ovh.net", ".ovh.net"]),
	("Rackspace", ["emailsrvr.com"]),
	("Proofpoint", ["pphosted.com"]),
	("Mailgun", ["mailgun.org"]),
	("Cloudflare Email Routing", ["mx.cloudflare.net"]),
	("Tencent / QQ", ["qq.com"]),
]


def _identify_provider(mx_hosts: List[str]) -> str:
	for provider, needles in _PROVIDER_MAP:
		for host in mx_hosts:
			for needle in needles:
				if needle in host:
					return provider
	return "Unknown or self-hosted"


def analyze_mx(domain: str, timeout_seconds: int = 10) -> Dict[str, Any]:
	mx_records: List[Dict[str, Any]] = []
	mx_hosts: List[str] = []
	warnings: List[str] = []

	try:
		start_ts = perf_counter()
		answers = dns.resolver.resolve(domain, "MX", lifetime=timeout_seconds)
		for rdata in sorted(answers, key=lambda r: int(r.preference)):
			preference = int(getattr(rdata, "preference", 0))
			exchange = str(getattr(rdata, "exchange", "")).rstrip(".")
			mx_records.append({"preference": preference, "exchange": exchange})
			mx_hosts.append(exchange)
	except dns.resolver.NoAnswer:
		warnings.append("No MX records found for domain.")
	except dns.resolver.NXDOMAIN:
		warnings.append("Domain does not exist (NXDOMAIN).")
	except dns.exception.Timeout:
		warnings.append("DNS lookup timed out.")
	except Exception as exc:  # noqa: BLE001
		return {"error": str(exc)}

	provider = _identify_provider(mx_hosts) if mx_hosts else "Unknown"

	return {
		"domain": domain,
		"mx_records": mx_records,
		"mx_hosts": mx_hosts,
		"provider": provider,
		"warnings": warnings,
		"elapsedMs": int((perf_counter() - start_ts) * 1000) if mx_records else None,
	}
