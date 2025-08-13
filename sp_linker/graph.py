from __future__ import annotations
import requests
from typing import Any, Dict, Optional

from .config import GRAPH_BASE
from .errors import GraphHttpError
from .auth import acquire_token

class GraphClient:
    def __init__(self, base: str = GRAPH_BASE, token: Optional[str] = None):
        self.base = base
        self._token = token or acquire_token()

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"}

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base.rstrip('/')}/{path.lstrip('/')}"
        r = requests.get(url, headers=self._headers(), params=params)
        if not r.ok:
            raise GraphHttpError(r.status_code, r.text)
        return r.json()

    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base.rstrip('/')}/{path.lstrip('/')}"
        r = requests.post(url, headers=self._headers(), json=json)
        if not r.ok:
            raise GraphHttpError(r.status_code, r.text)
        return r.json()
