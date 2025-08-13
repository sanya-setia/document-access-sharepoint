import random
from sp_linker.errors import GraphAuthError, GraphHttpError

def fake_graph_login():
    """Simulates logging in to Microsoft Graph."""
    if random.choice([True, False]):
        raise GraphAuthError("Invalid credentials or missing permissions.")
    return "fake_access_token"

def fake_graph_request(token: str):
    """Simulates making an API request to Microsoft Graph."""
    status_code = random.choice([200, 403, 404, 500])
    if status_code != 200:
        raise GraphHttpError(status_code, f"Simulated HTTP error {status_code}")
    return {"webUrl": "https://contoso.sharepoint.com/sites/Finance/Reports/Budget.xlsx"}

def main():
    try:
        print("🔑 Attempting to log in...")
        token = fake_graph_login()
        print("✅ Login success! Token:", token)

        print("🌐 Making API request...")
        data = fake_graph_request(token)
        print("✅ Request success! Got data:", data)

    except GraphAuthError as e:
        print("❌ AUTH ERROR:", e)

    except GraphHttpError as e:
        print("❌ HTTP ERROR:", e)

    except Exception as e:
        print("❌ UNEXPECTED ERROR:", e)

if __name__ == "__main__":
    main()
