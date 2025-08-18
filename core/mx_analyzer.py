from typing import Any, Dict, List


def fetch_mx_records(domain: str) -> List[Dict[str, Any]]:
    """Return MX records for a given domain.

    Intentionally left unimplemented; provide concrete behavior in production code.
    Tests should monkeypatch this function.
    """
    raise NotImplementedError("fetch_mx_records must be implemented")