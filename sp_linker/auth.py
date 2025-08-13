from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, Any
import msal

from .config import get_settings

SCOPES = ["Files.Read", "Sites.Read.All"]  # add/remove as needed
TOKEN_CACHE_PATH = Path(".cache/msal_token.bin")

def _load_cache() -> msal.SerializableTokenCache:
    cache = msal.SerializableTokenCache()
    if TOKEN_CACHE_PATH.exists():
        cache.deserialize(TOKEN_CACHE_PATH.read_text())
    return cache

def _save_cache(cache: msal.SerializableTokenCache) -> None:
    TOKEN_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_CACHE_PATH.write_text(cache.serialize())

def acquire_token() -> str:
    """
    Returns a bearer access token string for Microsoft Graph.
    Uses Device Code (sign-in as yourself) by default.
    Switch to confidential client by setting AUTH_MODE=confidential and CLIENT_SECRET.
    """
    settings = get_settings()
    authority = f"https://login.microsoftonline.com/{settings.tenant_id}"

    if settings.auth_mode == "device":
        cache = _load_cache()
        app = msal.PublicClientApplication(settings.client_id, authority=authority, token_cache=cache)

        # Try silent first
        accounts = app.get_accounts()
        if accounts:
            result = app.acquire_token_silent(SCOPES, account=accounts[0])
            if result and "access_token" in result:
                return result["access_token"]

        # Interactive device code
        flow = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            raise RuntimeError("Could not start device code flow. Check TENANT_ID/CLIENT_ID.")
        print("\n== Sign in required ==")
        print(flow["message"])  # shows URL + code
        result = app.acquire_token_by_device_flow(flow)
        if "access_token" not in result:
            raise RuntimeError(result.get("error_description", "Authentication failed"))
        _save_cache(cache)
        return result["access_token"]

    # Corporate "service principal" mode (later at work)
    if settings.auth_mode == "confidential":
        if not settings.client_secret:
            raise RuntimeError("CLIENT_SECRET is required for confidential auth.")
        app = msal.ConfidentialClientApplication(
            client_id=settings.client_id,
            client_credential=settings.client_secret,
            authority=authority,
        )
        # Use the application permission scope
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" not in result:
            raise RuntimeError(result.get("error_description", "Confidential auth failed"))
        return result["access_token"]

    raise RuntimeError("Unsupported AUTH_MODE")
