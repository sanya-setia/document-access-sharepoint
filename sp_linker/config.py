from __future__ import annotations #for dataclasses
from dataclasses import dataclass  #Dataclass is for making small "containers" class for our settings
import os #os is for reading environment variables
from dotenv import load_dotenv #is for loading .env into os.environ

load_dotenv()

@dataclass
class Settings:
    tenant_id: str
    client_id: str
    client_secret: str | None
    auth_mode: str