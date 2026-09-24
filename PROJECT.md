# Notes Static Publish Project

## Project Name
Notes Static Publish

## What it does
A self-hosted, web-based Markdown notes editor with one-click static site publishing. Built with Python/Flask, SQLite (FTS5 search), and Docker. Write notes in a browser editor, save → automatically rebuilds a static HTML site served via lightweight HTTP server.

## Demo URLs
- **API + Web Editor:** http://77.90.53.243:5001
- **Web Editor UI:** http://77.90.53.243:5001/
- **Static Site:** http://77.90.53.243:8080/
- **Healthcheck:** http://77.90.53.243:5001/healthz
- **GitHub:** (not yet created)

## Test Status
- ✅ API endpoints functional: GET/POST /api/notes, GET /api/notes/<slug>, GET /api/tags, GET /api/search, POST /api/rebuild
- ✅ Web editor UI loads and can create/edit/delete notes
- ✅ Auto-rebuild on save: creates/updates notes → triggers publish.py → updates dist/
- ✅ Static site served on port 8080 with generated HTML
- ✅ Full-text search via SQLite FTS5
- ✅ Markdown files persisted to /notes directory for portability
- ✅ Docker healthcheck passing (endpoint: /healthz)
- ✅ Container healthy and publicly accessible

## Deployment Status
Deployed via Docker Compose on public VDS (77.90.53.243). Two services in one container:
- Flask API + web editor on port 5001
- Python http.server serving static files from /app/dist on port 8080

## Architecture
```
┌─────────────────────────────────────────────────────────────┐
│  Single Container (Python 3.12-slim, ~50MB, ~20MB RAM)     │
├─────────────────────────────────────────────────────────────┤
│  Flask API (port 5001)                                      │
│  ├── GET/POST /api/notes          - CRUD + list            │
│  ├── GET /api/notes/<slug>        - Single note            │
│  ├── GET /api/tags                - Tag cloud with counts  │
│  ├── GET /api/search?q=...        - FTS5 full-text search  │
│  ├── POST /api/rebuild            - Manual rebuild trigger │
│  ├── GET /                        - Web editor UI          │
│  ├── GET /app.js                  - Editor JavaScript      │
│  └── GET /styles.css              - Editor styles          │
│  http.server (port 8080)                                      │
│  └── Serves /app/dist/ (static HTML)                        │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                   │
│  ├── SQLite + FTS5 at /app/data/notes.db                     │
│  ├── Markdown files at /app/notes/*.md                       │
│  └── Static output at /app/dist/                             │
└─────────────────────────────────────────────────────────────┘
```

## Key Features
- **Web-based Markdown editor** with live preview (no desktop app needed)
- **One-click publish** - every save triggers automatic static site rebuild
- **Full-text search** via SQLite FTS5 across title, content, tags
- **Tag system** with tag pages and tag cloud
- **Markdown portability** - notes stored as .md files with frontmatter
- **Zero external dependencies** - SQLite only, no Redis/PostgreSQL/MySQL
- **Lightweight** - ~50MB image, ~20MB RAM idle, ARM native
- **Simple deploy** - `docker compose up -d`

## Known Limitations
- Single-user (no auth/multi-user)
- No image upload in editor (Markdown image syntax works if images in /static)
- Static site is basic HTML (no JS interactivity beyond navigation)
- No custom domain built-in (works via reverse proxy)
- Rebuild is synchronous (blocks API response briefly)

## Suggested Domain Names
- notes-static.com
- static-notes.io
- markdown-publish.dev
- simple-notes.app
- (awaiting human purchase after commercial validation)

## Commercial Validation Status
**Technical MVP: ✅ COMPLETE** (full stack working, deployed, smoke-tested)
**Commercial Validation: ⏳ NOT STARTED** (need outreach, community feedback)

## Next Steps
- Create GitHub repository
- Prepare outreach posts (Reddit, HN, Telegram) - similar to url-shortener approach
- Monitor for responses on all channels
- Record responses in Factory memory
- Track willingness signals: GitHub stars, issues, "I deployed this" comments
- Monitor public demo for abuse/spam patterns
- Validate SEO keyword demand for "self hosted notes publish", "free Obsidian Publish alternative", "markdown static site generator web editor"
- Analyze competitive differentiation vs. Obsidian Publish (paid), Quartz/Hugo/Jekyll (no web editor), Trilium/SiYuan (no seamless publish)
- Complete Commercial Validation Gate decision: BUILD / PIVOT / DISCARD based on accumulated evidence

## Differentiation vs Competitors
| Tool | Web Editor | Static Publish | Self-Hosted | Free | SQLite | RAM |
|------|------------|----------------|-------------|------|--------|-----|
| **Notes Static Publish** | ✅ | ✅ One-click | ✅ | ✅ | ✅ | ~20MB |
| Obsidian Publish | ✅ | ✅ | ❌ (SaaS) | ❌ ($8/mo) | - | - |
| Quartz/Hugo/Jekyll | ❌ | ✅ | ✅ | ✅ | ❌ | - |
| Trilium Notes | ✅ | ❌ | ✅ | ✅ | ❌ (Node) | ~100MB |
| SiYuan | ✅ | ❌ | ✅ | ✅ | ❌ (Go) | ~100MB |
| Outline | ✅ | ❌ | ✅ | ✅ | ❌ (PostgreSQL) | ~200MB |

## Unique Value Proposition
"The only self-hosted tool combining: web Markdown editor + instant static site publish + SQLite simplicity + zero external deps + runs on a $3 VPS."