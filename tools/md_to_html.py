#!/usr/bin/env python3
"""Convert a dispatched website-article/website-publication markdown body
to an HTML fragment for Tier B hosted pages.

Stage 2, Tier B (see /home/elijo/futura-genesis/fuence-website-stage2-plan.md §3b).

Supports exactly the subset produced by the `website-article.md` /
`website-publication.md` platform templates (~/platform-templates/):
  - Strips the leading `# Title` line and the italic `*dek*` line (if present)
  - Strips the trailing `---` / `**Suggested ...**` metadata block
  - `## Heading` -> <h2>
  - Runs of `- item` lines -> <ul><li>...</li></ul>
  - Blank-line-separated paragraphs -> <p>, with **bold**/*italic* -> <strong>/<em>

Anything else (e.g. numbered lists in "Policy Recommendations") falls
through to a plain escaped <p> per line — fail-safe, not pretty.

Usage: import and call body_html(markdown_text) -> str (HTML fragment)
"""
import html
import re

HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$")
BULLET_RE = re.compile(r"^[-*]\s+(.*)$")
DEK_RE = re.compile(r"^\*[^*].*\*$")
TRAILING_META_RE = re.compile(r"\n-{3,}\s*\n\*\*Suggested", re.IGNORECASE)


def _inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def _strip_title_and_dek(lines):
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].lstrip().startswith("# "):
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i < len(lines) and DEK_RE.match(lines[i].strip()):
            i += 1
    return lines[i:]


def _strip_trailing_metadata(text):
    m = TRAILING_META_RE.search(text)
    return text[: m.start()] if m else text


def body_html(text, indent="      "):
    text = _strip_trailing_metadata(text)
    lines = _strip_title_and_dek(text.splitlines())

    parts = []
    para, items = [], []

    def flush_para():
        if para:
            parts.append(f"{indent}<p>{_inline(' '.join(para))}</p>")
            para.clear()

    def flush_list():
        if items:
            li = "\n".join(f"{indent}  <li>{_inline(t)}</li>" for t in items)
            parts.append(f"{indent}<ul>\n{li}\n{indent}</ul>")
            items.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_para()
            flush_list()
            continue

        heading = HEADING_RE.match(stripped)
        if heading:
            flush_para()
            flush_list()
            parts.append(f"{indent}<h2>{_inline(heading.group(1))}</h2>")
            continue

        bullet = BULLET_RE.match(stripped)
        if bullet:
            flush_para()
            items.append(bullet.group(1))
            continue

        flush_list()
        para.append(stripped)

    flush_para()
    flush_list()
    return "\n".join(parts)
