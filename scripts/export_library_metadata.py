#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, sys
from typing import Dict, Any, List, Optional

from sp_linker.graph import GraphClient
from sp_linker.sharepoint import get_site_id

# -----------------------
# Helpers
# -----------------------

def find_list(client: GraphClient, site_id: str, preferred_names: List[str]) -> Dict[str, Any]:
    """
    Returns the matching list (document library) object.
    We try common library names ('Documents', 'Shared Documents'), or a user-supplied name.
    """
    # CHANGED: select includes 'list' (not 'baseTemplate')
    page = client.get(
        f"sites/{site_id}/lists",
        params={"$select": "id,name,displayName,webUrl,list"}
    )
    lists = page.get("value", [])

    # CHANGED: document libraries = where list.template == 'documentLibrary'
    doc_lists = [l for l in lists if (l.get("list") or {}).get("template") == "documentLibrary"]

    # Try exact name match first (case-insensitive)
    for name in preferred_names:
        for l in doc_lists:
            if (l.get("name") or "").strip().lower() == name.strip().lower():
                return l

    # Fallback to first document library if no name matched
    if doc_lists:
        return doc_lists[0]

    raise RuntimeError("No document libraries (list.template == 'documentLibrary') found on this site.")

def iter_list_items(client: GraphClient, site_id: str, list_id: str,
                    server_filter: Optional[str] = None, page_size: int = 200):
    """
    Yields list items with fields + driveItem(webUrl).
    Handles Graph paging via @odata.nextLink.
    """
    params = {
        "$expand": "fields,driveItem($select=webUrl)",
        "$select": "id,fields,driveItem",
        "$top": str(page_size),
    }
    if server_filter:
        params["$filter"] = server_filter

    path = f"sites/{site_id}/lists/{list_id}/items"
    data = client.get(path, params=params)
    while True:
        for item in data.get("value", []):
            yield item
        next_link = data.get("@odata.nextLink")
        if not next_link:
            break
        # next_link is an absolute URL; GraphClient expects a relative path → strip base
        rel = next_link.split("graph.microsoft.com/v1.0/")[-1]
        data = client.get(rel)

def pick_fields_for_csv(items: List[Dict[str, Any]], requested: Optional[List[str]]) -> List[str]:
    """
    Decide which field names to write based on data + user request.
    We always include FileLeafRef (name) when present.
    """
    # Gather all field keys seen
    keys = set()
    for it in items[:100]:  # sample first page(s)
        fld = it.get("fields") or {}
        keys.update(fld.keys())

    # Always-good defaults
    defaults = ["FileLeafRef", "Title", "Verified", "Accounts", "Region", "Modified", "Editor"]

    if requested:
        base = requested
    else:
        base = [k for k in defaults if k in keys]

    # Ensure FileLeafRef is first if present
    if "FileLeafRef" in keys and "FileLeafRef" not in base:
        base = ["FileLeafRef"] + base

    # Always include webUrl column (added separately)
    return base

def normalize_field_value(v: Any) -> Any:
    """
    Basic cleanup for CSV. Handles dicts from people fields etc.
    """
    if isinstance(v, dict):
        # For people fields, SharePoint may return {'LookupValue': 'Name', ...}
        return v.get("LookupValue") or v.get("Email") or str(v)
    if isinstance(v, list):
        return "; ".join([normalize_field_value(x) for x in v])
    return v

# -----------------------
# CLI
# -----------------------

def main():
    ap = argparse.ArgumentParser(
        description="Export documents + metadata columns + webUrl from a SharePoint library to CSV."
    )
    ap.add_argument("--hostname", required=True, help="SharePoint hostname, e.g. contoso.sharepoint.com")
    ap.add_argument("--site-path", required=True, help="Site path, e.g. sites/Finance (or teams/Finance)")
    ap.add_argument("--list-name", default="", help="Library/list name (e.g., 'Documents' or 'Shared Documents'). If omitted, will auto-pick.")
    ap.add_argument("--columns", default="", help="Comma-separated field names to include (e.g., 'Verified,Accounts,Region').")
    ap.add_argument("--filter", default="", help="OData filter on fields, e.g., \"fields/Verified eq true and fields/Region eq 'EMEA'\"")
    ap.add_argument("--out-csv", required=True, help="Output CSV path")
    args = ap.parse_args()

    client = GraphClient()
    site_id = get_site_id(client, args.hostname, args.site_path)

    preferred_names = []
    if args.list_name:
        preferred_names.append(args.list_name)
    # Try common English library names by default
    preferred_names += ["Documents", "Shared Documents"]

    lib = find_list(client, site_id, preferred_names)
    list_id = lib["id"]
    list_name = lib.get("name") or lib.get("displayName") or "<library>"

    print(f"📁 Using library: {list_name} (id: {list_id})")

    # Stream items (first pass to collect a small sample for column choice)
    sample_items = []
    rows_gen = iter_list_items(client, site_id, list_id, server_filter=(args.filter or None))
    try:
        for _ in range(50):  # sample up to 50 to decide columns
            sample_items.append(next(rows_gen))
    except StopIteration:
        pass  # fewer than 50 available; that's fine

    requested_cols = [c.strip() for c in args.columns.split(",") if c.strip()] if args.columns else None
    field_cols = pick_fields_for_csv(sample_items, requested_cols)

    # Prepare CSV writer
    out_fields = field_cols + ["webUrl"]
    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()

        # Write sample first
        for it in sample_items:
            writer.writerow(_row_from_item(it, field_cols))

        # Then continue with the rest of the paging generator
        for it in rows_gen:
            writer.writerow(_row_from_item(it, field_cols))

    print(f"✅ Wrote CSV: {args.out_csv}")
    print(f"   Columns: {', '.join(out_fields)}")


def _row_from_item(item: Dict[str, Any], field_cols: List[str]) -> Dict[str, Any]:
    fields = item.get("fields") or {}
    web_url = (item.get("driveItem") or {}).get("webUrl", "")
    row = {}
    for col in field_cols:
        row[col] = normalize_field_value(fields.get(col, ""))
    row["webUrl"] = web_url
    return row


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
