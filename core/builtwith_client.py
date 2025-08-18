from typing import Any, Dict


def fetch_technology_stack(domain: str) -> Dict[str, Any]:
    """Query BuiltWith (or similar) to fetch technology stack for the domain.

    Intentionally left unimplemented; provide concrete behavior in production code.
    Tests should monkeypatch this function.
    """
    raise NotImplementedError("fetch_technology_stack must be implemented")