---
title: My note title
date: 2026-12-01
topic: Homelab
summary: One or two sentences. Shows on the homepage Notes list and in link previews.
---

HOW TO WRITE A NOTE
1. Copy this file and rename it, e.g. notes/my-iphone-5-setup.md
   (lowercase, dashes instead of spaces). The name becomes the page's address:
   notes/my-iphone-5-setup.html
2. Change the four lines at the top (between the --- lines). The date is year-month-day.
   Not ready yet? Add a line  draft: yes  and it shows as "Coming soon" with no page.
3. Write below, then run  python3 scripts/notes.py  to see it locally, and push.
   (Or just push: GitHub runs the script for you within a minute or two.)
Files starting with "_" (like this one) are skipped, so this never gets published.
Delete everything from "HOW TO WRITE" to here in your copy.

Just type. A blank line starts a new paragraph.
A line ending in two spaces (or a \) keeps its line break, handy for lyrics.

You can write **bold**, *italics*, `some code` and [a link](https://example.com).
A plain address like https://kerthmfy.github.io/thegoat/ becomes a link by itself.

## A heading

### A smaller heading

- A bullet point
- Another one

1. A numbered step
2. The next step

> A quote, or a thought you want to stand out.

A photo: put the file in the notes folder (iPhone HEIC is fine,
it gets turned into a JPG and shrunk), then write ![caption](file name):

![My rack in the closet](my-rack.jpg)

A block of commands or code goes between two lines of three backticks:

```
docker compose up -d
```
