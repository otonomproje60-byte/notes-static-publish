#!/usr/bin/env python3
"""
Notes Static Publish - Web Editor API
Flask-based API for note CRUD with auto-rebuild on save.
"""
import os
import json
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = Path(__file__).parent.parent.parent
NOTES_DIR = BASE_DIR / "notes"
DB_PATH = BASE_DIR / "data" / "notes.db"
PUBLISH_SCRIPT = BASE_DIR / "publish.py"

# Ensure directories exist
NOTES_DIR.mkdir(exist_ok=True)
DB_PATH.parent.mkdir(exist_ok=True)

def init_db():
    """Initialize SQLite database with FTS5 for full-text search."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    # FTS5 virtual table for full-text search
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
            title, content, tags, content='notes', content_rowid='id'
        )
    """)
    # Triggers to keep FTS in sync
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
            INSERT INTO notes_fts(rowid, title, content, tags) VALUES (new.id, new.title, new.content, new.tags);
        END
    """)
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN
            INSERT INTO notes_fts(notes_fts, rowid, title, content, tags) VALUES ('delete', old.id, old.title, old.content, old.tags);
        END
    """)
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS notes_au AFTER UPDATE ON notes BEGIN
            INSERT INTO notes_fts(notes_fts, rowid, title, content, tags) VALUES ('delete', old.id, old.title, old.content, old.tags);
            INSERT INTO notes_fts(rowid, title, content, tags) VALUES (new.id, new.title, new.content, new.tags);
        END
    """)
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def rebuild_static_site():
    """Trigger static site rebuild."""
    try:
        result = subprocess.run(
            ["python3", str(PUBLISH_SCRIPT)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Build timeout"
    except Exception as e:
        return False, "", str(e)

@app.route("/healthz")
def healthz():
    return jsonify({"status": "healthy", "service": "notes-static-publish-api"})

@app.route("/api/notes", methods=["GET"])
def list_notes():
    """List all notes with optional search."""
    query = request.args.get("q", "").strip()
    tag = request.args.get("tag", "").strip()
    
    conn = get_db()
    try:
        if query:
            # Full-text search
            cursor = conn.execute("""
                SELECT n.id, n.slug, n.title, n.tags, n.created_at, n.updated_at,
                       snippet(notes_fts, 1, '<mark>', '</mark>', '...', 32) as snippet
                FROM notes n
                JOIN notes_fts ON notes_fts.rowid = n.id
                WHERE notes_fts MATCH ?
                ORDER BY n.updated_at DESC
            """, (query,))
        elif tag:
            cursor = conn.execute("""
                SELECT id, slug, title, tags, created_at, updated_at
                FROM notes
                WHERE tags LIKE ?
                ORDER BY updated_at DESC
            """, (f"%{tag}%",))
        else:
            cursor = conn.execute("""
                SELECT id, slug, title, tags, created_at, updated_at
                FROM notes
                ORDER BY updated_at DESC
            """)
        
        notes = [dict(row) for row in cursor.fetchall()]
        return jsonify({"notes": notes, "count": len(notes)})
    finally:
        conn.close()

@app.route("/api/notes/<slug>", methods=["GET"])
def get_note(slug):
    """Get a single note by slug."""
    conn = get_db()
    try:
        cursor = conn.execute("SELECT * FROM notes WHERE slug = ?", (slug,))
        note = cursor.fetchone()
        if not note:
            return jsonify({"error": "Note not found"}), 404
        return jsonify(dict(note))
    finally:
        conn.close()

@app.route("/api/notes", methods=["POST"])
def create_note():
    """Create a new note."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    title = data.get("title", "").strip()
    content = data.get("content", "")
    tags = data.get("tags", [])
    
    if not title:
        return jsonify({"error": "Title is required"}), 400
    
    # Generate slug from title
    import re
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    if not slug:
        slug = "untitled"
    
    # Ensure unique slug
    conn = get_db()
    try:
        cursor = conn.execute("SELECT COUNT(*) as c FROM notes WHERE slug LIKE ?", (f"{slug}%",))
        count = cursor.fetchone()["c"]
        if count > 0:
            slug = f"{slug}-{count + 1}"
        
        now = datetime.utcnow().isoformat()
        tags_str = ",".join(tags) if tags else ""
        
        conn.execute("""
            INSERT INTO notes (slug, title, content, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (slug, title, content, tags_str, now, now))
        conn.commit()
        
        note_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        # Also write markdown file for portability
        md_content = f"""---
title: {title}
date: {now.split('T')[0]}
tags: {tags_str}
---

{content}
"""
        (NOTES_DIR / f"{slug}.md").write_text(md_content, encoding="utf-8")
        
        # Trigger rebuild
        success, stdout, stderr = rebuild_static_site()
        
        return jsonify({
            "id": note_id,
            "slug": slug,
            "title": title,
            "content": content,
            "tags": tags,
            "created_at": now,
            "updated_at": now,
            "rebuild": {"success": success, "stdout": stdout, "stderr": stderr}
        }), 201
    finally:
        conn.close()

@app.route("/api/notes/<slug>", methods=["PUT"])
def update_note(slug):
    """Update an existing note."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    title = data.get("title", "").strip()
    content = data.get("content", "")
    tags = data.get("tags", [])
    
    if not title:
        return jsonify({"error": "Title is required"}), 400
    
    now = datetime.utcnow().isoformat()
    tags_str = ",".join(tags) if tags else ""
    
    conn = get_db()
    try:
        cursor = conn.execute("SELECT id FROM notes WHERE slug = ?", (slug,))
        note = cursor.fetchone()
        if not note:
            return jsonify({"error": "Note not found"}), 404
        
        note_id = note["id"]
        
        conn.execute("""
            UPDATE notes SET title = ?, content = ?, tags = ?, updated_at = ?
            WHERE id = ?
        """, (title, content, tags_str, now, note_id))
        conn.commit()
        
        # Update markdown file
        md_content = f"""---
title: {title}
date: {now.split('T')[0]}
tags: {tags_str}
---

{content}
"""
        (NOTES_DIR / f"{slug}.md").write_text(md_content, encoding="utf-8")
        
        # Trigger rebuild
        success, stdout, stderr = rebuild_static_site()
        
        return jsonify({
            "id": note_id,
            "slug": slug,
            "title": title,
            "content": content,
            "tags": tags,
            "updated_at": now,
            "rebuild": {"success": success, "stdout": stdout, "stderr": stderr}
        })
    finally:
        conn.close()

@app.route("/api/notes/<slug>", methods=["DELETE"])
def delete_note(slug):
    """Delete a note."""
    conn = get_db()
    try:
        cursor = conn.execute("SELECT id FROM notes WHERE slug = ?", (slug,))
        note = cursor.fetchone()
        if not note:
            return jsonify({"error": "Note not found"}), 404
        
        note_id = note["id"]
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        
        # Remove markdown file
        md_file = NOTES_DIR / f"{slug}.md"
        if md_file.exists():
            md_file.unlink()
        
        # Trigger rebuild
        success, stdout, stderr = rebuild_static_site()
        
        return jsonify({
            "deleted": True,
            "slug": slug,
            "rebuild": {"success": success, "stdout": stdout, "stderr": stderr}
        })
    finally:
        conn.close()

@app.route("/api/tags", methods=["GET"])
def list_tags():
    """Get all unique tags with counts."""
    conn = get_db()
    try:
        cursor = conn.execute("SELECT tags FROM notes WHERE tags != ''")
        all_tags = {}
        for row in cursor.fetchall():
            for tag in row["tags"].split(","):
                tag = tag.strip()
                if tag:
                    all_tags[tag] = all_tags.get(tag, 0) + 1
        return jsonify({"tags": [{"name": k, "count": v} for k, v in sorted(all_tags.items())]})
    finally:
        conn.close()

@app.route("/api/search", methods=["GET"])
def search_notes():
    """Full-text search across notes."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"results": []})
    
    conn = get_db()
    try:
        cursor = conn.execute("""
            SELECT n.id, n.slug, n.title, n.tags, n.updated_at,
                   snippet(notes_fts, 1, '<mark>', '</mark>', '...', 64) as snippet
            FROM notes n
            JOIN notes_fts ON notes_fts.rowid = n.id
            WHERE notes_fts MATCH ?
            ORDER BY n.updated_at DESC
            LIMIT 20
        """, (query,))
        results = [dict(row) for row in cursor.fetchall()]
        return jsonify({"results": results, "query": query})
    finally:
        conn.close()

@app.route("/api/rebuild", methods=["POST"])
def manual_rebuild():
    """Manually trigger static site rebuild."""
    success, stdout, stderr = rebuild_static_site()
    return jsonify({"success": success, "stdout": stdout, "stderr": stderr})

@app.route("/")
def web_editor():
    """Serve the web editor UI."""
    return send_from_directory(BASE_DIR / "source" / "web", "index.html")

@app.route("/app.js")
def web_app_js():
    """Serve the web editor JavaScript."""
    return send_from_directory(BASE_DIR / "source" / "web", "app.js")

@app.route("/styles.css")
def web_styles_css():
    """Serve the web editor styles."""
    return send_from_directory(BASE_DIR / "source" / "web", "styles.css")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=False)