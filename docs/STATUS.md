# Migration status (2026-11-15)

Completed by GitHub Actions:
- Imported 28 public HTML pages and 139 files to this repository.
- Preserved original file paths for previously external-facing pages and PDFs.
- Stored original HTML under `site/source-original/` and a SHA-256 inventory under `site/IMPORT_MANIFEST.json`.
- Repaired genealogy iframe navigation and updated source-to-local links.
- Published a searchable complete inventory at `/legacy-index.html`.

Known source errors: bs4/bootstrap-theme.min.css, davoud2/davoud2.css (original server returned 404).

Next: visual testing, verify direct links, review living people's private data and image rights, build structured family graph, validate SEO/redirects, check DNS/email records, and only then cut over afsharnaderi.com.

**DO NOT change DNS or add CNAME during staging.**