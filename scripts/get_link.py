#!/usr/bin/env python
from __future__ import annotations
import argparse
from sp_linker.graph import GraphClient
from sp_linker.sharepoint import get_site_id, list_drives, pick_default_drive, normalize_path_for_drive, get_file_web_url

def main():
    ap = argparse.ArgumentParser(description="Get a SharePoint file link (webUrl) via Microsoft Graph.")
    ap.add_argument("--hostname", required=True, help="Your SharePoint hostname, e.g. contoso.sharepoint.com")
    ap.add_argument("--site-path", required=True, help="Site path, e.g. sites/Finance")
    ap.add_argument("--path", required=True, help="File path (relative to library root, or include library name)")
    args = ap.parse_args()

    client = GraphClient()
    site_id = get_site_id(client, args.hostname, args.site_path)
    drives = list_drives(client, site_id)
    drive_id, drive_name = pick_default_drive(drives)
    rel = normalize_path_for_drive(args.path, drive_name)
    url = get_file_web_url(client, drive_id, rel)

    print("\n✅ SharePoint link:")
    print(url)

if __name__ == "__main__":
    main()
