# How this site is built

A guided tour of the code, from the big picture down to each skeuomorphic detail.
Read it top to bottom once, then use it as a reference. Every part names the section to
search for in `index.html` (for example `7b.`), so you can read the real code next to the explanation.

**Contents**
1. [The big picture](#1-the-big-picture)
2. [Your tools](#2-your-tools)
3. [HTML: the content](#3-html-the-content)
4. [CSS: the look](#4-css-the-look)
5. [Recipes: how each retro object is made](#5-recipes-how-each-retro-object-is-made)
6. [The iPhone mockups](#6-the-iphone-mockups)
7. [JavaScript: the behaviour](#7-javascript-the-behaviour)
8. [Data from other sites: Letterboxd and Bandcamp](#8-data-from-other-sites-letterboxd-and-bandcamp)
9. [Accessibility and performance](#9-accessibility-and-performance)
10. [Changing things safely](#10-changing-things-safely)
11. [Exercises](#11-exercises)
12. [Glossary](#12-glossary)

---

## 1. The big picture

This is a **static site**: a folder of files that a server hands to the browser exactly as they are.
There's no database, no framework and no "build" step. What you see in `index.html` is what the visitor gets.
That's why it's a great way to learn: if you can read the file, you understand the site.

When someone opens the site:

1. The browser downloads `index.html`.
2. It reads the **HTML** top to bottom and builds the page's structure (headings, sections, links).
3. It applies the **CSS** in `<style>` to decide how everything looks.
4. It loads the images, fonts and the Bandcamp player only when needed.
5. It runs the **JavaScript** at the bottom, which adds behaviour: the clock, slide to unlock, the films.

| Layer | Job | Where |
|---|---|---|
| HTML | What's on the page | `<body>` |
| CSS | How it looks | `<style>` at the top |
| JavaScript | What it does | `<script>` at the bottom |

A rule this site follows everywhere: **content first, looks second, behaviour last.**
Turn JavaScript off and every section, link and text is still there. JavaScript only makes it nicer.

**Why one big file?** For a single page it's the simplest thing: one file to open, nothing to keep in sync.
The note pages are separate files because there will be many of them and they share one look (`notes/note.css`).
That's the moment splitting CSS into its own file starts paying off.

The top of `index.html` has a map of every section (search `HOW THIS FILE IS ORGANISED`).

---

## 2. Your tools

- **An editor:** VS Code is free and colours the code so it's easier to read. Its "Format Document"
  command tidies indentation.
- **A browser with DevTools:** right-click anything → **Inspect**. This is the most useful learning tool there is.
  - **Elements** shows the HTML. Click an element and the right side shows every CSS rule affecting it.
    You can tick rules off and edit values live. Nothing is saved, so experiment freely.
  - **Console** shows JavaScript errors in red. If something stops working, look here first.
  - **Network** shows every file the page loads, and which ones failed (for example a missing `photos/3.jpg`).
  - **Toggle device toolbar** (the phone icon) previews phone sizes.
- **A local server:** `python3 -m http.server 8000` in the folder, then open `http://localhost:8000`.
  Opening the file directly works for most things, but `fetch()` (used by Films) needs a server.

---

## 3. HTML: the content

HTML is a tree of **elements**: `<tag attribute="value">content</tag>`.
This site uses meaningful tags so browsers, search engines and screen readers understand the page:

| Tag | Used for |
|---|---|
| `<header>`, `<nav>` | The silver bar and its links |
| `<main>`, `<section>` | The page's content, one section per topic |
| `<article>` | Self-contained things: a note, a service card |
| `<h1>` … `<h4>` | Headings, in order of importance (one `<h1>` per page) |
| `<ul>`, `<ol>`, `<li>` | Lists: links, repos, contacts |
| `<dl>`, `<dt>`, `<dd>` | Label/value pairs: the address book cards, album facts |
| `<figure>`, `<figcaption>` | A photo and its caption |
| `<footer>` | The bottom of the page |

### Sections and links within the page
Each section has an `id`, like `<section class="sec" id="music">`. A link to `#music` scrolls there.
The nav, the iPhone icons and the "Go to…" buttons are all just links to these ids.

### Attributes you'll see a lot
- `class="…"` names an element so CSS and JavaScript can find it. One element can have several: `class="aqua pulse"`.
- `alt="…"` on images describes them for people who can't see them. Empty `alt=""` means "decorative, skip it".
- `aria-label`, `aria-hidden`, `role` give extra information to screen readers (more in [section 9](#9-accessibility-and-performance)).
- `hidden` hides an element completely. JavaScript adds and removes it (address book cards, the zoom view).
- `target="_blank" rel="noopener noreferrer"` opens a link in a new tab, safely.

### Comments
`<!-- like this -->` in HTML and `/* like this */` in CSS and JavaScript. The browser ignores them.
They're notes for you. The ✏️ comments mark things you'll want to edit.

### The icon sprite
Near the top of `<body>` (search `ICONS`) there's a hidden `<svg>` with `<symbol>`s: person, server, music, mail and more.
Each is a tiny line drawing. Anywhere on the page, `<svg class="ic"><use href="#i-music"/></svg>` stamps a copy.
Draw once, use everywhere. Change the drawing and every copy updates.

---

## 4. CSS: the look

### Rules, selectors and the cascade
```css
.ticket .tk-title { font-size: 19px; }
```
"For every element with class `tk-title` inside a `ticket`, make the text 19px."
When two rules disagree, the more specific selector wins, and if they're equal, the later one wins.
That's the "cascade". DevTools crosses out the losing rules, which is the fastest way to see why something
doesn't look how you expect.

### Design tokens (CSS variables)
Section `0.` defines every colour once:
```css
:root { --link: #0b63c4; --panel: #ffffff; }
a { color: var(--link); }
```
Change `--link` and every link on the site changes. Variables can also hold sizes, fonts and even pictures
(`--metal-tex`, `--noise` are tiny SVG textures).

### Light by default, dark on request
The dark theme is the same tokens with night values, applied only when the `<html>` element has
`data-theme="dark"`:
```css
:root[data-theme="dark"] { --page: #000; --ink: #f2f2f4; … }
```
A one-line script in `<head>` reads the visitor's saved choice and sets that attribute *before* the page paints,
so there's no flash of the wrong theme. The footer menu changes it (JavaScript part 3).

### Boxes: the box model
Every element is a box: **content**, then **padding** (space inside the border), then **border**, then **margin**
(space outside). `* { box-sizing: border-box }` at the top makes widths include padding and border, which is far
easier to reason about.

### Layout: flexbox and grid
- **Flexbox** lines things up in one direction. The nav bar is `display: flex`: items in a row, each `flex: 1`
  so they share the width equally.
- **Grid** lays things out in rows *and* columns. Projects is
  `grid-template-columns: 190px minmax(0,1fr) 190px`: two fixed side columns and a flexible middle.
- `gap` puts space between items without margins on each one.
- `minmax(0,1fr)` instead of `1fr` stops long words from stretching a column wider than the screen.

### Responsive design
The site has to work from a 4K monitor down to a small phone.
- **`@media (max-width: 760px) { … }`** applies rules only on narrow screens. Section `11.` holds most of them:
  the nav becomes 4 across, Projects becomes one column, the two outer phones hide.
- **`clamp(min, preferred, max)`** scales smoothly: `font-size: clamp(36px, 6.4vw, 62px)` follows the window width
  (`vw` = 1% of it) but never goes below 36px or above 62px.
- **Relative units:** `em` is "the current font size". The iPhone screens are built in `em`, so one number
  scales a whole screen (see [section 6](#6-the-iphone-mockups)).
- **The side gutter** `padding-left: max(16px, env(safe-area-inset-left))` keeps 16px of space at the edges, and
  more on phones with a notch.

### Positioning
- `position: relative` on a parent + `position: absolute` on a child = place the child exactly inside the parent
  (the cover's play button, the pins on polaroids, the ribbon on the book).
- `position: sticky; top: 8px` on the header: it scrolls normally, then sticks 8px from the top (section `3.`).
- `position: fixed` stays put on screen while the page scrolls (the zoom overlay).
- `z-index` decides what's on top when things overlap. It only works on positioned elements.

### Pseudo-elements: free extra layers
`::before` and `::after` add a fake element inside any element, with `content: ""`.
This site uses them constantly: the shine on Aqua buttons, the glare on phone screens, the notches on tickets,
the pins on polaroids, the stitching on the leather book. No extra HTML needed.

### Gradients: most of the "realism"
Almost every texture here is a gradient, not an image:
- `linear-gradient(top, bottom)`: metal bars, buttons, paper.
- **Hard stops** make sharp edges: `linear-gradient(#ddd 48%, #ccc 52%)` is the "curved metal" crease.
- `radial-gradient(circle at 50% 30%, …)`: round glossy things like the Say hi orb and push pins.
- `repeating-linear-gradient(…)`: ruled lines on the notepad and notes paper, the earpiece grille.
- `repeating-conic-gradient(…)`: the 12 tick marks on the clock face.
- Several gradients **stack** in one `background`, separated by commas, first one on top.

### Shadows and light
- `box-shadow: 0 2px 6px rgba(0,0,0,.3)` lifts something off the page.
- `inset` shadows push things in: the LCD, the search field, the slider track.
- **The 1px highlight trick:** `inset 0 1px 0 rgba(255,255,255,.8)` draws a thin bright line along the top edge.
  It's what makes surfaces look lit from above, the single most "2007 Apple" detail on the site.
- `text-shadow: 0 1px 0 #fff` on grey text looks *engraved*; `0 -1px 0 rgba(0,0,0,.4)` on white text looks *embossed*.

### Motion
- `transition: transform .2s` animates a change smoothly (hovering tickets, polaroids, dock icons).
- `@keyframes` + `animation` loop on their own: the pulsing button, the "slide to unlock" shimmer, the blinking
  terminal cursor.
- `@media (prefers-reduced-motion: reduce)` at the bottom of section `11.` switches all of it off for people who
  have asked their device for less motion.

---

## 5. Recipes: how each retro object is made

Each recipe names its CSS section. Open it in DevTools next to this.

**Aqua button** (section `2.`, `.aqua`). The body gradient runs *dark at the top to light at the bottom*, like light
glowing through blue plastic. `::before` is a white-to-clear pill over the top half: the shine.
`.aqua.alt` is the grey version. `.aqua.pulse` adds the Mac OS X "default button" throb with `@keyframes pulse`.

**Silver nav bar** (section `3.`). A four-stop gradient with a jump at 48–52% fakes a curved aluminium surface.
Between buttons: a dark 1px border plus a light 1px inset shadow = an engraved groove.
The selected button (`aria-current`) gets a dark gradient and an inset shadow, so it looks pressed in.

**Gradient headline** (section `4.`, `.hello`). `background: linear-gradient(white, grey)`, then
`background-clip: text` and `color: transparent`: the gradient only shows through the letters.

**Reflections** (sections `5.` and `8.`). `-webkit-box-reflect: below 2px linear-gradient(transparent 70%, rgba(255,255,255,.2))`
draws a mirrored copy, faded by the gradient. Chrome, Edge and Safari show it; Firefox skips it.

**Brushed metal** (`--metal-tex`, used by `.metal`). An SVG `feTurbulence` noise filter with
`baseFrequency='0.003 0.9'`: low frequency sideways, high frequency up and down, so the noise stretches into
thin horizontal streaks. Layered over a grey gradient.

**Leather Address Book** (section `6.`). Brown gradients with a noise texture blended on top
(`background-blend-mode: multiply`). The stitching is `::before` with a `2px dashed` border inset 7px.
The stacked page edges are four 1px `box-shadow`s in slightly different creams. The spine shadow is a gradient that
darkens toward the middle. The red ribbon is a rectangle with `clip-path: polygon(…)` cutting the V notch.

**Blue-grey panel bars** (section `7.`, `.bar`). Same split-gradient trick as the nav, in blue-grey, with white text
and a dark text shadow. The numbered list uses `counter(list-item)` so the numbers write themselves.

**iOS 6 table view** (section `7b.`). `.tv-bar` is the glossy navigation bar; `.tv-btn` the dark bar buttons.
`.src-h` is the translucent section header strip. The 1px lines between rows are a trick: the list has
`gap: 1px` and a grey background, the rows are white, so the background shows through the gaps as lines.

**Music player window** (section `8.`). Brushed metal frame, traffic lights (`radial-gradient` highlight + colour),
round transport buttons, and the LCD: a pale green-grey gradient with an inset shadow, like the old iTunes display.

**Paper ticket** (section `8b.`). Cream gradient + noise. The dashed tear line is the stub's `border-left`.
The half-moon notches are `::before`/`::after` circles painted in the *page* colour, so they look cut out.
`--r` gives each ticket a slightly different tilt (`:nth-child(3n+2)` picks every third one).

**Cork board and polaroids** (section `8c.`). Wooden frame = a diagonal brown gradient. Cork = tan gradients + noise.
A polaroid is a white box with more padding at the bottom; `::before` is the red push pin (radial gradient + shadow).
The sticky note is a yellow gradient, tilted 2°, in the handwriting font.

**World clock face** (section `5f.`). Three stacked backgrounds: a radial gradient that covers the middle and the rim,
leaving a ring; a `repeating-conic-gradient` that draws 12 tick marks, visible only in that ring; and a base colour.
The hands are thin rounded boxes rotated around their bottom edge (`transform-origin: 50% 100%`).

**Lined notepad** (section `5g.` and `notes/note.css`). A `repeating-linear-gradient` draws a blue line every
`1.5em` (or `--line-h`), and the text's `line-height` is the same number, so words sit on the lines.
A second gradient draws the red margin.

**Lock screen** (section `5h.`). Frosted bars = semi-transparent dark gradients. The famous shimmer:
```css
color: transparent;
background: linear-gradient(90deg, grey 42%, white 50%, grey 58%);
background-size: 250% 100%;
background-clip: text;
animation: shine 2.6s linear infinite;   /* slides the gradient sideways forever */
```
The text is invisible; you're seeing the gradient through the letter shapes, and the white band travels along.

**404 page** (`404.html`). An iOS 6 alert: a navy gradient box with a curved gloss
(an oversized `radial-gradient` ellipse peeking in from above), a white border and a glossy button.
GitHub Pages automatically shows `404.html` for any address that doesn't exist.

---

## 6. The iPhone mockups

This is the most advanced trick on the site.

### The pictures
`iphone5-black.png` and `iphone5-white.png` are cut out of the iPhone 5 three-quarter mockup PSD:
just the phone bodies, with transparent backgrounds so they sit on the black stage. They were taken from the PSD's
own full-quality render (so every bevel and highlight is there), with the background removed using the phone's
outline from the PSD. To do this yourself in a free tool like Photopea: open the PSD, hide the background and the
"YOUR SCREEN HERE" layer, and export a PNG.

### The screens are real HTML
The screens are *not* part of the picture. Each one is a `<div class="dev-scr">` sized exactly like an iPhone 5
screen in points: **320 × 568**. Everything inside is normal HTML and CSS: status bar, title bar, terminal, clock.
So the clock ticks, the icons are real links, and the lock screen can be dragged.

The screen uses `font-size: 32px` and every size inside is in `em`, so `1em` = 32px = one tenth of the screen's width.
That makes it easy to think in proportions: a `1.8em` icon is 18% of the screen wide.

### Bending a flat screen onto tilted glass
In the mockup the screen is a slanted four-sided shape, not a rectangle. CSS can bend a rectangle into any
four-sided shape with a **perspective warp**, written as `matrix3d(…)` (16 numbers).

1. Measure the screen's four corners in the phone image (863 × 1584 px):
   top-left `(230.5, 221)`, top-right `(698.5, 312.5)`, bottom-right `(698.5, 1367.4)`, bottom-left `(230.5, 1353)`.
2. Solve for the warp that sends the rectangle's corners `(0,0) (320,0) (320,568) (0,568)` to those four points.
3. Write it as `transform: scale(var(--z)) matrix3d(…)`. The `scale(var(--z))` shrinks everything along with the picture.

If you ever swap in a different mockup, only the four corners change. This Python snippet (needs `numpy`) prints
the new `matrix3d`:

```python
import numpy as np
w, h = 320, 568                                                 # the flat screen
corners = [(230.5, 221), (698.5, 312.5), (698.5, 1367.4), (230.5, 1353)]  # TL, TR, BR, BL in the image
A, b = [], []
for (x, y), (X, Y) in zip([(0, 0), (w, 0), (w, h), (0, h)], corners):
    A += [[x, y, 1, 0, 0, 0, -x * X, -y * X], [0, 0, 0, x, y, 1, -x * Y, -y * Y]]
    b += [X, Y]
a, b2, c, d, e, f, g, h2 = np.linalg.solve(A, b)
print(f"matrix3d({a},{d},0,{g},{b2},{e},0,{h2},0,0,1,0,{c},{f},0,1)")
```

### Size and layout
`--z` is the zoom level of the whole lineup: `.28` on desktop, smaller on phones (media queries in section `11.`).
Each phone is `863px × --z` wide; `.dev + .dev { margin-left: … }` overlaps them slightly; `z-index` keeps the
middle one in front. The tap-to-zoom view makes a copy with a bigger `--z`.

---

## 7. JavaScript: the behaviour

Everything lives in one `<script>` at the bottom, wrapped in `(function () { … })();`, a function that runs
immediately and keeps its variables private so nothing clashes. It's split into numbered parts.

### Concepts you'll see in every part
- **Finding elements:** `document.getElementById("theme")`, `document.querySelector(".lock")` (first match),
  `document.querySelectorAll(".js-time")` (all matches).
- **Reacting to things:** `element.addEventListener("click", function (event) { … })`.
- **Changing the page:** `el.textContent = "…"` (safe: always plain text), `el.hidden = true`,
  `el.classList.add("open")`, `el.setAttribute("aria-selected", "true")`.
- **Talking to CSS:** `el.style.setProperty("--h", "90deg")` sets a CSS variable that a CSS rule then uses.
  JavaScript does the maths, CSS does the drawing.
- **`js-` classes** (like `js-time`) mean "JavaScript uses this", so you know not to rename them for styling.

### Part 1: the clock
`Intl.DateTimeFormat` with `timeZone: "Asia/Manila"` formats the time for Manila wherever the visitor is.
`setInterval(tick, 1000)` runs `tick` every second. It writes the time into every `.js-time` element and sets
`--h`, `--m`, `--s` on each clock face: hour hand = `hour × 30° + minute × 0.5°`, minute hand = `minute × 6°`,
second hand = `second × 6°`.

### Part 2: the nav highlight
An `IntersectionObserver` watches each section and reports when it crosses the middle of the screen
(`rootMargin: "-45% 0px -50% 0px"`). The matching nav link gets `aria-current="true"`, and the CSS darkens it.

### Part 3: the theme picker
The `<select>` sets `data-theme` on `<html>` and saves the choice with `localStorage.setItem("theme", …)`.
`localStorage` can fail (private windows), so every use is wrapped in `try { … } catch (e) { }`.

### Part 4: Bandcamp
The "facade" pattern: the page shows a cover and a play button, and only creates Bandcamp's `<iframe>` when someone
presses play. Until then, the page never contacts Bandcamp. The play buttons are real links to Bandcamp, so they
still work if JavaScript is off; `event.preventDefault()` stops the link when JavaScript can do better.

### Part 5: slide to unlock
- The lock screen only shows when JavaScript is on: the `<head>` script adds a `js` class to `<html>`, and the CSS
  rule is `.js .lock { display: flex }`.
- While locked, the home screen gets `inert`, so its icons can't be clicked or tabbed to.
- **Dragging:** `pointerdown` remembers where you started; `setPointerCapture` keeps the events coming even if your
  finger leaves the knob; `pointermove` moves the knob with `translateX`; `pointerup` either unlocks (far enough)
  or snaps back.
- Because the phone is zoomed and tilted, a mouse movement of 10px isn't 10px on the phone. The code divides by
  `track.getBoundingClientRect().width / track.offsetWidth` (shown size ÷ real size) to convert.
- A tap without dragging, or pressing Enter, also unlocks.

### Part 6: the address book
Each name is a `<button role="tab">` pointing at its card with `aria-controls`. On click, the chosen button gets
`aria-selected="true"`, its card loses `hidden`, and every other card gets `hidden`.

### Part 7: films
Explained in [section 8](#8-data-from-other-sites-letterboxd-and-bandcamp). Worth noticing in the code: it builds every
ticket with `document.createElement` and `textContent`, never by pasting text into `innerHTML`. Review text comes from
another website, and `textContent` guarantees it's shown as plain text, never run as code.

### Part 8: tap a phone to zoom
`phone.cloneNode(true)` copies a phone, including its screen. The copy gets a bigger `--z`, worked out from the
window size so it always fits, and goes into the `.zoom` overlay. `document.body.style.overflow = "hidden"` stops
the page scrolling behind it. Closing it (×, Esc, or clicking the backdrop) puts keyboard focus back on the
phone you opened, so keyboard users don't lose their place.

---

## 8. Data from other sites: Letterboxd and Bandcamp

### Why not just load Letterboxd directly?
Browsers block a page from reading another website's data unless that website allows it. This rule is called
**CORS** (cross-origin resource sharing). Letterboxd doesn't allow it, so the page can't simply `fetch` your feed.

### How the Films section gets your diary
```
Letterboxd RSS feed ──► proxy ──► your page (live, every visit)
        │
        └──► GitHub Action (daily) ──► films.json ──► your page (backup)
```
1. The page first shows `films.json` (instant).
2. It then tries live sources in order: your own Cloudflare Worker (`MY_PROXY`, if set), then two public proxies.
   A **proxy** fetches the feed on the page's behalf and adds the "allowed" header. Each try gives up after
   7 seconds (`AbortController`).
3. The feed is **RSS**, a standard XML format. `DOMParser` turns it into a tree, and the code reads each item's
   `letterboxd:filmTitle`, `memberRating`, `watchedDate` and so on. The review is HTML inside `<description>`;
   it's parsed separately, skipping the poster and "Watched on…" lines, and spotting spoiler warnings.
4. If everything fails, whatever was already showing stays. Nothing breaks.

### The GitHub Action
`.github/workflows/letterboxd.yml` tells GitHub: "every day at 02:17 UTC, start a Linux machine, run
`python3 scripts/letterboxd.py kerthfyadao films.json`, and if `films.json` changed, commit it and republish the site."
The Python script does the same parsing as the browser, using `urllib` (download) and `xml.etree` (parse).
You can run it yourself to see what it does. Open the **Actions** tab on GitHub to see every run and its log.

### Cloudflare Worker
`cloudflare-worker.js` is a tiny program that runs on Cloudflare's servers for free. When your page asks it, it fetches
*only your* feed and returns it with `Access-Control-Allow-Origin: *`, the "allowed" header. It caches the result
for 5 minutes. It's your own private proxy, more reliable than public ones.

### Bandcamp
Bandcamp offers an official embeddable player (an `<iframe>`), so no proxy is needed. The URL's settings choose its
look: `size=large/bgcol=333333/linkcol=4ec5ff/tracklist=false`.

---

## 9. Accessibility and performance

Small choices that make the site work for everyone:

- **Real buttons and links:** anything clickable is a `<button>` or an `<a>`, so it works with a keyboard and
  screen readers.
- **Visible focus:** `:focus-visible` draws a blue outline when someone tabs with the keyboard.
- **Skip link:** the first Tab press shows "Skip to content".
- **`aria-hidden="true"`** hides decorative copies (the fake terminal, the phone screens) from screen readers;
  `aria-label` names things that have no visible text.
- **Reduced motion:** every animation stops for people who ask for less motion.
- **Text stays text:** headings and paragraphs are real text, not pictures of text, so they're searchable,
  translatable and sharp at any zoom.
- **Fast loading:** no frameworks, gradients instead of image textures, Bandcamp loaded only on demand, and photos
  hidden until they've loaded (no layout jumps).

---

## 10. Changing things safely

1. Make one change at a time.
2. Save, refresh the browser, check it at phone width too (DevTools device toolbar).
3. Look at the Console for red errors.
4. Commit with a short message describing what you did. If something breaks, undo it from GitHub's history.

**Common mistakes**
- **A missing closing tag** (`</div>`, `</a>`) can swallow everything after it. VS Code highlights matching pairs.
- **Capital letters in file names:** GitHub Pages treats `Photo.JPG` and `photo.jpg` as different files.
  Keep everything lowercase.
- **A typo in a CSS property** is silently ignored. DevTools shows it with a yellow warning triangle.
- **Missing semicolon or bracket in JavaScript** stops the whole script. The Console tells you the line number.
- **Renaming a `js-` class or an `id`** that JavaScript or a link uses. Search the file for the old name first.

---

## 11. Exercises

Start small. Each one teaches a piece of the site.

1. **Change the link colour** everywhere by editing `--link` in section `0.`.
2. **Make the headline say something else.** Search `hello, human.`.
3. **Add a repo** to the GitHub section by copying an `<li>` line.
4. **Add a photo with a caption** to the cork board.
5. **Write a note** from `notes/_template.html` and link it from the homepage.
6. **Add a contact to the address book**, for example your iPod collection.
7. **Change the lock screen** to show seconds. Hint: JavaScript part 1, `lockTimeFmt`, add `second: "2-digit"`.
8. **Give the sticky note a different colour.** Find `.sticky` in section `8c.`.
9. **Add a new icon** to the sprite (draw it in a free SVG editor with a 24×24 canvas), then use it on the iPhone home screen.
10. **Switch on the Favorites section** from the `TEMPLATE` comment and add it to the nav.
11. **Set up the Cloudflare Worker** and paste its address into `MY_PROXY`. Watch for the green "Live" dot.
12. **Bigger challenge:** add a sixth phone to the lineup with a new iOS 6 app on its screen (copy one `<a class="dev …">`
    block and invent the screen).

---

## 12. Glossary

| Term | Meaning |
|---|---|
| **Element** | One piece of HTML, like `<p>…</p>` |
| **Attribute** | Extra info on an element: `href`, `class`, `alt` |
| **Selector** | The part of a CSS rule that picks elements: `.ticket .tk-title` |
| **Cascade / specificity** | How CSS decides which rule wins when two disagree |
| **Custom property / token** | A CSS variable like `--link`, read with `var(--link)` |
| **Pseudo-element** | `::before` / `::after`, extra layers made by CSS |
| **Media query** | `@media (…)`: rules that only apply on certain screens |
| **Flexbox / Grid** | CSS layout systems for rows, and rows-and-columns |
| **Viewport** | The visible part of the browser window |
| **DOM** | The page's live tree of elements that JavaScript reads and changes |
| **Event** | Something that happens (click, key press, drag) that code can react to |
| **fetch** | JavaScript's way to download data from a URL |
| **CORS** | The browser rule that blocks reading other sites' data without permission |
| **Proxy** | A middleman server that fetches something on your behalf |
| **RSS** | A standard XML format for feeds of updates |
| **JSON** | A simple text format for data, like `films.json` |
| **iframe** | A window into another site, embedded in your page (the Bandcamp player) |
| **GitHub Pages** | GitHub's free hosting for static sites |
| **GitHub Action / workflow** | A script GitHub runs for you on a schedule or after a push |
| **Commit / push** | Save a snapshot of your changes / send it to GitHub |
| **Skeuomorphism** | Designing digital things to look like real materials: leather, metal, paper |

**Keep learning:** [MDN Learn web development](https://developer.mozilla.org/en-US/docs/Learn_web_development),
[CSS-Tricks guides to Flexbox and Grid](https://css-tricks.com/guides/),
and the games [Flexbox Froggy](https://flexboxfroggy.com) and [Grid Garden](https://cssgridgarden.com).
