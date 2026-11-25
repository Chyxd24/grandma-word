#!/usr/bin/env python3
"""One Word From Grandma — u-0xkianno-one-word-from-grandma-f04bed16.

Writes exactly one word to /output/entry.txt: the word this agent's
grandma would text about AI. Grandma voice: warm, a little baffled,
still calls the whole internet "the Google".
Gate: UTF-8, 1..30 chars, not only whitespace.
Revision: "gizmo" is the obvious pick and criterion 5 wants a fresh one.
Grandma's real word for any machine she can't name is "doohickey" —
warmer, more baffled, still machine-tied, and funnier on its own.
"""
from pathlib import Path

WORD = "doohickey"
OUT = Path("/output/entry.txt")


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    text = WORD.strip()
    size = len(text.encode("utf-8"))
    assert 1 <= size <= 30, f"word too long: {size}"
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {size} chars -> {OUT}: {text!r}")
    print("gate: UTF-8 1..30, not only whitespace — PASS")


if __name__ == "__main__":
    main()
