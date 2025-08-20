#!/usr/bin/env python
from __future__ import annotations
import argparse, json, webbrowser
from sp_linker.graph import GraphClient
from sp_linker.sharepoint import (
    get_site_id, list_drives, pick_default_drive,
    normalize_path_for_drive, get_file_web_url,
)

def main():
    ap = argparse.ArgumentParser(description="Get a SharePoint file link (webUrl) via Microsoft Graph.")
    ap.add_argument("--hostname", required=True, help="SharePoint hostname, e.g. contoso.sharepoint.com")
    ap.add_argument("--site-path", required=True, help="Site path, e.g. sites/Finance (or teams/Finance)")
    ap.add_argument("--path", required=True, help="File path relative to library (e.g., Reports/Budget.xlsx). "
                                                 "Including the library name also works.")
    ap.add_argument("--json", action="store_true", help="Output JSON (hostname, sitePath, path, webUrl)")
    ap.add_argument("--open", action="store_true", help="Open the webUrl in your default browser")
    args = ap.parse_args()

    client = GraphClient()

    # 1) Site
    site_id = get_site_id(client, args.hostname, args.site_path)

    # 2) Drives (document libraries)
    drives = list_drives(client, site_id)
    drive_id, drive_name = pick_default_drive(drives)

    # 3) Normalize file path (strip leading 'Documents/' or 'Shared Documents/' if included)
    rel = normalize_path_for_drive(args.path, drive_name)

    # 4) Fetch link
    web_url = get_file_web_url(client, drive_id, rel)

    if args.json:
        print(json.dumps({
            "hostname": args.hostname,
            "sitePath": args.site_path,
            "inputPath": args.path,
            "normalizedPath": rel,
            "webUrl": web_url
        }, indent=2))
    else:
        print("\n✅ SharePoint link:")
        print(web_url)

    if args.open:
        webbrowser.open(web_url)

if __name__ == "__main__":
    main()
