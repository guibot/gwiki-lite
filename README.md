# gwiki-lite

A server-less version of [gwiki](https://github.com/guibot/gwiki): a single
self-contained HTML file that works as an editable wiki or a step-by-step
tutorial — no install, no build, no backend.

## Why

The original gwiki needs a server. This one is for when that's overkill:
course notes, a tutorial to share, small-project documentation — just open
the file in a browser (`file://`) and you're done.

## Usage

1. Copy `gwiki_template.html` into your project (you can rename it to
   `index.html`).
2. Open it in a browser. On first run, pick a mode:
   - **Basic Wiki** — text blocks and sessions, with notes per activity.
   - **Tutorial** — numbered steps, each with an image + caption.
3. Click 🔒 to unlock and edit directly on the page.
4. Click again (🔓 → 🔒) to save — the browser downloads an updated
   `index.html`. Replace the old file with that one.

There's no server or database: all state (content, chosen mode, color
theme, notes, sidebar widths) lives inside the HTML itself. Saving means
downloading the file and replacing the old one.

## Features

- Mode chooser on first run (stays fixed once you save)
- Left index generated automatically from the content
- Direct in-page editing (lock/unlock)
- Basic mode: per-activity notes in a side panel
- Tutorial mode: image + caption steps, auto-numbered
- 4 color themes (green/blue/orange/gray)
- Resizable, collapsible sidebars
- Zero external dependencies, zero build, zero server

## Files

- `gwiki_template.html` — the main template (use this one)
- `template.md` — documentation of the HTML's internal structure, for
  anyone editing the content directly in code (or asking Claude Code to do
  it)

## Relation to gwiki

This project is a derivative of [gwiki](https://github.com/guibot/gwiki),
built for cases where running a server isn't worth it. It's not a
replacement — it's a lightweight version for one-off or offline use.
