# Migration and deployment plan — Afshar Naderi

**Stage:** Initial redesign and staging. Never change DNS until the new site is complete and approved.

## What is live in this repository
- Responsive RTL landing page with a conceptual tree illustration.
- Search/filter interface for eight public source links.
- Branch-name overview with no asserted kinship relationships.
- Static GitHub Actions deployment from `site/` to project Pages URL.
- Original PDFs and archival media are NOT copied yet.

## Pages staging activation
1. Open https://github.com/nimania/afsharnaderi/settings/pages
2. Choose **Source → GitHub Actions**.
3. Visit Actions and ensure `Deploy staging website to GitHub Pages` succeeds.
4. Preview at https://nimania.github.io/afsharnaderi/ .

## Original URL inventory from the existing homepage (partial)
| Old path | Content | Migrated? |
|---|---|---|
| / | Introduction | Summary only |
| /tabaar/tabaar1.html | Genealogy diagram | No |
| /docs/shajareh.pdf | Genealogy PDF | No |
| /docs/kashkoul.html | Birth records | No |
| /docs/ismail_memo.pdf | Family history PDF | No |
| /ismail/ismail.html | Ismail Mirza | No |
| /davoud2/davoudm2.html | Davoud Mirza II | No |
| /drghan/drghan.html | Dr Gholamreza Afshar Naderi | No |
| /drnader/drnader.html | Dr Nader Afshar Naderi | No |

This is not a complete crawl.

## Before DNS cutover
- [ ] Export complete original site, images, subpages, PDFs, scripts and other assets, store backups separately.
- [ ] Record checksums for original documents, provenance and archival metadata.
- [ ] Inventory nested paths and preserve URL addresses wherever possible.
- [ ] Audit private data of living people and asset publication rights.
- [ ] Convert verified information to accessible records; do not invent kinship.
- [ ] Validate all documents, links, mobile layouts, loading, alt text and accessibility.
- [ ] Prepare explicit redirect mapping for paths that must change.
- [ ] Remove noindex and set correct canonical URLs only once production is approved.
- [ ] Back up current DNS records, including mail MX and SPF/DKIM/DMARC TXT records.
- [ ] Configure apex and www per GitHub Pages guidance, verify domain and HTTPS.
- [ ] Monitor 404s, Search Console and certificate issuance; retain original hosting for rollback.

Do not add a CNAME file or configure the production domain at this stage.
