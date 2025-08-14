#!/usr/bin/env python
from sp_linker.graph import GraphClient
from sp_linker.sharepoint import get_site_id, list_drives, pick_default_drive

def main():
    hostname = input("SharePoint hostname (e.g., contoso.sharepoint.com): ").strip()
    site_path = input("Site path (e.g., sites/Finance): ").strip()

    client = GraphClient()
    site_id = get_site_id(client, hostname, site_path)
    print(f"\n✅ Site ID: {site_id}")

    drives = list_drives(client, site_id)
    if not drives:
        print("No document libraries found.")
        return

    print("\n📁 Document Libraries on this site:")
    for d in drives:
        print(f" - {d.get('name')} (id: {d.get('id')})")

    chosen_id, chosen_name = pick_default_drive(drives)
    print(f"\n Default library I’ll use by default: {chosen_name} (id: {chosen_id})")

if __name__ == "__main__":
    main()
