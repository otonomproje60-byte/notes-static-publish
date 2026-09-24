# Outreach Posts for Notes Static Publish (Ready for Posting)

## Correct Demo URLs:
- **API + Web Editor:** http://77.90.53.243:5001
- **Web Editor UI:** http://77.90.53.243:5001/
- **Static Site:** http://77.90.53.243:8080/
- **Healthcheck:** http://77.90.53.243:5001/healthz
- **GitHub:** (not yet created - will create before posting)

---

## r/selfhosted Post

**Title:** I built a self-hosted Obsidian Publish alternative with a web editor (Python + SQLite, ~2 min deploy)

**Body:**

Hey r/selfhosted,

I've been looking for a way to publish my Markdown notes as a static site without paying $8/mo for Obsidian Publish or maintaining a complex Hugo/Quartz/Jekyll setup with separate build pipelines. So I built one:

**What it is:**
- Web-based Markdown editor with live preview (write in browser, no desktop app needed)
- One-click publish — every save automatically rebuilds a static HTML site
- Python/Flask + SQLite (FTS5 full-text search)
- Docker Compose deploy in ~2 minutes
- ~50 MB Docker image, ~20 MB RAM idle
- Notes stored as portable .md files with frontmatter
- Zero external dependencies — no Redis, PostgreSQL, Node.js, or build tools

**Live demo (web editor):** http://77.90.53.243:5001/
**Live demo (published static site):** http://77.90.53.243:8080/
**GitHub:** [will add before posting]

**Deploy:**
```bash
git clone [github-url]
cd notes-static-publish
docker compose up -d
```

**Known limitations (MVP):**
- Single-user (no auth/multi-user)
- No image upload in editor (Markdown image syntax works if images in /static)
- Static site is basic HTML (no JS interactivity beyond navigation)
- No custom domain built-in (works via reverse proxy)
- Rebuild is synchronous (blocks API response briefly)

**Why I built this:**
Obsidian Publish = $8/mo + vendor lock-in. Quartz/Hugo/Jekyll = no web editor, separate build step, Node.js/Go toolchain. Trilium/SiYuan/Outline = great editors but no seamless static publish. I wanted: write in browser → instant static site → runs on a $3 VPS.

Looking for feedback:
- Would you use this over Obsidian Publish / Quartz / Trilium for personal notes?
- What features are dealbreakers?
- Any security concerns with the current approach?

---

## r/webdev Post

**Title:** Self-hosted Markdown notes + static site publish in 300 lines of Python (Flask + SQLite FTS5, Docker)

**Body:**

Built this because every existing option was either:
- SaaS with monthly fees (Obsidian Publish, Notion)
- No web editor — requires local dev setup + build pipeline (Quartz, Hugo, Jekyll)
- Great editor but no static publish (Trilium, SiYuan, Outline)
- Heavy stacks requiring Node.js/Go + PostgreSQL + Redis

**Stack:** Python 3.12 + Flask + SQLite FTS5 + Gunicorn + Docker
**Deploy:** `docker compose up -d` (2 min)
**Size:** ~50 MB image, ~20 MB RAM
**Architecture:** Single container runs both the API/editor (port 5001) and static file server (port 8080)

**Demo (editor):** http://77.90.53.243:5001/
**Demo (published site):** http://77.90.53.243:8080/
**Source:** [will add before posting]

Main differentiator: web editor + instant static publish in one lightweight container. SQLite FTS5 for search. Notes as portable .md files.

Trade-offs: single-user, basic static HTML output, no image upload yet, synchronous rebuild.

Feedback welcome — especially from people who've tried Obsidian Publish, Quartz, or Trilium.

---

## Hacker News "Show HN" Post

**Title:** Show HN: Notes Static Publish – Self-hosted Markdown editor with instant static site publish

**URL:** [will add GitHub URL before posting]

**Text (optional):**
Built this after realizing the gap: Obsidian Publish costs $8/mo, Quartz/Hugo need local builds, Trilium/SiYuan don't publish static sites.

Stack: Python 3.12 + Flask + SQLite FTS5
- ~50 MB Docker image
- ~20 MB RAM idle
- Single SQLite file + .md files for persistence
- Full-text search across title, content, tags
- Tag system with tag pages
- One-click publish on every save

Live editor: http://77.90.53.243:5001/
Live published site: http://77.90.53.243:8080/

Known gaps: single-user, basic HTML output, no image upload, no custom domains (reverse proxy works), synchronous rebuild.

Happy to discuss the architecture, SQLite FTS5 search implementation, or self-hosting trade-offs.

---

## Telegram Channel Post

**Message:**
🚀 **New self-hosted tool: Notes Static Publish**

A web-based Markdown editor that instantly publishes your notes as a static HTML site. Think: Obsidian Publish but self-hosted, free, and with a browser editor.

✅ Web editor with live preview
✅ One-click auto-publish on save
✅ Full-text search (SQLite FTS5)
✅ Tags + tag pages
✅ Portable .md files with frontmatter
✅ Single Docker container (~50MB, ~20MB RAM)
✅ Zero external deps (no Redis/PostgreSQL/Node)

🔗 **Try it:** http://77.90.53.243:5001/ (editor) → http://77.90.53.243:8080/ (published site)
📦 **Deploy:** `docker compose up -d` (2 min)

Looking for feedback from the self-hosted community. Would you use this over Obsidian Publish / Quartz / Trilium?

---

## Posting Checklist

- [ ] Create GitHub repository
- [ ] Push source code to GitHub
- [ ] Update GitHub URLs in this file
- [ ] Post to r/selfhosted
- [ ] Post to r/webdev  
- [ ] Submit to Hacker News (Show HN)
- [ ] Post to Telegram channel
- [ ] Monitor for comments/feedback
- [ ] Record responses in Factory memory

## Tracking
- GitHub repo created at: [TIMESTAMP]
- GitHub URL: [URL]
- Posted at: [TIMESTAMP]
- r/selfhosted URL: [URL]
- r/webdev URL: [URL]
- HN URL: [URL]
- Telegram message ID: [ID]
- Initial feedback summary: [SUMMARY]