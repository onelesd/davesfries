# Dave's Fries - 90s Movie Review Site

A 90s-style static HTML site. One long-scrolling page of curated movie reviews, generated from markdown files via a Python build script.

## Quick Reference

```bash
source .venv/bin/activate          # activate venv (Python 3.13)
python build.py                    # one-shot build → dist/index.html
python build.py --watch            # dev server with live reload at http://localhost:8000
python add-movie.py <imdb-url> [rating]  # generate movie .md from IMDB link
```

## Project Structure

```
build.py          # Reads movies/*.md, sorts by year, renders into template → dist/index.html
add-movie.py      # Fetches title/year/director from IMDB GraphQL API, writes movies/<slug>.md
template.html     # HTML shell with {{ movies }} and {{ count }} placeholders
assets/style.css  # 90s aesthetic (starfield bg, neon colors, Comic Neue, rainbow HRs)
movies/*.md       # One file per movie: YAML frontmatter + markdown review body
dist/             # Generated output (gitignored)
```

## Movie File Format

Each movie is a markdown file in `movies/` with YAML frontmatter:

```markdown
---
title: "Blade Runner"
year: 1982
director: "Ridley Scott"
rating: 5
---
Review text in markdown goes here.
```

- **title**: Movie title (quoted if it contains special chars)
- **year**: Release year (used for sorting — ascending)
- **director**: Director name(s), comma-separated for multiple
- **rating**: 1-5 (rendered as unicode stars ★★★★☆)
- **body**: Markdown rendered to HTML for the review blurb

## Build Pipeline

`build.py` does: read all `movies/*.md` → parse YAML frontmatter + render markdown body → sort by (year, title) → inject into `template.html` replacing `{{ movies }}` and `{{ count }}` → copy `assets/` into `dist/assets/` → write `dist/index.html`.

## add-movie.py

Uses IMDB's public GraphQL API (`https://graphql.imdb.com/`) to fetch movie metadata. Extracts the `tt` ID from the URL, queries for title, year, and director(s), generates a slugified filename. The review body is left empty for manual editing.

## Dependencies

Managed via `requirements.txt` and a local `.venv`:
- `markdown` — markdown to HTML rendering
- `pyyaml` — YAML frontmatter parsing
- `livereload` — watch mode dev server
- `requests` — HTTP client for IMDB API

## Style

90s GeoCities-inspired: dark starfield background (CSS radial gradients), Comic Neue font, neon magenta/cyan/yellow palette, rainbow gradient `<hr>` separators, `<marquee>` subtitle, fake visitor counter, glowing cyan-bordered movie cards.

## Adding a Movie

1. Run `python add-movie.py "https://www.imdb.com/title/tt0078748/" 5`
2. Edit the generated `movies/<slug>.md` to add your review
3. Run `python build.py` (or use `--watch` mode)
