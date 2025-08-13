from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

@dataclass
class Settings:
    tenant_id: str
    client_id: str
    client_secret: str | None
    auth_mode: str  # "device" or "confidential"

def get_settings() -> Settings:
    tenant = os.getenv("TENANT_ID", "").strip()
    client = os.getenv("CLIENT_ID", "").strip()
    secret = os.getenv("CLIENT_SECRET")
    mode = (os.getenv("AUTH_MODE") or "device").strip().lower()

    if not tenant or not client:
        raise RuntimeError("TENANT_ID and CLIENT_ID must be set in .env")
    if mode not in {"device", "confidential"}:
        raise RuntimeError("AUTH_MODE must be 'device' or 'confidential'")

    return Settings(tenant, client, secret, mode)
