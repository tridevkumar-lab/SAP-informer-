"""Read-only OData adapter. The SAP service must be configured by your team."""
from datetime import datetime, timezone
import requests
from .config import settings


class SAPNotConfigured(RuntimeError):
    pass


class SAPReadError(RuntimeError):
    pass


def get_stock(material: str, plant: str, storage_location: str | None = None) -> tuple[dict, str]:
    if not settings.sap_stock_odata_url:
        raise SAPNotConfigured("SAP stock OData service is not configured")
    if not material or not plant:
        raise ValueError("Material and plant are required for a stock lookup")

    params = {"Material": material, "Plant": plant}
    if storage_location:
        params["StorageLocation"] = storage_location
    try:
        response = requests.get(
            settings.sap_stock_odata_url,
            params=params,
            auth=(settings.sap_username, settings.sap_password)
            if settings.sap_username else None,
            headers={"Accept": "application/json"},
            timeout=settings.sap_timeout_seconds,
            verify=settings.sap_verify_tls,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise SAPReadError("Could not read stock from SAP. Check service/network configuration.") from exc
    return payload, datetime.now(timezone.utc).isoformat()
