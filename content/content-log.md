# Fuence Website — Content Log

One line per item added to the site, regardless of which path was used.
Format and workflow: see
`/home/elijo/futura-genesis/fuence-website-content-system.md`.

- **systematic** rows are appended automatically by `tools/build_content.py`
  for any `id` in `content/publications.json` / `content/milestones.json`
  not yet logged here.
- **pipeline** rows are appended automatically the same way, for items
  synced from the publishing pipeline's dispatch output by
  `tools/sync_dispatch.py` (Stage 2) — `publications.json` entries carry
  `"source": "pipeline"`, which sets the Method column here.
- **manual** rows are appended by hand after a direct HTML edit (no JSON) —
  list every file/section touched in the Location column.

| Date | Method | ID | Type | Series | Location |
|---|---|---|---|---|---|
| 2026-06-12 | systematic | bd-shrinking-democratic-space-2025 | report | bangladesh | publications.json |
| 2026-06-12 | systematic | china-influence-playbook-south-asia-2025 | report | india | publications.json |
| 2026-06-12 | systematic | india-neutral-eastern-flank-2025 | oped | india | publications.json |
| 2026-06-12 | systematic | international-silence-bangladesh-2025 | oped | bangladesh | publications.json |
| 2026-06-12 | systematic | petitions-political-tools-2025 | brief | bangladesh | publications.json |
| 2026-06-12 | systematic | website-launch-2025 | milestone | — | milestones.json |
| 2026-06-21 | systematic | sonar-bangla-india-investment-2026 | oped | india | publications.json |
| 2026-06-21 | systematic | 1971-unfinished-promise-2026 | report | bangladesh | publications.json |
| 2026-06-21 | systematic | who-is-jamaat-2026 | report | bangladesh | publications.json |
| 2026-06-21 | systematic | project-ukraine-for-india-2026 | report | bangladesh | publications.json |
| 2026-06-21 | systematic | pakistan-bay-of-bengal-2026 | brief | india | publications.json |
