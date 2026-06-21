#!/usr/bin/env python3
"""Regenerate the JSON-driven content blocks on the Fuence website.

Reads content/publications.json and content/milestones.json, and
rewrites everything between matching
  <!-- CONTENT:BEGIN <name> -->  ...  <!-- CONTENT:END <name> -->
marker comments in:
  publications/index.html  (regions: pub-all, pub-reports, pub-opeds,
                             pub-briefs, pub-guest, pub-milestones)
  index.html                (region:  home-latest)
  series/bangladesh/index.html, series/india/index.html
                            (region:  series-pubs)

Anything outside these marker regions is left untouched — manual edits
(see content/content-log.md) live there.

Design doc: /home/elijo/futura-genesis/fuence-website-content-system.md
Usage: python3 tools/build_content.py   (run from anywhere; paths are
       resolved relative to this file's location)
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"

TYPE_INFO = {
    "report": ("badge-teal", "Report"),
    "oped": ("badge-amber", "Op-Ed"),
    "brief": ("badge-teal", "Brief"),
    "guest": ("badge-amber", "Guest Article"),
}

SERIES_LABEL = {
    "bangladesh": "Bangladesh",
    "india": "India / China",
}

HOME_PINNED_LIMIT = 3


def load(name):
    return json.loads((CONTENT_DIR / name).read_text())


def sort_pubs(pubs):
    # stable sort: items with equal "date" keep their relative order
    # from publications.json
    return sorted(pubs, key=lambda p: p["date"], reverse=True)


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def resolve_link(link, depth):
    """Resolve a stored `link` for a page at the given marker-region depth.

    "#" and absolute URLs pass through unchanged. Root-relative links (Tier B
    hosted pages, e.g. "publications/{id}/") are prefixed with "../" * depth.
    depth: 0 = index.html, 1 = publications/index.html, 2 = series/{slug}/index.html.
    """
    if link == "#" or link.startswith(("http://", "https://")):
        return link
    return "../" * depth + link


# ----------------------------------------------------------------------
# HTML fragment templates
# ----------------------------------------------------------------------

def pub_item_full(item, depth, show_series=True, show_author=False, indent="        "):
    cls, label = TYPE_INFO[item["type"]]
    series_span = ""
    if show_series and item.get("series"):
        series_span = f'<span class="pi-series">{SERIES_LABEL.get(item["series"], "")}</span>'
    meta = item["date_label"]
    if show_author and item.get("author"):
        meta = f'{meta} · {item["author"]}'
    href = resolve_link(item["link"], depth)
    return (
        f'{indent}<div class="pub-item scroll-reveal">\n'
        f'{indent}  <div class="pi-type"><span class="badge {cls}">{label}</span>{series_span}</div>\n'
        f'{indent}  <div class="pi-body">\n'
        f'{indent}    <h4>{item["title"]}</h4>\n'
        f'{indent}    <p>{item["excerpt"]}</p>\n'
        f'{indent}    <div class="pi-meta"><span class="text-muted">{meta}</span></div>\n'
        f'{indent}  </div>\n'
        f'{indent}  <div class="pi-actions"><a href="{href}" class="btn btn-outline btn-sm" target="_blank">Read →</a></div>\n'
        f'{indent}</div>'
    )


def pub_item_compact(item, depth, show_series=True, indent="        "):
    cls, label = TYPE_INFO[item["type"]]
    series_span = ""
    if show_series and item.get("series"):
        series_span = f'<span class="pi-series">{SERIES_LABEL.get(item["series"], "")}</span>'
    href = resolve_link(item["link"], depth)
    return (
        f'{indent}<div class="pub-item">\n'
        f'{indent}  <div class="pi-type"><span class="badge {cls}">{label}</span>{series_span}</div>\n'
        f'{indent}  <div class="pi-body"><h4>{item["title"]}</h4><p>{item["excerpt"]}</p>'
        f'<div class="pi-meta"><span class="text-muted">{item["date_label"]}</span></div></div>\n'
        f'{indent}  <div class="pi-actions"><a href="{href}" class="btn btn-outline btn-sm" target="_blank">Read →</a></div>\n'
        f'{indent}</div>'
    )


def pub_strip_card(item, idx, depth, indent="      "):
    cls, label = TYPE_INFO[item["type"]]
    delay = f" delay-{idx + 1}" if idx < 3 else ""
    href = resolve_link(item["link"], depth)
    return (
        f'{indent}<div class="pub-strip-card card scroll-reveal{delay}">\n'
        f'{indent}  <span class="badge {cls}">{label}</span>\n'
        f'{indent}  <h4>{item["title"]}</h4>\n'
        f'{indent}  <p class="pub-strip-excerpt">{item["excerpt"]}</p>\n'
        f'{indent}  <div class="pub-strip-meta">\n'
        f'{indent}    <span class="text-muted">{item["date_label"]}</span>\n'
        f'{indent}    <a href="{href}" class="pub-strip-link" target="_blank">Read →</a>\n'
        f'{indent}  </div>\n'
        f'{indent}</div>'
    )


def milestone_item(m, indent="        "):
    return (
        f'{indent}<div class="milestone-item">\n'
        f'{indent}  <div class="ms-date">{m["date"]}</div>\n'
        f'{indent}  <div class="ms-body">\n'
        f'{indent}    <h4>{m["title"]}</h4>\n'
        f'{indent}    <p>{m["body"]}</p>\n'
        f'{indent}  </div>\n'
        f'{indent}</div>'
    )


def empty_guest_tab(indent="        "):
    return (
        f'{indent}<div class="empty-tab">\n'
        f'{indent}  <p>No guest articles yet. Interested in contributing?</p>\n'
        f'{indent}  <a href="../contact/index.html" class="btn btn-primary" style="margin-top:16px">Get in Touch →</a>\n'
        f'{indent}</div>'
    )


# ----------------------------------------------------------------------
# Region builders
# ----------------------------------------------------------------------

def build_pub_all(pubs, depth):
    return "\n\n".join(pub_item_full(p, depth, show_series=True, show_author=False) for p in pubs)


def build_pub_type_tab(pubs, type_key, depth):
    items = [p for p in pubs if p["type"] == type_key]
    return "\n".join(pub_item_compact(p, depth, show_series=True) for p in items)


def build_pub_guest(pubs, depth):
    items = [p for p in pubs if p["type"] == "guest"]
    if not items:
        return empty_guest_tab()
    return "\n".join(pub_item_compact(p, depth, show_series=True) for p in items)


def build_home_latest(pubs, depth):
    pinned = [p for p in pubs if p.get("pinned_home")][:HOME_PINNED_LIMIT]
    return "\n\n".join(pub_strip_card(p, i, depth) for i, p in enumerate(pinned))


def build_series_pubs(pubs, slug, depth):
    items = [p for p in pubs if p.get("series") == slug]
    return "\n".join(pub_item_full(p, depth, show_series=False, show_author=True, indent="      ") for p in items)


def build_milestones(milestones):
    return "\n".join(milestone_item(m) for m in milestones)


# ----------------------------------------------------------------------
# Marker replacement
# ----------------------------------------------------------------------

def replace_region(text, name, body, path):
    pattern = re.compile(
        r"([ \t]*<!-- CONTENT:BEGIN " + re.escape(name) + r" -->)\n"
        r"(.*?)"
        r"([ \t]*<!-- CONTENT:END " + re.escape(name) + r" -->)",
        re.DOTALL,
    )
    if not pattern.search(text):
        raise SystemExit(f"Marker region '{name}' not found in {path}")
    return pattern.sub(lambda m: m.group(1) + "\n" + body + "\n" + m.group(3), text, count=1)


def process_file(path, regions):
    text = path.read_text()
    for name, body in regions:
        text = replace_region(text, name, body, path)
    path.write_text(text)


# ----------------------------------------------------------------------
# content-log.md auto-append (systematic entries only)
# ----------------------------------------------------------------------

def update_log(pubs, milestones):
    log_path = CONTENT_DIR / "content-log.md"
    lines = log_path.read_text().splitlines()
    existing_ids = set()
    for line in lines:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 3 and cells[1] in ("systematic", "pipeline"):
            existing_ids.add(cells[2])

    today = date.today().isoformat()
    new_rows = []
    for p in pubs:
        if p["id"] not in existing_ids:
            method = p.get("source", "systematic")
            new_rows.append(
                f'| {today} | {method} | {p["id"]} | {p["type"]} | {p.get("series") or "—"} | publications.json |'
            )
    for m in milestones:
        if m["id"] not in existing_ids:
            new_rows.append(
                f'| {today} | systematic | {m["id"]} | milestone | — | milestones.json |'
            )

    if new_rows:
        with log_path.open("a") as f:
            for row in new_rows:
                f.write(row + "\n")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():
    pubs = sort_pubs(load("publications.json"))
    milestones = load("milestones.json")

    process_file(ROOT / "publications" / "index.html", [
        ("pub-all", build_pub_all(pubs, depth=1)),
        ("pub-reports", build_pub_type_tab(pubs, "report", depth=1)),
        ("pub-opeds", build_pub_type_tab(pubs, "oped", depth=1)),
        ("pub-briefs", build_pub_type_tab(pubs, "brief", depth=1)),
        ("pub-guest", build_pub_guest(pubs, depth=1)),
        ("pub-milestones", build_milestones(milestones)),
    ])

    process_file(ROOT / "index.html", [
        ("home-latest", build_home_latest(pubs, depth=0)),
    ])

    for slug in ("bangladesh", "india"):
        process_file(ROOT / "series" / slug / "index.html", [
            ("series-pubs", build_series_pubs(pubs, slug, depth=2)),
        ])

    update_log(pubs, milestones)
    print("build_content.py: regenerated all content regions.")


if __name__ == "__main__":
    main()
