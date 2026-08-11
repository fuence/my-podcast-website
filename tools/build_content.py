#!/usr/bin/env python3
"""Regenerate the JSON-driven content blocks on the Fuence website.

Reads content/publications.json, content/topics.json, and
content/milestones.json, and rewrites everything between matching
  <!-- CONTENT:BEGIN <name> -->  ...  <!-- CONTENT:END <name> -->
marker comments in:
  publications/index.html  (regions: pub-all, pub-reports, pub-opeds,
                             pub-briefs, pub-guest, pub-milestones)
  index.html                (region:  home-latest)
  series/{slug}/index.html  (region:  series-pubs, one per active sub-series)

Anything outside these marker regions is left untouched — manual edits
(see content/content-log.md) live there.

Also generates a full standalone page per publication —
publications/{id}/index.html — from scratch each run (not marker-based,
since the whole page is derived data): title/excerpt/citation/JSON-LD,
Core-status topic badges, a topic-rarity-weighted related-publications
list, and a "Read the full piece on Ghost" out-link. Body text is never
hosted here — see docs/references/website-master.md's "fuence.com never
hosts long-form body text" rule.

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
    # South Asia & Bangladesh program — "bangladesh" itself is now a program
    # hub page (series/bangladesh/index.html), not a content-holding slug;
    # publications live under one of these 4 sub-series instead.
    "genesis-of-a-republic": "Genesis of a Republic",
    "republic-unmade": "A Republic Unmade",
    "republic-ascending": "The Republic Ascending",
    "stable-republic": "Stable Republic",
    # "india" series retired (T2-3) — its content was 100% bwbuai-authored,
    # now in-house only (OPEN-ITEMS CW-2/CW-3).
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


def internal_pub_url(item, depth):
    """Link to this publication's own fuence.com landing page (the citable
    page, see build_publication_pages) rather than straight to Ghost — the
    Ghost link lives as the "Read the full piece" CTA on that page instead.
    Falls back to "#" for legacy stub entries with no real Ghost link at all.
    """
    if item["link"] == "#":
        return "#"
    return resolve_link(f'publications/{item["id"]}/index.html', depth)


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
    href = internal_pub_url(item, depth)
    return (
        f'{indent}<div class="pub-item scroll-reveal">\n'
        f'{indent}  <div class="pi-type"><span class="badge {cls}">{label}</span>{series_span}</div>\n'
        f'{indent}  <div class="pi-body">\n'
        f'{indent}    <h4>{item["title"]}</h4>\n'
        f'{indent}    <p>{item["excerpt"]}</p>\n'
        f'{indent}    <div class="pi-meta"><span class="text-muted">{meta}</span></div>\n'
        f'{indent}  </div>\n'
        f'{indent}  <div class="pi-actions"><a href="{href}" class="btn btn-outline btn-sm" aria-label="Read: {item["title"]}">Read →</a></div>\n'
        f'{indent}</div>'
    )


def pub_item_compact(item, depth, show_series=True, indent="        "):
    cls, label = TYPE_INFO[item["type"]]
    series_span = ""
    if show_series and item.get("series"):
        series_span = f'<span class="pi-series">{SERIES_LABEL.get(item["series"], "")}</span>'
    href = internal_pub_url(item, depth)
    return (
        f'{indent}<div class="pub-item">\n'
        f'{indent}  <div class="pi-type"><span class="badge {cls}">{label}</span>{series_span}</div>\n'
        f'{indent}  <div class="pi-body"><h4>{item["title"]}</h4><p>{item["excerpt"]}</p>'
        f'<div class="pi-meta"><span class="text-muted">{item["date_label"]}</span></div></div>\n'
        f'{indent}  <div class="pi-actions"><a href="{href}" class="btn btn-outline btn-sm" aria-label="Read: {item["title"]}">Read →</a></div>\n'
        f'{indent}</div>'
    )


def pub_strip_card(item, idx, depth, indent="      "):
    cls, label = TYPE_INFO[item["type"]]
    delay = f" delay-{idx + 1}" if idx < 3 else ""
    href = internal_pub_url(item, depth)
    return (
        f'{indent}<div class="pub-strip-card card scroll-reveal{delay}">\n'
        f'{indent}  <span class="badge {cls}">{label}</span>\n'
        f'{indent}  <h4>{item["title"]}</h4>\n'
        f'{indent}  <p class="pub-strip-excerpt">{item["excerpt"]}</p>\n'
        f'{indent}  <div class="pub-strip-meta">\n'
        f'{indent}    <span class="text-muted">{item["date_label"]}</span>\n'
        f'{indent}    <a href="{href}" class="pub-strip-link" aria-label="Read: {item["title"]}">Read →</a>\n'
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
# Individual publication pages (publications/{id}/index.html)
# ----------------------------------------------------------------------

def topic_index(topics_data):
    """slug -> topic record, for fast lookup while building pub pages."""
    return {t["slug"]: t for t in topics_data["topics"]}


def series_info(slug, topics_data):
    return topics_data.get("series_registry", {}).get(slug, {"name": slug, "program": None})


def core_topic_badges(pub, tidx):
    slugs = pub.get("topics", [])
    names = [tidx[s]["name"] for s in slugs if s in tidx and tidx[s]["status"] == "core"]
    if not names:
        return ""
    return "".join(f'<span class="badge badge-teal" style="margin-right:6px">{n}</span>' for n in names)


def related_publications(pub, pubs, tidx, limit=3):
    """Weight by topic rarity: a shared topic used by fewer total publications
    is a stronger signal than one used everywhere. Score = sum of 1/usage
    over shared topic slugs; ties broken by date recency."""
    my_topics = set(pub.get("topics", []))
    if not my_topics:
        return []
    usage = {s: max(t.get("publication_count", 1), 1) for s, t in tidx.items()}
    scored = []
    for other in pubs:
        if other["id"] == pub["id"]:
            continue
        shared = my_topics & set(other.get("topics", []))
        if not shared:
            continue
        score = sum(1.0 / usage.get(s, 1) for s in shared)
        scored.append((score, other["date"], other))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [o for _, _, o in scored[:limit]]


def citation_block(pub, url):
    return f'{pub["author"]}. &ldquo;{pub["title"]}.&rdquo; <em>Fuence</em>, {pub["date_label"]}. {url}.'


def json_ld(pub, url):
    payload = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": pub["title"],
        "datePublished": pub["date"],
        "author": {"@type": "Organization", "name": pub["author"]},
        "publisher": {"@type": "Organization", "name": "Fuence"},
        "url": url,
        "description": pub["excerpt"],
    }
    return json.dumps(payload, indent=2)


def publication_page_html(pub, pubs, topics_data):
    tidx = topic_index(topics_data)
    sinfo = series_info(pub.get("series", ""), topics_data)
    series_name = sinfo["name"]
    program = sinfo.get("program")
    cls, type_label = TYPE_INFO[pub["type"]]
    url = f'https://www.fuence.com/publications/{pub["id"]}/'
    series_href = f'../../series/{pub.get("series", "")}/index.html'

    breadcrumb_parts = ['<a href="../../index.html">Home</a>']
    if program:
        # Program hub currently only exists for South Asia & Bangladesh (series/bangladesh/)
        program_href = "../../series/bangladesh/index.html" if program == "South Asia & Bangladesh" else "../../series/index.html"
        breadcrumb_parts.append(f'<a href="{program_href}">{program}</a>')
    breadcrumb_parts.append(f'<a href="{series_href}">{series_name}</a>')
    breadcrumb_parts.append(f'<span>{pub["title"]}</span>')
    breadcrumb = " <span style=\"color:var(--text-muted)\">/</span> ".join(breadcrumb_parts)

    topic_badges = core_topic_badges(pub, tidx)

    # Pagefind filter metadata — hidden, uses the FULL topic set (not just
    # Core-status) since filtering doesn't need the same visual restraint
    # as on-page badges. See Segment 4's search design.
    filter_tags = [f'<span data-pagefind-filter="Type:{type_label}"></span>']
    if program:
        filter_tags.append(f'<span data-pagefind-filter="Program:{program}"></span>')
    filter_tags.append(f'<span data-pagefind-filter="Series:{series_name}"></span>')
    for slug in pub.get("topics", []):
        t = tidx.get(slug)
        if t:
            filter_tags.append(f'<span data-pagefind-filter="Topic:{t["name"]}"></span>')
    filter_meta_html = f'<div style="display:none">{"".join(filter_tags)}</div>'
    related = related_publications(pub, pubs, tidx)
    related_html = ""
    if related:
        cards = []
        for r in related:
            r_cls, r_label = TYPE_INFO[r["type"]]
            cards.append(
                f'      <div class="pub-item scroll-reveal">\n'
                f'        <div class="pi-type"><span class="badge {r_cls}">{r_label}</span></div>\n'
                f'        <div class="pi-body">\n'
                f'          <h4><a href="../{r["id"]}/index.html" style="color:inherit;text-decoration:none">{r["title"]}</a></h4>\n'
                f'          <p>{r["excerpt"]}</p>\n'
                f'          <div class="pi-meta"><span class="text-muted">{r["date_label"]}</span></div>\n'
                f'        </div>\n'
                f'      </div>'
            )
        related_html = (
            '<section class="section section-tint">\n'
            '  <div class="container">\n'
            '    <span class="section-label">Related</span>\n'
            '    <h2>Related Publications</h2>\n'
            '    <div class="divider"></div>\n'
            '    <div class="pub-list">\n' + "\n".join(cards) + '\n    </div>\n'
            '  </div>\n'
            '</section>\n'
        )

    read_link = ""
    if pub["link"].startswith(("http://", "https://")):
        read_link = f'<a href="{pub["link"]}" class="btn btn-primary btn-lg" target="_blank">Read the Full Piece on Ghost →</a>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<script>(function(){{var t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t)}})()</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Source+Serif+4:wght@300;400;600&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap">
  <meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{pub["title"]} — Fuence</title>
  <meta name="description" content="{pub["excerpt"]}" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="Fuence" />
  <meta property="og:title" content="{pub["title"]} — Fuence" />
  <meta property="og:description" content="{pub["excerpt"]}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="https://www.fuence.com/assets/img/fuence-logo.jpg" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{pub["title"]} — Fuence" />
  <meta name="twitter:description" content="{pub["excerpt"]}" />
  <meta name="twitter:image" content="https://www.fuence.com/assets/img/fuence-logo.jpg" />
  <link rel="canonical" href="{url}" />
  <link rel="stylesheet" href="../../assets/css/style.css" />
  <link rel="stylesheet" href="../../assets/css/nav.css" />
  <link rel="stylesheet" href="../../assets/css/inner.css" />
  <script type="application/ld+json">
{json_ld(pub, url)}
  </script>
</head>
<body>
<div id="nav-placeholder"></div>
{filter_meta_html}

<section class="page-hero">
  <div class="container">
    <div style="font-size:.82rem;margin-bottom:16px">{breadcrumb}</div>
    <span class="badge {cls}">{type_label}</span>
    {topic_badges}
    <h1 style="margin-top:12px">{pub["title"]}</h1>
    <p class="page-hero-sub">{pub["excerpt"]}</p>
    <div style="font-size:.85rem;color:var(--text-muted);margin-top:10px">{pub["date_label"]} &middot; {pub["author"]}</div>
    <div style="margin-top:24px">{read_link}</div>
  </div>
</section>

<section class="section">
  <div class="container" style="max-width:640px">
    <span class="section-label">Cite This</span>
    <div style="background:var(--bg-tint);border:1px solid var(--border);border-radius:8px;padding:18px 20px;font-size:.9rem;line-height:1.7;margin-top:12px">
      {citation_block(pub, url)}
    </div>
  </div>
</section>

{related_html}
<div id="footer-placeholder"></div>
<script src="../../assets/js/nav.js"></script>
<script src="../../assets/js/main.js"></script>
</body>
</html>
"""


def build_publication_pages(pubs, topics_data):
    out_dir = ROOT / "publications"
    for pub in pubs:
        page_dir = out_dir / pub["id"]
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(publication_page_html(pub, pubs, topics_data))


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
    topics_data = load("topics.json")

    missing_project = [p["id"] for p in pubs if "project" not in p]
    if missing_project:
        raise SystemExit(
            "build_content.py: publications.json entries missing internal "
            f"'project' field (never rendered publicly, but required so "
            f"'series' can't silently drift from real attribution — see "
            f"OPEN-ITEMS CW-2/CW-3): {missing_project}"
        )

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

    for slug in ("genesis-of-a-republic", "republic-unmade", "republic-ascending", "stable-republic"):
        process_file(ROOT / "series" / slug / "index.html", [
            ("series-pubs", build_series_pubs(pubs, slug, depth=2)),
        ])

    build_publication_pages(pubs, topics_data)

    update_log(pubs, milestones)
    print(f"build_content.py: regenerated all content regions + {len(pubs)} publication pages.")


if __name__ == "__main__":
    main()
