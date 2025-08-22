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
	templates_auto_reload: bool = _get_bool("TEMPLATES_AUTO_RELOAD", False)
	# SMTP settings for sending training emails
	smtp_host: Optional[str] = os.getenv("SMTP_HOST")
	smtp_port: int = _get_int("SMTP_PORT", 587)
	smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
	smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
	smtp_use_tls: bool = _get_bool("SMTP_USE_TLS", True)
	smtp_use_ssl: bool = _get_bool("SMTP_USE_SSL", False)
	smtp_from: Optional[str] = os.getenv("SMTP_FROM")
	# Mailbox verification (SMTP probe) toggle
	probe_smtp_enable: bool = _get_bool("PROBE_SMTP_ENABLE", True)
	probe_mail_from: Optional[str] = os.getenv("PROBE_SMTP_MAIL_FROM")


def get_config() -> Config:
	return Config()