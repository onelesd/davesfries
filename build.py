#!/usr/bin/env python3
"""Build script for 90s movie review site."""

import argparse
import glob
import os
import shutil
import subprocess
import sys

import markdown
import yaml


def parse_movie(filepath: str) -> dict | None:
    """Parse a movie markdown file. Returns dict with frontmatter fields + 'body_html'."""
    with open(filepath, "r") as f:
        content = f.read()

    if not content.startswith("---"):
        print(f"Warning: {filepath} missing frontmatter, skipping")
        return None

    parts = content.split("---", 2)
    if len(parts) < 3:
        print(f"Warning: {filepath} malformed frontmatter, skipping")
        return None

    frontmatter = yaml.safe_load(parts[1])
    body_md = parts[2].strip()
    body_html = markdown.markdown(body_md)

    return {**frontmatter, "body_html": body_html}


def render_stars(rating: int) -> str:
    """Render a 1-5 rating as unicode stars."""
    filled = "\u2605" * rating
    empty = "\u2606" * (5 - rating)
    return filled + empty


def render_movie(movie: dict) -> str:
    """Render a single movie dict to an HTML fragment."""
    stars = render_stars(movie.get("rating", 0))
    return f"""    <div class="movie-card">
      <h2>{movie['title']} <span class="year">({movie['year']})</span></h2>
      <p class="meta">
        <span class="director">Directed by {movie['director']}</span>
        <span class="rating">{stars}</span>
      </p>
      <div class="review">{movie['body_html']}</div>
    </div>
    <hr class="rainbow">"""


def build() -> None:
    """Read all movie files, sort by year, render into template, write dist/index.html."""
    movie_files = sorted(glob.glob("movies/*.md"))
    if not movie_files:
        print("No movie files found in movies/")
        sys.exit(1)

    movies = []
    for f in movie_files:
        movie = parse_movie(f)
        if movie:
            movies.append(movie)

    movies.sort(key=lambda m: (m.get("added", ""), m.get("year", 0), m.get("title", "")), reverse=True)

    movie_html = "\n".join(render_movie(m) for m in movies)

    with open("template.html", "r") as f:
        template = f.read()

    commit = os.environ.get("COMMIT_SHA", "")
    if not commit:
        try:
            commit = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True
            ).stdout.strip()
        except FileNotFoundError:
            pass
    commit = commit[:7] or "unknown"

    html = template.replace("{{ movies }}", movie_html)
    html = html.replace("{{ count }}", str(len(movies)))
    html = html.replace("{{ commit }}", commit)

    os.makedirs("dist", exist_ok=True)

    if os.path.isdir("assets"):
        dist_assets = os.path.join("dist", "assets")
        if os.path.isdir(dist_assets):
            shutil.rmtree(dist_assets)
        shutil.copytree("assets", dist_assets)

    with open("dist/index.html", "w") as f:
        f.write(html)

    print(f"Built dist/index.html with {len(movies)} movies")


def watch() -> None:
    """Watch for changes and serve with live reload."""
    from livereload import Server

    build()

    server = Server()
    server.watch("movies/*.md", build)
    server.watch("template.html", build)
    server.watch("assets/*", build)
    server.serve(root="dist", port=8000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build 90s movie site")
    parser.add_argument("--watch", action="store_true", help="Watch and serve with live reload")
    args = parser.parse_args()

    if args.watch:
        watch()
    else:
        build()
