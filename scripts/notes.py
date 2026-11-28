"""Turn my notes, written in Markdown, into the note pages on my site.

Each note is a plain text file in the notes/ folder, for example notes/home-server.md:

    ---
    title: How my home server is put together
    date: 2026-12-03
    topic: Homelab
    summary: One or two sentences for the Notes list and link previews.
    ---

    Then just write. A blank line starts a new paragraph.

(notes/_template.md has every option with examples.)

Running this script:
  1. builds notes/home-server.html from it (the look lives in notes/note.css),
  2. rewrites the Notes list on index.html (between NOTES:START and NOTES:END), newest first,
  3. gets photos ready for the web: shrinks big ones to 1600px, turns iPhone HEIC photos
     into JPG, rotates them the right way up and removes hidden data like GPS location.

Run it yourself before previewing:
    python3 scripts/notes.py
On GitHub, .github/workflows/notes.yml runs it whenever a note changes.

Text needs nothing extra installed. Photos need Pillow, installed once with:
    pip3 install --user pillow pillow-heif
(Without it, the script still builds the pages and GitHub fixes the photos when you push.)
"""

import datetime
import html
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent     # the website folder
NOTES = ROOT / "notes"
INDEX = ROOT / "index.html"
MAX_PHOTO = 1600                                  # longest side of a photo, in pixels
MADE_BY = "Made by scripts/notes.py"              # marks pages this script owns


# ---------------------------------------------------------------------------
# 1. Reading a note: the "front matter" block on top, then the text
# ---------------------------------------------------------------------------
def read_note(path):
    """Return (settings, text) for one .md file."""
    raw = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    settings, text = {}, raw
    m = re.match(r"---\n(.*?)\n---\n?(.*)", raw, re.S)
    if m:
        text = m.group(2)
        for line in m.group(1).split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                settings[key.strip().lower()] = value.strip().strip('"').strip("'")
    return settings, text


def pretty_date(iso):
    """2026-11-27 -> Nov 27, 2026"""
    d = datetime.date.fromisoformat(iso)
    return "{} {}, {}".format(d.strftime("%b"), d.day, d.year)


# ---------------------------------------------------------------------------
# 2. Markdown -> HTML (only the pieces a note needs)
# ---------------------------------------------------------------------------
IMAGE = re.compile(r'!\[([^\]]*)\]\(\s*([^)\s]+)(?:\s+"([^"]*)")?\s*\)')   # ![alt](src "caption")
LINK = re.compile(r"\[([^\]]+)\]\(\s*([^)\s]+)\s*\)")                      # [text](url)
BARE_URL = re.compile(r"(?<![\w\"'=/])(https?://[^\s<]+[^\s<.,:;!?)\]'\"])")
BULLET = re.compile(r"[-*+]\s+")
NUMBER = re.compile(r"\d+[.)]\s+")
HEADING = re.compile(r"(#{1,3})\s+(.*)")


def attr(value):
    """Make text safe inside an HTML attribute like href="…"."""
    return html.escape(value, quote=False).replace('"', "&quot;")


def link_html(url, text):
    outside = url.startswith(("http://", "https://"))
    extra = ' target="_blank" rel="noopener noreferrer"' if outside else ""
    return '<a href="{}"{}>{}</a>'.format(attr(html.unescape(url)), extra, text)


def inline(text):
    """**bold**, *italic*, `code`, [links](…) and bare https://… links inside one line."""
    text = html.escape(text, quote=False)        # so < and & show up as typed
    saved = []

    def keep(snippet):                           # park finished HTML so later steps can't touch it
        saved.append(snippet)
        return "\x00{}\x00".format(len(saved) - 1)

    text = re.sub(r"`([^`]+)`", lambda m: keep("<code>" + m.group(1) + "</code>"), text)
    text = IMAGE.sub(lambda m: keep('<img src="{}" alt="{}" loading="lazy">'.format(
        attr(html.unescape(m.group(2))), attr(html.unescape(m.group(1))))), text)
    text = LINK.sub(lambda m: keep(link_html(m.group(2), emphasis(m.group(1)))), text)
    text = BARE_URL.sub(lambda m: keep(link_html(m.group(1), m.group(1))), text)
    text = emphasis(text)
    return re.sub("\x00(\\d+)\x00", lambda m: saved[int(m.group(1))], text)


def emphasis(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<i>\1</i>", text)
    return re.sub(r"(?<![\w])_(?!\s)(.+?)(?<!\s)_(?![\w])", r"<i>\1</i>", text)


def lines_to_html(lines):
    """Lines of one paragraph. A line ending in two spaces or a \\ keeps its line break."""
    out = ""
    for n, line in enumerate(lines):
        hard_break = line.endswith("  ") or line.rstrip().endswith("\\")
        out += inline(line.strip().rstrip("\\").rstrip())
        if n < len(lines) - 1:
            out += "<br>\n" if hard_break else " "
    return out


def figure(m):
    alt, src, caption = m.group(1), m.group(2), m.group(3) or m.group(1)
    cap = "<figcaption>{}</figcaption>".format(inline(caption)) if caption else ""
    return '<figure><img src="{}" alt="{}" loading="lazy">{}</figure>'.format(attr(src), attr(alt), cap)


def starts_block(s):
    return (s.startswith(("```", ">")) or HEADING.match(s) or BULLET.match(s)
            or NUMBER.match(s) or IMAGE.fullmatch(s))


def markdown(text):
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
        elif s.startswith("```"):                                   # a block of code
            i, code = i + 1, []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(code), quote=False) + "</code></pre>")
        elif HEADING.match(s):                                      # ## Heading
            m = HEADING.match(s)
            level = 3 if len(m.group(1)) == 3 else 2                # the note's title is the only h1
            out.append("<h{0}>{1}</h{0}>".format(level, inline(m.group(2))))
            i += 1
        elif IMAGE.fullmatch(s):                                    # a photo on its own line
            out.append(figure(IMAGE.fullmatch(s)))
            i += 1
        elif s.startswith(">"):                                     # > a quote
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].lstrip())
                i += 1
            out.append("<blockquote>" + lines_to_html(quote) + "</blockquote>")
        elif BULLET.match(s) or NUMBER.match(s):                    # - a list
            pattern = NUMBER if NUMBER.match(s) else BULLET
            items = []
            while i < len(lines) and lines[i].strip():
                t = lines[i].strip()
                m = pattern.match(t)
                if m:
                    items.append(t[m.end():])
                elif items and lines[i][:1] in (" ", "\t"):          # an indented line continues the item
                    items[-1] += " " + t
                else:
                    break
                i += 1
            tag = "ol" if pattern is NUMBER else "ul"
            out.append("<{0}>{1}</{0}>".format(tag, "".join("<li>" + inline(x) + "</li>" for x in items)))
        else:                                                       # a paragraph
            para = []
            while i < len(lines) and lines[i].strip() and (not para or not starts_block(lines[i].strip())):
                para.append(lines[i])
                i += 1
            out.append("<p>" + lines_to_html(para) + "</p>")
    return "\n".join("    " + block for block in out)


def first_paragraph(text):
    """Plain text of the first paragraph, used when a note has no summary."""
    for chunk in text.split("\n\n"):
        s = chunk.strip()
        if s and not starts_block(s):
            plain = re.sub(r"<[^>]+>", "", html.unescape(lines_to_html(s.split("\n"))))
            return plain if len(plain) <= 220 else plain[:217].rsplit(" ", 1)[0] + "…"
    return ""


# ---------------------------------------------------------------------------
# 3. Photos: shrink, turn HEIC into JPG, rotate upright, drop hidden data (GPS…)
# ---------------------------------------------------------------------------
try:
    from PIL import Image, ImageOps
    try:
        import pillow_heif                     # lets Pillow open iPhone .heic photos
        pillow_heif.register_heif_opener()
    except ImportError:
        pass
except ImportError:
    Image = None

warned_no_pillow = False


def fix_photo(path):
    """Get one photo ready for the web. Returns its (maybe new) path."""
    global warned_no_pillow
    heic = path.suffix.lower() in (".heic", ".heif")
    if Image is None:
        if not warned_no_pillow:
            print("  ! Photos weren't checked: run  pip3 install --user pillow pillow-heif"
                  "  (or just push: GitHub does it for you).")
            warned_no_pillow = True
        return path
    try:
        img = Image.open(path)
    except Exception as e:                     # e.g. HEIC without pillow-heif
        print("  ! Couldn't open {}: {}".format(path.name, e))
        return path
    too_big = max(img.size) > MAX_PHOTO
    has_extra_data = bool(img.getexif())       # camera info, GPS location, rotation…
    if not (heic or too_big or has_extra_data):
        return path                            # already fine: leave it alone
    icc = img.info.get("icc_profile")          # keeps the colours right
    img = ImageOps.exif_transpose(img)         # phone photos store "rotate me" separately
    img.thumbnail((MAX_PHOTO, MAX_PHOTO))
    out = path.with_suffix(".jpg") if heic else path
    if out.suffix.lower() in (".jpg", ".jpeg"):
        img.convert("RGB").save(out, "JPEG", quality=82, progressive=True, optimize=True, icc_profile=icc)
    else:
        img.save(out, icc_profile=icc)
    if heic:
        path.unlink()                          # the JPG replaces the HEIC
    print("  photo ready: {} ({}x{})".format(out.name, *img.size))
    return out


def fix_photos(md_path, text):
    """Fix every photo a note uses. If a HEIC became a JPG, update the .md to match."""
    changed = text
    for m in IMAGE.finditer(text):
        src = m.group(2)
        if src.startswith(("http://", "https://", "/", "data:")):
            continue
        photo = (NOTES / urllib.parse.unquote(src)).resolve()
        if not photo.is_file():
            print("  ! {} uses {}, but that file isn't there.".format(md_path.name, src))
            continue
        new = fix_photo(photo)
        if new != photo:
            new_src = src[: -len(photo.suffix)] + new.suffix
            changed = changed.replace("](" + src, "](" + new_src)
    if changed != text:
        md_path.write_text(md_path.read_text(encoding="utf-8").replace(text, changed), encoding="utf-8")
    return changed


# ---------------------------------------------------------------------------
# 4. The page for one note, and its card in the homepage list
# ---------------------------------------------------------------------------
PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<!-- {made_by} from notes/{slug}.md. Edit that file, not this one:
     this page is rewritten every time the script runs. -->
<title>{title} · Kerth Yadao</title>
<meta name="description" content="{summary}">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<!-- dark only if the switch on the homepage was set to dark -->
<script>try{{if(localStorage.getItem("theme")==="dark")document.documentElement.dataset.theme="dark"}}catch(e){{}}</script>
<link rel="stylesheet" href="note.css">
</head>
<body>
<div class="page">

  <header class="top"><a href="../#notes">‹ Notes</a><a href="../">Kerth Yadao</a></header>

  <article>
    <p class="meta"><time datetime="{date}">{pretty}</time>{topic}</p>
    <h1>{title}</h1>

{body}
  </article>

  <footer class="foot"><a href="../#notes">‹ All notes</a><a href="../">Home</a></footer>
</div>
</body>
</html>
"""

CARD = """      <article class="note">
        <div class="note-top"><h3><a href="{href}">{title}</a></h3><time datetime="{date}">{pretty}</time></div>
        <p>{summary}</p>
        <div class="split"><a href="{href}">Read note ▸</a><span>{topic}</span></div>
      </article>"""

DRAFT_CARD = """      <article class="note">
        <div class="note-top"><h3>{title}</h3><span class="when">Draft</span></div>
        <p>{summary}</p>
        <div class="split"><span>Coming soon</span><span>{topic}</span></div>
      </article>"""


def write_if_changed(path, content):
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")
        return True
    return False


def main():
    notes, problems = [], []
    for md in sorted(NOTES.glob("*.md")):
        if md.name.startswith("_"):            # _template.md and friends are skipped
            continue
        s, text = read_note(md)
        draft = s.get("draft", "").lower() in ("yes", "true", "1")
        if not s.get("title"):
            problems.append("{}: needs a 'title:' line at the top.".format(md.name))
            continue
        try:
            date = s.get("date", "")
            pretty = pretty_date(date) if date or not draft else ""
        except ValueError:
            problems.append("{}: date must look like 2026-12-03 (year-month-day), not '{}'.".format(md.name, date))
            continue
        if not draft:
            text = fix_photos(md, text)
        notes.append({
            "slug": md.stem, "draft": draft, "date": date, "pretty": pretty, "text": text,
            "title": s["title"], "topic": s.get("topic", ""),
            "summary": s.get("summary") or first_paragraph(text),
        })

    if problems:
        print("Couldn't build these notes:\n  " + "\n  ".join(problems))
        sys.exit(1)

    # newest first; drafts go after the published notes
    newest_first = lambda group: sorted(group, key=lambda n: n["date"], reverse=True)
    notes = newest_first([n for n in notes if not n["draft"]]) + newest_first([n for n in notes if n["draft"]])

    # 1. one page per published note
    for n in notes:
        if n["draft"]:
            continue
        page = PAGE.format(
            made_by=MADE_BY, slug=n["slug"], title=html.escape(n["title"], quote=False), summary=attr(n["summary"]),
            date=n["date"], pretty=n["pretty"], body=markdown(n["text"]),
            topic=" · " + html.escape(n["topic"], quote=False) if n["topic"] else "")
        if write_if_changed(NOTES / (n["slug"] + ".html"), page):
            print("  wrote notes/{}.html".format(n["slug"]))

    # pages whose note was deleted or turned back into a draft
    keep = {n["slug"] for n in notes if not n["draft"]}
    for page in NOTES.glob("*.html"):
        if page.stem not in keep and MADE_BY in page.read_text(encoding="utf-8")[:600]:
            page.unlink()
            print("  removed notes/{} (its .md is gone or is a draft)".format(page.name))

    # 2. the list on the homepage
    cards = []
    for n in notes:
        fields = {k: html.escape(n[k], quote=False) for k in ("title", "summary", "topic", "date", "pretty")}
        fields["href"] = "notes/" + urllib.parse.quote(n["slug"]) + ".html"
        cards.append((DRAFT_CARD if n["draft"] else CARD).format(**fields))
    page = INDEX.read_text(encoding="utf-8")
    m = re.search(r"(<!-- NOTES:START.*?-->\n)(.*?)(\s*<!-- NOTES:END -->)", page, re.S)
    if not m:
        print("index.html is missing the <!-- NOTES:START --> and <!-- NOTES:END --> lines.")
        sys.exit(1)
    page = page[: m.start(2)] + "\n\n".join(cards) + page[m.end(2):]
    if write_if_changed(INDEX, page):
        print("  updated the Notes list on index.html")

    print("Notes done: {} published, {} draft.".format(len(keep), len(notes) - len(keep)))


if __name__ == "__main__":
    main()
