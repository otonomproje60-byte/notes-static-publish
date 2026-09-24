---
title: Getting Started with Static Notes
date: 2026-09-24
tags: tutorial, getting-started
---

# Getting Started

Welcome to **static notes publishing**! This is a proof-of-concept for a lightweight, Python-based notes system that:

- Stores notes as **markdown files on disk** (your source of truth)
- Uses **SQLite for indexing and search** (fast queries)
- Publishes to a **static HTML site** (free hosting on GitHub Pages, Netlify, etc.)

## Why This Approach?

| Feature | Obsidian Publish | This System |
|---------|-----------------|-------------|
| Cost | $8/month | **Free** |
| Hosting | Their servers | **Your choice** (GitHub Pages, Netlify, VPS) |
| Source format | Proprietary | **Plain markdown files** |
| Web editor | ✅ | Planned |
| Mobile apps | ✅ | Browser-based |

## Quick Start

1. Create `.md` files in the `notes/` directory
2. Run `python publish.py`
3. Deploy the `dist/` folder anywhere

## Markdown Features

- **Headers** (# ## ###)
- **Bold** and *italic*
- **Code blocks** with syntax highlighting
- **Tables**
- **Blockquotes**
- **Links** and images

```python
def hello():
    print("Hello, static notes!")
```

> This is a blockquote. It works beautifully.

| Feature | Status |
|---------|--------|
| Markdown parsing | ✅ |
| Frontmatter | ✅ |
| Tag pages | ✅ |
| Static output | ✅ |

## Next Steps

- Add a web-based editor
- Implement SQLite full-text search
- Add Git auto-commit on save
- Build Docker image for easy deployment
