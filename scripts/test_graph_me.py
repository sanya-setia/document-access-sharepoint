import requests
from sp_linker.auth import acquire_token

GRAPH = "https://graph.microsoft.com/v1.0"

if __name__ == "__main__":
    token = acquire_token()
    r = requests.get(f"{GRAPH}/me", headers={"Authorization": f"Bearer {token}"})
    print("Status:", r.status_code)
    print("Body:", r.text[:300], "...")
