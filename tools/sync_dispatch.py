#!/usr/bin/env python3
"""Sync publishing-pipeline dispatch output into content/publications.json,
and (Tier B) generate full hosted pages for selected items.

See /home/elijo/futura-genesis/fuence-website-stage2-plan.md.

--- Tier A: metadata sync (default) ---

Scans a directory of dispatch sidecar JSON files (default:
/mnt/nas-work/ai-outputs/publishing/dispatch/website/), and for each
"ready" item with platform website-article or website-publication that
isn't already in publications.json, appends a new entry:
  - type      <- platform (website-publication -> report, website-article -> oped)
  - series    <- pool (see POOL_SERIES)
  - title     <- topic
  - excerpt   <- parsed from the dispatched .md (meta description / abstract)
  - date / date_label <- parsed from sidecar "date" (YYYYMMDD)
  - author    <- derived from type
  - link      <- "#" (placeholder — fill in once you know where the piece lives)
  - pinned_home <- false
  - source    <- "pipeline" (so content-log.md logs it with Method=pipeline)

website-presentation items are skipped (not yet supported) and reported.

After updating publications.json, runs build_content.py to regenerate all
marker regions and the content log.

Usage: python3 tools/sync_dispatch.py [dispatch-dir]
       (dispatch-dir defaults to the real pipeline dispatch/website folder;
       pass a different path to sync from a test/staging directory instead)

--- Tier B: full hosting (opt-in, per item) ---

For an item already synced via Tier A, generate
publications/{id}/index.html from the original dispatched markdown
(re-located in dispatch-dir as {platform}-{id}.md), point its `link` at
that page, and re-run build_content.py.

Usage: python3 tools/sync_dispatch.py --host <id> [dispatch-dir]
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import build_content
import md_to_html

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"

DEFAULT_DISPATCH_DIR = Path("/mnt/nas-work/ai-outputs/publishing/dispatch/website")

PLATFORM_TYPE = {
    "website-publication": "report",
    "website-article": "oped",
}

TYPE_PLATFORM = {v: k for k, v in PLATFORM_TYPE.items()}

POOL_SERIES = {
    "bwbuai": "bangladesh",
    "sonar-bangla": "bangladesh",
    "india-china": "india",
}

TYPE_AUTHOR = {
    "report": "Fuence Research Team",
    "oped": "Fuence Editorial",
}

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} — Fuence Podcast</title>
  <meta name="description" content="{excerpt}" />
  <link rel="stylesheet" href="../../assets/css/style.css" />
  <link rel="stylesheet" href="../../assets/css/nav.css" />
  <link rel="stylesheet" href="../../assets/css/inner.css" />
</head>
<body>
<div id="nav-placeholder"></div>

<section class="page-hero">
  <div class="container">
    <a href="../index.html" class="back-link">← All Publications</a>
    <span class="badge {badge_cls}">{badge_label}</span>
    <h1>{title}</h1>
    <p class="page-hero-sub">{excerpt}</p>
    <div class="pub-detail-meta"><span class="text-muted">{meta}</span></div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="pub-detail-body">
      <!-- CONTENT:BEGIN pub-body -->
{body}
      <!-- CONTENT:END pub-body -->
    </div>
  </div>
</section>

<div id="footer-placeholder"></div>
<script src="../../assets/js/nav.js"></script>
<script src="../../assets/js/main.js"></script>
</body>
</html>
"""


def load_publications():
    return json.loads((CONTENT_DIR / "publications.json").read_text())


def save_publications(pubs):
    (CONTENT_DIR / "publications.json").write_text(json.dumps(pubs, indent=2) + "\n")


def extract_excerpt(platform, text):
    if platform == "website-article":
        m = re.search(r"\*\*Suggested meta description\*\*[^\n]*\n+(.+)", text)
        if m:
            return m.group(1).strip()
        return ""

    if platform == "website-publication":
        m = re.search(r"##\s*Abstract\s*\n+(.*?)(?=\n#{1,6}\s|\n---|\Z)", text, re.DOTALL)
        if not m:
            return ""
        abstract = re.sub(r"\s+", " ", m.group(1)).strip()
        if len(abstract) <= 160:
            return abstract
        return abstract[:160].rsplit(" ", 1)[0] + "…"

    return ""


def sync(dispatch_dir):
    pubs = load_publications()
    existing_ids = {p["id"] for p in pubs}

    new_entries = []
    skipped_presentations = []

    for json_path in sorted(dispatch_dir.glob("*.json")):
        sidecar = json.loads(json_path.read_text())
        if sidecar.get("status") != "ready":
            continue

        platform = sidecar.get("platform")
        if platform == "website-presentation":
            skipped_presentations.append(json_path.name)
            continue
        if platform not in PLATFORM_TYPE:
            continue

        pool = sidecar["pool"]
        slug = sidecar["slug"]
        date_raw = sidecar["date"]
        item_id = f"{pool}-{slug}-{date_raw}"
        if item_id in existing_ids:
            continue

        md_path = json_path.with_suffix(".md")
        text = md_path.read_text() if md_path.exists() else ""

        pub_type = PLATFORM_TYPE[platform]
        dt = datetime.strptime(date_raw, "%Y%m%d")

        entry = {
            "id": item_id,
            "type": pub_type,
            "series": POOL_SERIES.get(pool),
            "title": sidecar.get("topic", "").strip(),
            "excerpt": extract_excerpt(platform, text),
            "date": dt.strftime("%Y-%m-%d"),
            "date_label": dt.strftime("%B %Y"),
            "author": TYPE_AUTHOR.get(pub_type, "Fuence Research Team"),
            "link": "#",
            "pinned_home": False,
            "source": "pipeline",
        }
        pubs.append(entry)
        existing_ids.add(item_id)
        new_entries.append(entry)

    if not new_entries:
        print("sync_dispatch.py: no new website-target items to sync.")
        if skipped_presentations:
            print(f"  (skipped {len(skipped_presentations)} website-presentation item(s) — not yet supported)")
        return

    save_publications(pubs)
    build_content.main()

    print(f"sync_dispatch.py: synced {len(new_entries)} new item(s):")
    for e in new_entries:
        print(f"  - {e['id']}  type={e['type']}  series={e['series']}  pinned_home={e['pinned_home']}  link={e['link']}")
    if skipped_presentations:
        print(f"  (skipped {len(skipped_presentations)} website-presentation item(s) — not yet supported)")


def write_hosted_page(entry, md_text):
    page_dir = ROOT / "publications" / entry["id"]
    page_dir.mkdir(parents=True, exist_ok=True)

    cls, label = build_content.TYPE_INFO[entry["type"]]
    meta = entry["date_label"]
    if entry.get("author"):
        meta = f'{meta} · {entry["author"]}'

    page = PAGE_TEMPLATE.format(
        title=entry["title"],
        excerpt=entry["excerpt"],
        badge_cls=cls,
        badge_label=label,
        meta=meta,
        body=md_to_html.body_html(md_text),
    )
    (page_dir / "index.html").write_text(page)


def host_item(item_id, dispatch_dir):
    pubs = load_publications()
    entry = next((p for p in pubs if p["id"] == item_id), None)
    if entry is None:
        sys.exit(f"sync_dispatch.py --host: no publications.json entry with id '{item_id}'")

    platform = TYPE_PLATFORM.get(entry["type"])
    if platform is None:
        sys.exit(f"sync_dispatch.py --host: type '{entry['type']}' has no Tier B page template")

    md_path = dispatch_dir / f"{platform}-{item_id}.md"
    if not md_path.exists():
        sys.exit(f"sync_dispatch.py --host: source markdown not found: {md_path}")

    write_hosted_page(entry, md_path.read_text())

    entry["link"] = f"publications/{item_id}/"
    save_publications(pubs)
    build_content.main()

    print(f"sync_dispatch.py --host: generated publications/{item_id}/index.html")
    print(f"  link updated to '{entry['link']}' — regenerated all marker regions.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "dispatch_dir", nargs="?", type=Path, default=DEFAULT_DISPATCH_DIR,
        help="dispatch sidecar directory (default: real pipeline dispatch/website folder)",
    )
    parser.add_argument(
        "--host", metavar="ID",
        help="Tier B: generate a full hosted page for an existing publications.json id "
             "(reads {platform}-{ID}.md from dispatch_dir, sets link to publications/{ID}/)",
    )
    args = parser.parse_args()

    if args.host:
        host_item(args.host, args.dispatch_dir)
        return

    sync(args.dispatch_dir)


if __name__ == "__main__":
    main()
