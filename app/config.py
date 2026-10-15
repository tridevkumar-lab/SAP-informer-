from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "SAP Yard Assistant")
    database_path: str = os.getenv("DATABASE_PATH", "data/assistant.db")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    sap_stock_odata_url: str = os.getenv("SAP_STOCK_ODATA_URL", "").strip()
    sap_username: str = os.getenv("SAP_USERNAME", "")
    sap_password: str = os.getenv("SAP_PASSWORD", "")
    sap_verify_tls: bool = _bool("SAP_VERIFY_TLS", True)
    sap_timeout_seconds: int = int(os.getenv("SAP_TIMEOUT_SECONDS", "15"))


settings = Settings()
