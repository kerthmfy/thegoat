# Kerth's personal site

A hand-made personal website in the style of the glossy, brushed-metal Apple web of 2002–2012.
No frameworks and no build step: plain HTML, CSS and a little JavaScript you can open, read, edit and host anywhere.

```
kerth-site/
├── index.html            ← the whole homepage (HTML + CSS + JavaScript in one file)
├── 404.html              ← the iOS-style "Page Not Found" alert for wrong addresses
├── notes/                ← one page per note
│   ├── _template.html    ←   copy this to start a new note
│   ├── hello-world.html  ←   your first note
│   └── note.css          ←   the look shared by every note
├── photos/               ← 1.jpg … 6.jpg for the photo board (add yours)
├── cover.jpg             ← the Trajectories album cover
├── photo.jpg             ← (add this) your photo, square, ~400×400
├── iphone5-black.png     ← the phones in the top banner, cut out of the iPhone 5 mockup
├── iphone5-white.png
├── favicon.svg           ← the glossy :) icon in the browser tab
├── apple-touch-icon.png  ← the same icon for iPhone home screens
├── og.png                ← the picture shown when someone shares your link
├── films.json            ← latest Letterboxd films (updated automatically; don't edit by hand)
├── scripts/letterboxd.py ← reads the Letterboxd diary and writes films.json
├── .github/workflows/letterboxd.yml ← runs that script on GitHub every day
├── cloudflare-worker.js  ← optional: your own proxy for live film updates
└── README.md             ← this file
```

Until `photo.jpg` exists, the page shows your initials instead, so nothing looks broken.

---

## 1. See it on your computer

Double-click `index.html` and it opens in your browser. That's enough for most editing.

Some parts (the Films tickets, opening notes from the list) need a real web server. Run this inside the
folder, then open http://localhost:8000:

```bash
python3 -m http.server 8000
```

Edit → save → refresh. That's the whole workflow.

**Check it on your phone:** while that command is running, find your computer's local IP address
(Mac: System Settings → Wi-Fi → Details; Windows: `ipconfig`) and open `http://THAT-IP:8000` on a phone
on the same Wi-Fi.

---

## 2. Editing cheat sheet

Open `index.html`, search (Ctrl/Cmd+F) for the text in the right column, and change what's between the tags.

| To change… | Search for |
|---|---|
| The big headline | `hello, human.` |
| The line under it | `Enjoy lad` |
| Your contact card and the other address-book cards | `class="book"`, then the `<dt>label</dt><dd>value</dd>` pairs |
| Projects | `id="projects"` |
| GitHub repos | `id="code"` (one `<li>` line per repo) |
| Album info | `id="music"` |
| The list of notes | `NEW NOTE?` |
| Photo captions | `class="polaroid"` |
| Links | `id="links"` |
| Any color, everywhere | the design tokens at the top of `<style>`, e.g. `--link` |

### Write a new note
1. Copy `notes/_template.html` and rename the copy, e.g. `notes/my-iphone-5-setup.html`
   (lowercase, dashes instead of spaces; it becomes `yoursite/notes/my-iphone-5-setup.html`).
2. Change the 4 things marked ✏️ (tab title, one-line description, date and topic, big title), then write.
   The template shows every building block: paragraphs, headings, lists, quotes, a taped-on photo, code.
3. In `index.html`, search `NEW NOTE?`, copy the `<article class="note">` block below it, paste it at the top
   of the list, and point its title, date, summary and links at your new file.
4. Upload both files.

### Add photos
Save them as `photos/1.jpg` … `photos/6.jpg` (lowercase `.jpg`, under ~1 MB, square-ish looks best).
Only the ones that exist show up. Caption: put `<figcaption>Binondo, 2026</figcaption>` right after that
photo's `<img …>`. More than 6: copy a whole `<figure class="polaroid">…</figure>` line and change the number.

### Other common edits
- **Add a GitHub repo:** copy one `<li>` line under `id="code"`, change the name, text, language and color.
- **Add a contact to the address book:** add a `<li><button …>` on the left page and a matching
  `<div class="card" …>` on the right page. The button's `aria-controls` must equal the card's `id`
  (e.g. `aria-controls="card-ipod"` and `id="card-ipod"`). Every card except the first has `hidden`.
- **Add a service card in Projects:** copy one `<article class="item"> … </article>` block (3 or 6 per panel looks neatest).
- **Change an icon tile:** each tile has `style="--a:#…;--b:#…"` (top and bottom color) and an icon like
  `<use href="#i-music"/>`. The icons are defined once near the top of `<body>` (search `ICONS`).
- **Add a whole new section:** a "Favorites" section is ready in an HTML comment. Search `TEMPLATE`.

---

## 3. Put it online with GitHub Pages (free)

**One-time setup**
1. On github.com, create a **public** repository named exactly `thegoat`.
2. Upload everything in this folder. Use **GitHub Desktop** (clone the empty repo, copy the files in,
   Commit, Push): the website uploader skips hidden folders like `.github`, which the Films updater needs.
3. In the repo: **Settings → Pages → Source: Deploy from a branch → main / (root) → Save** (if it isn't already).
4. **Settings → Actions → General → Workflow permissions → Read and write permissions → Save**
   (lets the Films updater save `films.json`).
5. **Actions → Update films → Run workflow** once, so your films appear straight away.
6. Open `https://kerthmfy.github.io/thegoat/`. That's your site.
   (Your work portfolio keeps living at `https://kerthmfy.github.io/portfolio_/`.)

Renaming the repository later? The address becomes `https://kerthmfy.github.io/NEW-NAME/`, so
change the two `og:` addresses in `index.html`, and the two `/thegoat/` links in `404.html`.

**Changing things later**
- **Quick text fixes:** open the file on github.com → pencil icon → edit → **Commit changes**. Live in about a minute.
- **Bigger edits:** edit in **VS Code**, check in your browser, then in GitHub Desktop write a short summary
  ("add new note") → **Commit** → **Push**.
- **Swapping a picture:** upload a file with the same name and it replaces the old one.

Every commit is saved, so you can always see or undo an older version from the repository's history.

**Custom domain (optional):** **Settings → Pages → Custom domain**, then follow GitHub's DNS instructions.
HTTPS is free. Update the `og:` addresses afterwards.

---

## 4. Things that update by themselves

**Films.** On every visit the page reads your Letterboxd feed live through a proxy, and falls back to
`films.json`, which the GitHub Action refreshes daily at 10:17 Manila time. The note above the tickets says
which one you're seeing ("Live from Letterboxd" with a green dot, or "Updated daily").
For the most reliable live updates, set up your own free Cloudflare Worker: the steps are at the top of
`cloudflare-worker.js`, then paste its address into `MY_PROXY` in `index.html`.

**Clock, date and lock screen.** Always show the current time in Manila.

**Footer year.** Updates itself every January.

---

## 5. Credits

Phones: "iPhone 5 three-quarter perspective mockup", a free PSD resource.
Fonts: Myriad, Lucida Grande, Helvetica Neue and Monaco where the visitor has them;
otherwise Source Sans 3 and Patrick Hand from Google Fonts, or built-in lookalikes.
