#!/usr/bin/env python3
"""
Static site publishing pipeline for markdown notes.
Proof-of-concept: markdown files -> HTML -> static site.
"""
import os
import sys
import json
from pathlib import Path
from markdown_it import MarkdownIt
from jinja2 import Environment, FileSystemLoader

# Setup
NOTES_DIR = Path("notes")
OUTPUT_DIR = Path("dist")
TEMPLATES_DIR = Path("templates")

md = MarkdownIt()
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def read_notes():
    """Read all markdown files from notes directory."""
    notes = []
    for md_file in sorted(NOTES_DIR.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        # Parse frontmatter (simple YAML-like)
        frontmatter = {}
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                for line in parts[1].strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        frontmatter[k.strip()] = v.strip()
                body = parts[2].strip()
        
        html = md.render(body)
        notes.append({
            "slug": md_file.stem,
            "title": frontmatter.get("title", md_file.stem.replace("-", " ").title()),
            "date": frontmatter.get("date", ""),
            "tags": [t.strip() for t in frontmatter.get("tags", "").split(",")] if frontmatter.get("tags") else [],
            "html": html,
            "raw": body,
        })
    return notes

def build_index(notes):
    """Build index page."""
    template = env.get_template("index.html")
    return template.render(notes=notes)

def build_note(note, all_notes):
    """Build individual note page."""
    template = env.get_template("note.html")
    return template.render(note=note, all_notes=all_notes)

def build_tag_pages(notes):
    """Build tag index pages."""
    tags = {}
    for note in notes:
        for tag in note["tags"]:
            if tag not in tags:
                tags[tag] = []
            tags[tag].append(note)
    
    template = env.get_template("tag.html")
    for tag, tag_notes in tags.items():
        yield tag, template.render(tag=tag, notes=tag_notes)

def main():
    # Clean output - remove contents but keep directory (may be mounted)
    import shutil
    if OUTPUT_DIR.exists():
        for item in OUTPUT_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    else:
        OUTPUT_DIR.mkdir(parents=True)
    
    # Read notes
    notes = read_notes()
    print(f"Found {len(notes)} notes")
    
    # Build index
    index_html = build_index(notes)
    (OUTPUT_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print("Built index.html")
    
    # Build notes
    for note in notes:
        note_html = build_note(note, notes)
        (OUTPUT_DIR / f"{note['slug']}.html").write_text(note_html, encoding="utf-8")
        print(f"Built {note['slug']}.html")
    
    # Build tag pages
    for tag, tag_html in build_tag_pages(notes):
        (OUTPUT_DIR / f"tag-{tag}.html").write_text(tag_html, encoding="utf-8")
        print(f"Built tag-{tag}.html")
    
    # Copy static assets
    static_src = Path("static")
    if static_src.exists():
        shutil.copytree(static_src, OUTPUT_DIR / "static")
    
    print(f"\n✅ Static site built in {OUTPUT_DIR}/")
    print(f"   Open {OUTPUT_DIR / 'index.html'} in browser")

if __name__ == "__main__":
    main()
