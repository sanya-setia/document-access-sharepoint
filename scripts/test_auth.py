from sp_linker.auth import acquire_token

if __name__ == "__main__":
    token = acquire_token()
    print("✅ Got a token (first 40 chars):", token[:40], "...")


