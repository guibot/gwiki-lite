# gwiki_template.html — offline mini-wiki/tutorial, no server

## What this is

`gwiki_template.html` is a single, **self-contained HTML page** (no server,
no build, no external dependencies) that works as a small wiki or
step-by-step tutorial, structured into **Blocks** and **Sessions**, with:

- **Mode chooser** on first open: **Basic** (text + per-activity notes) or
  **Tutorial** (steps with image + caption)
- Left sidebar with an automatic index (generated from the content)
- Edit mode with lock/unlock (🔒/🔓)
- Right-side notes panel, per activity (Basic mode)
- Image+caption steps, auto-numbered (Tutorial mode)
- 4 color themes (green/blue/orange/gray), picked next to the 🔒 button
- Resizable, collapsible sidebars
- Dark theme, mono font for UI and sans for text

Opened by double-clicking the file (`file://`) — no internet or server
needed. Just a modern browser (Chrome, Edge, Firefox, Safari).

## Mode choice (first open)

On first opening the file (no `mode-basic`/`mode-tutorial` class on
`<body>` yet), a full chooser page is shown instead of the normal layout —
"Basic Wiki" or "Tutorial". On click:

- The class `mode-basic` or `mode-tutorial` is added to `<body>`.
- The other mode's example elements are removed from the DOM
  (`[data-mode="basic"]` / `[data-mode="tutorial"]`).
- The choice only becomes **permanent** once the file is saved (🔒 → 🔓 → 🔒,
  or "💾 Save to file"). Without saving, reloading the page brings the
  chooser back.

There's no popup or `confirm()` for this — it's a full page, no server or
`localStorage`, following the same philosophy as the rest of the file (see
the persistence section below).

## Data structure (where the content lives)

All visible content lives inside:

```html
<main class="main" id="main">
  ... here ...
</main>
```

Each **Block** is a `<section class="doc-section">` with a unique `id`.
Each **Session** is a `<div class="sub-section">` inside a block, also with
a unique `id`. The sidebar is **built automatically by JavaScript** from
these elements — never edit `<ul id="navList">` by hand.

### Minimal skeleton — Basic mode (a Block with one Session)

```html
<section id="block-x" class="doc-section">
  <div class="section-controls">
    <button class="ctrl-btn add-session-btn" type="button">+ Session</button>
    <button class="ctrl-btn danger del-block-btn" type="button">🗑 Block</button>
  </div>
  <h1 contenteditable="false">Block title</h1>
  <p contenteditable="false">Optional intro paragraph for the block.</p>

  <div id="session-x-1" class="sub-section">
    <div class="section-controls">
      <button class="ctrl-btn danger del-session-btn" type="button">🗑 Session</button>
    </div>
    <h2 contenteditable="false">Session 1 · duration - Session title</h2>

    <p contenteditable="false"><strong>15 min · Activity name</strong> Descriptive text for the activity.</p>

    <ul>
      <li contenteditable="false">Optional supporting point.</li>
      <li contenteditable="false">Another point.</li>
    </ul>

    <p contenteditable="false"><strong>Suggested materials and resources</strong> List of materials.</p>
  </div>
</section>
```

### Minimal skeleton — Tutorial mode (a Session with one Step)

```html
<div id="session-y-1" class="sub-section">
  <div class="section-controls">
    <button class="ctrl-btn danger del-session-btn" type="button">🗑 Session</button>
  </div>
  <h2 contenteditable="false">Session 1 · Title</h2>

  <div class="step-block">
    <div class="section-controls step-controls">
      <button class="ctrl-btn add-step-btn" type="button">+ Step</button>
      <button class="ctrl-btn danger del-step-btn" type="button">🗑 Step</button>
    </div>
    <p contenteditable="false"><strong>Step 01</strong> <em>caption…</em></p>
    <img src="screenshots/file-name.png" alt="Step 01"
         style="max-width:100%;border-radius:8px;border:1px solid var(--border);margin:4px 0 24px;display:block">
  </div>

  <div class="step-end-wrap">
    <button class="ctrl-btn add-step-end-btn" type="button">+ Step (at the end of the session)</button>
  </div>
</div>
```

The image must already be copied into a `screenshots/` folder next to the
HTML file — the "+ Step" button only reads the chosen file's **name**, it
doesn't copy the file itself. Numbering (`Step 01`, `Step 02`…) and the
image `alt` are recalculated automatically on every add/remove
(`renumberSteps()`).

### Important rules when adding/editing content by hand (via code)

1. **Unique IDs across the whole document.** Never reuse an `id` (neither
   between blocks nor between sessions). Use descriptive kebab-case
   (`block-coffee`, `session-brew-methods`) or a random suffix if
   generated automatically.
2. **`contenteditable="false"` on every `<h1>`, `<h2>` and `<p>` inside
   `#main`.** The JavaScript toggles this to `true` when the user unlocks
   the page (🔓). Not strictly required by hand, but it's the convention
   used throughout the file.
3. **Activities (Basic mode) = paragraphs starting with `<strong>`.** Any
   `<p>` whose first child is `<strong>text</strong>` is automatically:
   - Styled as a highlighted "badge" (the time/title tag).
   - Clickable in read mode, opening the notes panel on the right.

   Pattern to follow: `<p><strong>15 min · Activity name</strong> rest of the text…</p>`
4. **`section-controls` is required** on every `.doc-section` (with the
   `+ Session` and `🗑 Block` buttons), on every `.sub-section` (with the
   `🗑 Session` button), and on every `.step-block` (with `step-controls`:
   `+ Step` / `🗑 Step`). Without it, the edit buttons won't show up — but
   the JavaScript also injects them automatically on load (`decorateAll()`),
   so it's not critical to forget for blocks/sessions (steps do need to
   come with their buttons already, they aren't rebuilt automatically).
5. **`data-mode="basic"` / `data-mode="tutorial"`** is only used on the
   example blocks shown **before** the mode is chosen. Once the mode is
   set (class on `<body>`), new content doesn't need this attribute.
6. **Don't edit `<ul id="navList">` or the `<script>`.** The sidebar and
   all the logic (lock, notes, steps, theme, resize, save) are generated/
   controlled by the JavaScript already included in the file. Editing
   those by hand can break the page.
7. **Document title and subtitle** (top of the sidebar) are here:
   ```html
   <h1 id="docTitle" contenteditable="false">Offline Wiki</h1>
   <div class="meta" id="docSubtitle" contenteditable="false">Edit and add content</div>
   ```
   These can be edited by hand in the HTML, or through the UI itself once
   unlocked.

## How editing works (for whoever uses the page, not just edits code)

- **Mode choice (first time):** a welcome page with two cards — "Basic
  Wiki" and "Tutorial". Once chosen, it stays fixed (see section above).
- **🔒 / 🔓 (top of the sidebar):** unlocks the page for direct in-browser
  editing (click any title/paragraph and type). Clicking again to lock
  **automatically downloads an updated `index.html`** — you then need to
  manually replace the file in the project folder. There's no server, so
  there's no other way to save.
- **Theme dots** (shown only when unlocked, right below 🔒): green/blue/
  orange/gray — change the accent color across the whole document.
- **+ New Block** (only visible when unlocked, bottom of the sidebar):
  creates a new empty block.
- **+ Session / 🗑 Block / 🗑 Session**: shown above each block/session
  when unlocked. In Tutorial mode, "+ Session" already creates the session
  with one step included.
- **+ Step / 🗑 Step / + Step (at the end of the session)** (Tutorial mode
  only, unlocked): asks for an image file (must already be in
  `screenshots/`) and inserts a new step before/after.
- **Clicking an activity (paragraph with a badge) while locked, Basic
  mode:** opens the notes panel on the right. The **💾 Save to file**
  button inside that panel downloads the file with the note included,
  without touching the lock.
- **Left sidebar:** `⟨` hides it, a fixed `☰` button brings it back. Drag
  the sidebar's right edge (or the notes panel's left edge) to resize.

## Persistence — no localStorage

**Everything** (content, chosen mode, color theme, notes, sidebar widths,
collapsed state) lives inside the HTML file itself (`style`/`data-*`
attributes, classes, text). There's no database and no `localStorage` —
the only real "save" is downloading the updated file and replacing the
original on disk. If the page is reloaded without saving first, changes
made in that browser session are lost — including the mode choice, if it
hasn't been saved yet.

## When Claude Code is asked to add content to this file

1. Read the target `.html` file first.
2. Check which mode is already chosen (`mode-basic`/`mode-tutorial` class
   on `<body>`) to know which skeleton to use (Basic vs. Tutorial).
3. Find `<main class="main" id="main">` and insert new blocks/sessions
   following exactly the matching skeleton above (unique ids,
   `contenteditable="false"`, `section-controls`, activity paragraphs
   starting with `<strong>`, or `step-block`/`step-end-wrap` in Tutorial).
4. Don't touch `<style>` or `<script>`, unless explicitly asked to change
   appearance/behavior.
5. No need to edit the sidebar (`<ul id="navList">`) — it's rebuilt
   automatically on load from the content of `#main`.
6. Validate the resulting HTML (e.g. running `node --check` over the
   `<script>` contents) before calling it done, to make sure no edit broke
   the syntax.
