#!/usr/bin/env python3
"""Fetch movie info from IMDB and generate a markdown file in movies/."""

import json
import re
import sys
import unicodedata

import requests

GRAPHQL_URL = "https://graphql.imdb.com/"

QUERY = """
query ($id: ID!) {
  title(id: $id) {
    titleText { text }
    releaseYear { year }
    directors: credits(first: 5, filter: {categories: ["director"]}) {
      edges {
        node {
          name { nameText { text } }
        }
      }
    }
  }
}
"""


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def extract_title_id(url: str) -> str:
    """Extract the tt-prefixed ID from an IMDB URL."""
    match = re.search(r"(tt\d+)", url)
    if not match:
        raise ValueError(f"Could not find IMDB title ID in: {url}")
    return match.group(1)


def fetch_movie(title_id: str) -> dict:
    """Fetch movie data from IMDB's GraphQL API."""
    resp = requests.post(
        GRAPHQL_URL,
        json={"query": QUERY, "variables": {"id": title_id}},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    resp.raise_for_status()

    data = resp.json().get("data", {}).get("title")
    if not data:
        raise ValueError(f"No results for {title_id}")

    title = data["titleText"]["text"]
    year = data["releaseYear"]["year"]

    director_edges = data.get("directors", {}).get("edges", [])
    directors = [e["node"]["name"]["nameText"]["text"] for e in director_edges]
    director = ", ".join(directors) if directors else "Unknown"

    return {"title": title, "year": year, "director": director}


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python add-movie.py <imdb-url> [rating]")
        print("  rating: 1-5 (default: 0, fill in later)")
        sys.exit(1)

    url = sys.argv[1]
    rating = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    if not re.match(r"https?://(www\.)?imdb\.com/title/tt\d+", url):
        print("Error: URL must be an IMDB title page (e.g. https://www.imdb.com/title/tt0083658/)")
        sys.exit(1)

    title_id = extract_title_id(url)
    print(f"Fetching {title_id}...")
    movie = fetch_movie(title_id)

    slug = slugify(movie["title"])
    filepath = f"movies/{slug}.md"

    content = f"""---
title: "{movie['title']}"
year: {movie['year']}
director: "{movie['director']}"
rating: {rating}
---
"""

    with open(filepath, "w") as f:
        f.write(content)

    print(f"Created {filepath}")
    print(f"  Title: {movie['title']}")
    print(f"  Year: {movie['year']}")
    print(f"  Director: {movie['director']}")
    print(f"  Rating: {rating}")
    print(f"\nEdit {filepath} to add your review below the frontmatter.")


if __name__ == "__main__":
    main()
