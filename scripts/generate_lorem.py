#!/usr/bin/env python3
"""
Generate a lorem ipsum Markdown file according to settings.json.

Usage:
  python scripts/generate_lorem.py                # reads settings.json in repo root
  python scripts/generate_lorem.py --settings path/to/settings.json
"""
from __future__ import annotations
import argparse
import json
import random
import textwrap
from pathlib import Path

# Short list of lorem words to build paragraphs from (cycled).
LOREM_WORDS = (
    "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt "
    "ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco "
    "laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in "
    "voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat "
    "non proident sunt in culpa qui officia deserunt mollit anim id est laborum"
).split()

DEFAULT_SETTINGS = {
    "output_path": "content/lorem.md",
    "characters": 1000,
    "paragraphs": 3,
    "max_line_length": 80,
    "include_title": True,
    "title_characters": 40,
    "seed": None
}

def load_settings(path: Path) -> dict:
    if not path.exists():
        print(f"Settings file {path} not found — using defaults.")
        return DEFAULT_SETTINGS.copy()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # merge with defaults
    settings = DEFAULT_SETTINGS.copy()
    settings.update(data or {})
    return settings

def gen_title(char_count: int, rng: random.Random) -> str:
    if char_count <= 0:
        return ""
    words = []
    while len(" ".join(words)) < char_count:
        w = rng.choice(LOREM_WORDS)
        words.append(w.capitalize() if not words else w)
    title = " ".join(words)[:char_count].rstrip()
    # avoid trailing punctuation
    return title.strip()

def gen_paragraph(target_chars: int, rng: random.Random) -> str:
    # Build a paragraph by cycling words, adding periods occasionally to create sentences.
    if target_chars <= 0:
        return ""
    words = []
    char_len = 0
    sentence_len = rng.randint(8, 16)
    words_in_sentence = 0
    while char_len < target_chars:
        w = rng.choice(LOREM_WORDS)
        # If start of sentence capitalize.
        if words_in_sentence == 0:
            w = w.capitalize()
        words.append(w)
        words_in_sentence += 1
        char_len = len(" ".join(words))
        if words_in_sentence >= sentence_len:
            # end sentence
            words[-1] = words[-1] + "."
            words_in_sentence = 0
            sentence_len = rng.randint(6, 20)
    # ensure paragraph ends with a period
    paragraph = " ".join(words)
    paragraph = paragraph.strip()
    if not paragraph.endswith("."):
        paragraph += "."
    return paragraph

def distribute_chars(total_chars: int, paragraphs: int) -> list[int]:
    if paragraphs <= 0:
        return []
    base = total_chars // paragraphs
    remainder = total_chars % paragraphs
    distribution = [base + (1 if i < remainder else 0) for i in range(paragraphs)]
    return distribution

def render_markdown(title: str, paragraphs: list[str], max_line_len: int) -> str:
    parts = []
    if title:
        parts.append(f"# {title}")
        parts.append("")  # blank line
    for p in paragraphs:
        wrapped = textwrap.fill(p, width=max_line_len)
        parts.append(wrapped)
        parts.append("")
    # remove the trailing blank line
    if parts and parts[-1] == "":
        parts.pop()
    return "\n".join(parts)

def main():
    parser = argparse.ArgumentParser(description="Generate lorem ipsum markdown from settings JSON.")
    parser.add_argument("--settings", "-s", default="settings.json", help="Path to settings.json")
    args = parser.parse_args()

    settings = load_settings(Path(args.settings))
    rng = random.Random(settings.get("seed"))

    total_chars = int(settings.get("characters", 0))
    paragraphs = int(settings.get("paragraphs", 1))
    max_line_length = int(settings.get("max_line_length", 80))
    include_title = bool(settings.get("include_title", True))
    title_chars = int(settings.get("title_characters", 40))
    output_path = Path(settings.get("output_path", "content/lorem.md"))

    # If characters is small, keep at least a few words per paragraph
    if total_chars < paragraphs * 20:
        # fallback: ensure at least 20 chars per paragraph
        total_chars = max(total_chars, paragraphs * 20)

    distribution = distribute_chars(total_chars, paragraphs)
    paragraphs_text = [gen_paragraph(n, rng) for n in distribution]
    title_text = gen_title(title_chars, rng) if include_title else ""

    md = render_markdown(title_text, paragraphs_text, max_line_length)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md, encoding="utf-8")
    print(f"Wrote {len(md)} chars to {output_path}")

if __name__ == "__main__":
    main()