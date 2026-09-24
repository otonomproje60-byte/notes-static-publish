/**
 * Notes Static Publish - Web Editor Frontend Logic
 * Handles note CRUD, markdown preview, search, and publishing
 */

const API_BASE = '/api';
let currentNoteSlug = null;
let notesCache = [];
let isDirty = false;
let saveDebounce = null;

// DOM Elements
const elements = {
    noteSelect: document.getElementById('note-select'),
    searchInput: document.getElementById('search-input'),
    notesList: document.getElementById('notes-list'),
    editor: document.getElementById('editor'),
    preview: document.getElementById('preview'),
    noteTitle: document.getElementById('note-title'),
    noteTags: document.getElementById('note-tags'),
    btnSave: document.getElementById('btn-save'),
    btnPublish: document.getElementById('btn-publish'),
    wordCount: document.getElementById('word-count'),
    charCount: document.getElementById('char-count'),
    saveStatus: document.getElementById('save-status'),
    sidebar: document.getElementById('sidebar'),
};

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadNotes();
    setupEventListeners();
    setupMarkdownPreview();
    updateCounts();
});

// Load all notes from API
async function loadNotes(searchQuery = '', tag = '') {
    try {
        const params = new URLSearchParams();
        if (searchQuery) params.set('q', searchQuery);
        if (tag) params.set('tag', tag);

        const response = await fetch(`${API_BASE}/notes?${params}`);
        const data = await response.json();

        if (data.notes) {
            notesCache = data.notes;
            renderNotesList(data.notes);
            updateNoteSelect(data.notes);
        }
    } catch (error) {
        console.error('Failed to load notes:', error);
        showSaveStatus('Failed to load notes', 'error');
    }
}

// Render notes in sidebar
function renderNotesList(notes) {
    elements.notesList.innerHTML = notes.map(note => `
        <li class="note-item${note.slug === currentNoteSlug ? ' active' : ''}" data-slug="${note.slug}">
            <div class="note-item-title">${escapeHtml(note.title)}</div>
            <div class="note-item-meta">
                <span>${formatDate(note.updated_at)}</span>
                <div class="note-item-tags">
                    ${note.tags ? note.tags.split(',').map(t => `<span class="note-tag">${escapeHtml(t.trim())}</span>`).join('') : ''}
                </div>
            </div>
        </li>
    `).join('');

    // Add click handlers
    elements.notesList.querySelectorAll('.note-item').forEach(item => {
        item.addEventListener('click', () => loadNote(item.dataset.slug));
    });
}

// Update dropdown select
function updateNoteSelect(notes) {
    const currentValue = elements.noteSelect.value;
    elements.noteSelect.innerHTML = '<option value="">+ New Note</option>' +
        notes.map(note => `<option value="${note.slug}"${note.slug === currentValue ? ' selected' : ''}>${escapeHtml(note.title)}</option>`).join('');
}

// Load a single note
async function loadNote(slug) {
    if (isDirty && !confirm('You have unsaved changes. Discard?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/notes/${slug}`);
        const note = await response.json();

        if (note.error) {
            showSaveStatus(note.error, 'error');
            return;
        }

        currentNoteSlug = slug;
        elements.editor.value = note.content || '';
        elements.noteTitle.value = note.title || '';
        elements.noteTags.value = note.tags || '';
        elements.btnSave.disabled = false;

        // Update active state in list
        elements.notesList.querySelectorAll('.note-item').forEach(item => {
            item.classList.toggle('active', item.dataset.slug === slug);
        });
        elements.noteSelect.value = slug;

        updatePreview();
        updateCounts();
        isDirty = false;
        showSaveStatus('Loaded', 'saved');
    } catch (error) {
        console.error('Failed to load note:', error);
        showSaveStatus('Failed to load note', 'error');
    }
}

// Create new note
function newNote() {
    if (isDirty && !confirm('You have unsaved changes. Discard?')) {
        return;
    }

    currentNoteSlug = null;
    elements.editor.value = '';
    elements.noteTitle.value = '';
    elements.noteTags.value = '';
    elements.btnSave.disabled = false;
    elements.noteSelect.value = '';
    elements.notesList.querySelectorAll('.note-item').forEach(item => item.classList.remove('active'));
    updatePreview();
    updateCounts();
    isDirty = false;
    showSaveStatus('New note', 'saved');
    elements.noteTitle.focus();
}

// Save current note (create or update)
async function saveNote() {
    const title = elements.noteTitle.value.trim();
    const content = elements.editor.value;
    const tags = elements.noteTags.value.split(',').map(t => t.trim()).filter(Boolean);

    if (!title) {
        showSaveStatus('Title is required', 'error');
        elements.noteTitle.focus();
        return;
    }

    showSaveStatus('Saving...', 'saving');
    elements.btnSave.disabled = true;

    try {
        const method = currentNoteSlug ? 'PUT' : 'POST';
        const url = currentNoteSlug ? `${API_BASE}/notes/${currentNoteSlug}` : `${API_BASE}/notes`;

        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content, tags })
        });

        const result = await response.json();

        if (result.error) {
            showSaveStatus(result.error, 'error');
            elements.btnSave.disabled = false;
            return;
        }

        currentNoteSlug = result.slug;
        elements.noteSelect.value = currentNoteSlug;
        elements.btnSave.disabled = false;
        isDirty = false;

        await loadNotes();
        showSaveStatus(`Saved${result.rebuild?.success ? ' · Published' : ''}`, 'saved');

        if (result.rebuild && !result.rebuild.success) {
            console.warn('Rebuild failed:', result.rebuild.stderr);
        }
    } catch (error) {
        console.error('Failed to save note:', error);
        showSaveStatus('Save failed', 'error');
        elements.btnSave.disabled = false;
    }
}

// Delete current note
async function deleteNote() {
    if (!currentNoteSlug) return;
    if (!confirm('Delete this note permanently?')) return;

    try {
        const response = await fetch(`${API_BASE}/notes/${currentNoteSlug}`, { method: 'DELETE' });
        const result = await response.json();

        if (result.error) {
            showSaveStatus(result.error, 'error');
            return;
        }

        showSaveStatus('Deleted', 'saved');
        newNote();
        await loadNotes();
    } catch (error) {
        console.error('Failed to delete note:', error);
        showSaveStatus('Delete failed', 'error');
    }
}

// Publish / rebuild static site
async function publishSite() {
    showSaveStatus('Publishing...', 'saving');
    elements.btnPublish.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/rebuild`, { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            showSaveStatus('Published successfully', 'saved');
        } else {
            showSaveStatus(`Publish failed: ${result.stderr}`, 'error');
        }
    } catch (error) {
        console.error('Publish failed:', error);
        showSaveStatus('Publish failed', 'error');
    } finally {
        elements.btnPublish.disabled = false;
    }
}

// Search notes
function handleSearch() {
    const query = elements.searchInput.value.trim();
    loadNotes(query);
}

// Update word/character counts
function updateCounts() {
    const text = elements.editor.value;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const chars = text.length;

    elements.wordCount.textContent = `${words} word${words !== 1 ? 's' : ''}`;
    elements.charCount.textContent = `${chars} char${chars !== 1 ? 's' : ''}`;
}

// Markdown preview using marked.js
function setupMarkdownPreview() {
    // Load marked.js from CDN if not available
    if (typeof marked === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
        script.onload = () => {
            marked.setOptions({
                breaks: true,
                gfm: true,
                highlight: (code, lang) => {
                    if (lang && typeof hljs !== 'undefined') {
                        return hljs.highlight(code, { language: lang }).value;
                    }
                    return code;
                }
            });
            updatePreview();
        };
        document.head.appendChild(script);
    }
}

function updatePreview() {
    if (typeof marked !== 'undefined') {
        elements.preview.innerHTML = marked.parse(elements.editor.value || '');
    }
}

// Debounced auto-save indicator
function markDirty() {
    if (!isDirty) {
        isDirty = true;
        showSaveStatus('Unsaved changes', 'saving');
    }
    clearTimeout(saveDebounce);
    saveDebounce = setTimeout(() => {
        if (isDirty && currentNoteSlug) {
            saveNote();
        }
    }, 30000); // Auto-save after 30s of changes
}

// Show save status
function showSaveStatus(message, type) {
    elements.saveStatus.textContent = message;
    elements.saveStatus.className = `save-status ${type}`;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Format date
function formatDate(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) return 'just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
}

// Toolbar actions
function setupToolbar() {
    const actions = {
        bold: () => wrapSelection('**', '**'),
        italic: () => wrapSelection('*', '*'),
        heading: () => insertAtCursor('\n## '),
        link: () => {
            const url = prompt('Enter URL:');
            if (url) wrapSelection('[', `](${url})`);
        },
        code: () => wrapSelection('`', '`'),
        codeblock: () => insertAtCursor('\n```\n\n```\n'),
        ul: () => insertAtCursor('\n- '),
        ol: () => insertAtCursor('\n1. '),
        quote: () => insertAtCursor('\n> '),
    };

    document.querySelectorAll('[data-action]').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = actions[btn.dataset.action];
            if (action) {
                action();
                elements.editor.focus();
                updatePreview();
                updateCounts();
                markDirty();
            }
        });
    });
}

function wrapSelection(prefix, suffix) {
    const start = elements.editor.selectionStart;
    const end = elements.editor.selectionEnd;
    const selected = elements.editor.value.substring(start, end);
    const replacement = prefix + selected + suffix;
    elements.editor.value = elements.editor.value.substring(0, start) + replacement + elements.editor.value.substring(end);
    elements.editor.setSelectionRange(start + prefix.length, start + prefix.length + selected.length);
}

function insertAtCursor(text) {
    const start = elements.editor.selectionStart;
    elements.editor.value = elements.editor.value.substring(0, start) + text + elements.editor.value.substring(elements.editor.selectionEnd);
    elements.editor.setSelectionRange(start + text.length, start + text.length);
}

// Event listeners
function setupEventListeners() {
    // Note select dropdown
    elements.noteSelect.addEventListener('change', (e) => {
        if (e.target.value) loadNote(e.target.value);
        else newNote();
    });

    // Search input
    elements.searchInput.addEventListener('input', debounce(handleSearch, 300));

    // Editor changes
    elements.editor.addEventListener('input', () => {
        updatePreview();
        updateCounts();
        markDirty();
    });

    // Title/tags changes
    elements.noteTitle.addEventListener('input', markDirty);
    elements.noteTags.addEventListener('input', markDirty);

    // Save button
    elements.btnSave.addEventListener('click', saveNote);

    // Publish button
    elements.btnPublish.addEventListener('click', publishSite);

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            saveNote();
        }
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            newNote();
        }
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            publishSite();
        }
    });

    // Toolbar
    setupToolbar();

    // Mobile sidebar toggle (could add hamburger menu later)
}

// Debounce helper
function debounce(fn, delay) {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
    };
}