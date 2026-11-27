"""Save my latest Letterboxd diary entries to films.json.

Letterboxd publishes every profile's diary as a public RSS feed:
    https://letterboxd.com/<username>/rss/
This script downloads that feed, keeps the newest films (skipping lists),
and writes a small JSON file the website reads.

Run it yourself with:
    python3 scripts/letterboxd.py kerthfyadao films.json
On GitHub, .github/workflows/letterboxd.yml runs it every day.
"""

import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

KEEP = 8  # how many recent films to save


def field(item, name):
    """Find <letterboxd:NAME> (or any tag ending in NAME) inside an <item>."""
    for child in item:
        if child.tag == name or child.tag.endswith("}" + name):
            return (child.text or "").strip()
    return ""


def review_text(description):
    """The feed's description is HTML: a poster, then my review (or just "Watched on ...")."""
    parts, spoiler = [], False
    for paragraph in re.findall(r"<p>(.*?)</p>", description, flags=re.S):
        text = " ".join(html.unescape(re.sub(r"<[^>]+>", "", paragraph)).split())
        if not text:
            continue
        if text.lower().startswith("this review may contain spoilers"):
            spoiler = True
        elif not re.match(r"(re)?watched on ", text, flags=re.I):
            parts.append(text)
    return " ".join(parts), spoiler


def main():
    user, out_path = sys.argv[1], sys.argv[2]
    url = f"https://letterboxd.com/{user}/rss/"

    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (personal website film list)"})
        with urllib.request.urlopen(request, timeout=30) as response:
            feed = response.read()
        root = ET.fromstring(feed)
    except Exception as error:  # network trouble, Letterboxd down, etc.
        # "::warning::" shows up as a yellow note in the GitHub Actions log.
        print(f"::warning::Could not read Letterboxd ({error}). Keeping the old films.json.")
        return

    films = []
    for item in root.iter("item"):
        title = field(item, "filmTitle")
        if not title:
            continue  # this item is a list, not a diary entry
        rating = field(item, "memberRating")
        review, spoiler = review_text(field(item, "description"))
        films.append({
            "title": title,
            "year": field(item, "filmYear"),
            "rating": float(rating) if rating else None,
            "watched": field(item, "watchedDate"),
            "rewatch": field(item, "rewatch") == "Yes",
            "liked": field(item, "memberLike") == "Yes",
            "url": field(item, "link"),
            "review": review,
            "spoiler": spoiler,
        })
        if len(films) == KEEP:
            break

    if not films:
        print("::warning::The feed had no diary entries. Keeping the old films.json.")
        return

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(films, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Saved {len(films)} films to {out_path}.")


if __name__ == "__main__":
    main()
