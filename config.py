import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


def _get_bool(name: str, default: bool = False) -> bool:
	value = os.getenv(name)
	if value is None:
		return default
	return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
	try:
		return int(os.getenv(name, str(default)))
	except (TypeError, ValueError):
		return default


@dataclass
class Config:
	secret_key: str = os.getenv("FLASK_SECRET_KEY", "change-this-in-production")
	builtwith_api_key: Optional[str] = os.getenv("BUILTWITH_API_KEY")
	request_timeout_seconds: int = _get_int("REQUEST_TIMEOUT_SECONDS", 15)
	debug: bool = _get_bool("DEBUG", False)
	env: str = os.getenv("FLASK_ENV", "production")
	host: str = os.getenv("HOST", "0.0.0.0")
	port: int = _get_int("PORT", 5000)
	templates_auto_reload: bool = _get_bool("TEMPLATES_AUTO_RELOAD", True)


def get_config() -> Config:
	return Config()