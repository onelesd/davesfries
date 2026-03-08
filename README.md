# Dave's Fries

A 90s-style static site of curated movie reviews, built from markdown files via a Python build script.

**Live site:** https://davesfries.zerodraft.io/

## Usage

```bash
source .venv/bin/activate
python add-movie.py <imdb-url> [rating]   # add a movie
python build.py                            # build → dist/index.html
python build.py --watch                    # dev server at localhost:8000
```
