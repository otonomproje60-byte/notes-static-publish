---
title: System Architecture
date: 2026-09-24
tags: architecture, technical
---

# System Architecture

## Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Markdown Files │────▶│  Build Pipeline │────▶│  Static HTML    │
│  (source)       │     │  (Python)       │     │  (dist/)        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  SQLite Index   │
                       │  (FTS5 search)  │
                       └─────────────────┘
```

## Components

### 1. Markdown Files (Source of Truth)
- Plain `.md` files in `notes/`
- YAML frontmatter for metadata
- Portable, version-controllable, editable anywhere

### 2. Build Pipeline (`publish.py`)
- **markdown-it-py**: Fast, compliant CommonMark parser
- **Jinja2**: Template engine for HTML generation
- **SQLite FTS5**: Full-text search index (planned)

### 3. Static Output (`dist/`)
- `index.html` - All notes list
- `{slug}.html` - Individual notes
- `tag-{tag}.html` - Tag index pages
- `static/` - CSS, JS, images

### 4. Optional: Web Editor (Future)
- Flask/FastAPI backend
- SQLite for note storage + metadata
- Auto-rebuild on save
- Git integration

## Data Flow

```
Edit markdown → Git commit → CI/CD → Build → Deploy to Pages
                    ↓
              SQLite index updated
                    ↓
              Search API available
```

## Deployment Targets

| Platform | Cost | SSL | Custom Domain | Notes |
|----------|------|-----|---------------|-------|
| GitHub Pages | Free | ✅ | ✅ | Native Jekyll, but works with any static |
| Netlify | Free tier | ✅ | ✅ | Drag & drop, forms, functions |
| Cloudflare Pages | Free | ✅ | ✅ | Fast, unlimited bandwidth |
| VPS + Nginx | $5/mo | Manual | ✅ | Full control |
| S3 + CloudFront | ~$1/mo | ✅ | ✅ | Scalable, pay per use |
