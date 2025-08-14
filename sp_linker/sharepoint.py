from __future__ import annotations
from typing import Dict, Any, List, Tuple
from urllib.parse import quote

from .graph import GraphClient

def get_site_id(client: GraphClient, hostname: str, site_path: str) -> str:
    """
    site_path like 'sites/Finance' or 'sites/MyTeamSite'
    """
    path = f"sites/{hostname}:/{quote('/' + site_path)}"
    data = client.get(path, params={"$select": "id,name,displayName"})
    return data["id"]

def list_drives(client: GraphClient, site_id: str) -> List[Dict[str, Any]]:
    data = client.get(f"sites/{site_id}/drives")
    return data.get("value", [])

def pick_default_drive(drives: List[Dict[str, Any]]) -> Tuple[str, str]:
    """
    Returns (drive_id, drive_name). Prefers 'Documents' or 'Shared Documents'.
    """
    if not drives:
        raise RuntimeError("No document libraries (drives) found on the site.")
    names = [d.get("name", "") for d in drives]
    preferred = next((d for d in drives if d.get("name", "").lower() in ("documents", "shared documents")), None)
    chosen = preferred or drives[0]
    return chosen["id"], chosen.get("name", "Documents")

def normalize_path_for_drive(path_from_root: str, drive_name: str) -> str:
    """
    Accepts either:
      'Reports/Budget.xlsx'  (already relative to drive root)
    OR:
      'Shared Documents/Reports/Budget.xlsx'
    We'll strip the leading library name if present.
    """
    p = path_from_root.replace("\\", "/").lstrip("/")
    dn = drive_name.lower().strip("/")
    if p.lower().startswith(dn + "/"):
        p = p[len(dn) + 1 :]
    return p

def get_file_web_url(client: GraphClient, drive_id: str, path_from_root: str) -> str:
    """
    Returns the permission-trimmed webUrl for a file in a given drive.
    """
    safe = quote(path_from_root)
    data = client.get(f"drives/{drive_id}/root:/{safe}")
    return data["webUrl"]
