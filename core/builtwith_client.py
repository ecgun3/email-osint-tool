from typing import Any, Dict, Optional, List
import re
import requests
from time import perf_counter


def _simplify_builtwith(response_json: Any) -> Dict[str, Any]:
	# BuiltWith can sometimes return a JSON string for errors; guard against non-dict
	if not isinstance(response_json, dict):
		return {"error": "Unexpected BuiltWith response type", "raw": response_json}

	results = response_json.get("Results") or response_json.get("results") or []
	if not isinstance(results, list) or not results:
		return {"summary": {}, "flat": [], "paths": [], "raw": response_json}

	first = results[0] if isinstance(results[0], dict) else {}
	data = first.get("Result") or first.get("result") or {}
	if not isinstance(data, dict):
		return {"summary": {}, "flat": [], "paths": [], "raw": response_json}

	paths = data.get("Paths") or data.get("paths") or []
	if not isinstance(paths, list):
		paths = []

	# Aggregate technologies across all paths
	tech_by_category: Dict[str, List[str]] = {}
	tech_flat: List[str] = []

	# Group by a derived base name (e.g., "jQuery 1.10.1" -> base "jQuery"),
	# and accumulate variant counts and categories.
	def derive_base_name(original: str) -> str:
		name = (original or "").strip()
		# Strip common version suffixes: " v1.2.3", " 1.2", etc.
		name = re.sub(r"\s+v?\d+(?:[._-]\d+)*(?:\s.*)?$", "", name, flags=re.IGNORECASE)
		# If starts with a known family (jquery, microsoft), group by that token
		low = name.lower()
		for root in ("jquery", "microsoft"):
			if low.startswith(root):
				return root
		# Otherwise, use the cleaned name itself as base key (normalized)
		return low

	# base_key -> group info
	base_groups: Dict[str, Dict[str, Any]] = {}
	for path in paths:
		if not isinstance(path, dict):
			continue
		techs = path.get("Technologies", []) or path.get("technologies", []) or []
		if not isinstance(techs, list):
			continue
		for tech in techs:
			if not isinstance(tech, dict):
				continue
			name = tech.get("Name") or tech.get("name")
			cats = tech.get("Categories") or tech.get("categories") or []
			if not name:
				continue
			# Flat collection (no categorization)
			if name not in tech_flat:
				tech_flat.append(name)
			# Grouping by base name
			base_key = derive_base_name(name)
			grp = base_groups.setdefault(base_key, {
				"base": name if base_key == name.lower() else base_key.title(),
				"total": 0,
				"variants": {},  # variant_name -> count
				"categories": set(),
			})
			grp["total"] += 1
			grp["variants"][name] = grp["variants"].get(name, 0) + 1
			if not cats or not isinstance(cats, list):
				tech_by_category.setdefault("Unknown", [])
				if name not in tech_by_category["Unknown"]:
					tech_by_category["Unknown"].append(name)
			else:
				for cat in cats:
					if not isinstance(cat, dict):
						continue
					cat_name = cat.get("Name") or cat.get("name") or "Uncategorized"
					tech_by_category.setdefault(cat_name, [])
					if name not in tech_by_category[cat_name]:
						tech_by_category[cat_name].append(name)
					# Capture categories into grouping entry
					grp["categories"].add(cat_name)

	# Ensure deterministic order for display
	tech_flat = sorted(tech_flat)
	grouped: List[Dict[str, Any]] = []
	for base_key, info in base_groups.items():
		cats_list = sorted(info["categories"]) if isinstance(info.get("categories"), set) else []
		variants_list = [
			{"name": var_name, "count": var_count}
			for var_name, var_count in sorted(info["variants"].items(), key=lambda x: (-x[1], x[0].lower()))
		]
		grouped.append({
			"name": info["base"],
			"count": info["total"],
			"categories": cats_list,
			"variants": variants_list,
		})
	# Sort groups by total desc, then name asc
	grouped.sort(key=lambda x: (-x["count"], str(x["name"]).lower()))

	return {"summary": tech_by_category, "flat": tech_flat, "grouped": grouped, "paths": paths, "raw": response_json}


def fetch_builtwith(domain: str, api_key: str, timeout_seconds: int = 15) -> Dict[str, Any]:
	url = "https://api.builtwith.com/v21/api.json"
	params = {"KEY": api_key, "LOOKUP": domain}
	try:
		start_ts = perf_counter()
		resp = requests.get(url, params=params, timeout=timeout_seconds)
		if resp.status_code != 200:
			return {
				"error": f"BuiltWith API returned status {resp.status_code}",
				"status_code": resp.status_code,
				"text": resp.text[:2000],
				"elapsedMs": int((perf_counter() - start_ts) * 1000),
			}
		data: Any = resp.json()
		result = _simplify_builtwith(data)
		result["elapsedMs"] = int((perf_counter() - start_ts) * 1000)
		return result
	except requests.exceptions.Timeout:
		return {"error": "BuiltWith request timed out"}
	except requests.exceptions.RequestException as exc:  # noqa: BLE001
		return {"error": str(exc)}
	except ValueError:
		return {"error": "Failed to parse BuiltWith JSON response"}


def fetch_technology_stack(domain: str) -> Dict[str, Any]:
	"""Compatibility wrapper for unit tests to monkeypatch.

	Production code should use fetch_builtwith with an API key.
	"""
	return {"domain": domain, "note": "use fetch_builtwith for real data"}