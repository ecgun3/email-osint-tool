from typing import Any, Dict, Optional, List
import requests


def _simplify_builtwith(response_json: Any) -> Dict[str, Any]:
	# BuiltWith can sometimes return a JSON string for errors; guard against non-dict
	if not isinstance(response_json, dict):
		return {"error": "Unexpected BuiltWith response type", "raw": response_json}

	results = response_json.get("Results") or response_json.get("results") or []
	if not isinstance(results, list) or not results:
		return {"summary": {}, "paths": [], "raw": response_json}

	first = results[0] if isinstance(results[0], dict) else {}
	data = first.get("Result") or first.get("result") or {}
	if not isinstance(data, dict):
		return {"summary": {}, "paths": [], "raw": response_json}

	paths = data.get("Paths") or data.get("paths") or []
	if not isinstance(paths, list):
		paths = []

	# Aggregate technologies across all paths
	tech_by_category: Dict[str, List[str]] = {}
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

	return {"summary": tech_by_category, "paths": paths, "raw": response_json}


def fetch_builtwith(domain: str, api_key: str, timeout_seconds: int = 15) -> Dict[str, Any]:
	url = "https://api.builtwith.com/v21/api.json"
	params = {"KEY": api_key, "LOOKUP": domain}
	try:
		resp = requests.get(url, params=params, timeout=timeout_seconds)
		if resp.status_code != 200:
			return {
				"error": f"BuiltWith API returned status {resp.status_code}",
				"status_code": resp.status_code,
				"text": resp.text[:2000],
			}
		data: Any = resp.json()
		return _simplify_builtwith(data)
	except requests.exceptions.Timeout:
		return {"error": "BuiltWith request timed out"}
	except requests.exceptions.RequestException as exc:  # noqa: BLE001
		return {"error": str(exc)}
	except ValueError:
		return {"error": "Failed to parse BuiltWith JSON response"}