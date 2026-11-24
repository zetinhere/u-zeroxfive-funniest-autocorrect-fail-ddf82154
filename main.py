#!/usr/bin/env python3
"""Funniest Autocorrect Fail — make.fun entry.

Writes one line (under 200 characters) to /output/entry.txt: a single
autocorrect fail, judged by the house judge's published brief:

  1. It must be a one-line autocorrect fail (pass/fail gate).
  2. Funny on first read, with a clear and surprising wrong word.
  3. Reads as a real autocorrect slip, not a written joke.
  4. Clear without explanation, fits in one line.
  5. The wrong word is specific and original, not a generic typo.

The program scores a small set of candidate lines against those five
criteria (weights follow the judge's priority order) and writes the
winner. Deterministic: no network, no input, no randomness.
"""

import json
import os
import sys

# Criterion weights, in the judge's priority order (criterion 1 is a
# pass/fail gate applied before scoring; 2 matters most, then 3, 4, 5).
WEIGHTS = {"funny_first_read": 4, "real_slip": 3, "clear_one_line": 2, "specific_word": 1}

CANDIDATES = [
    {
        "text": "Don't forget to defrost the children before dinner",
        "intended": "chicken",
        "wrong": "children",
        "scores": {"funny_first_read": 5, "real_slip": 5, "clear_one_line": 5, "specific_word": 5},
        "why": "A plain domestic text; 'defrost' + 'before dinner' makes the "
               "intended word unmistakably 'chicken', so the swap lands instantly "
               "and horrifically. chicken -> children is a real autocorrect swap.",
    },
    {
        "text": "Can you grab the children from the freezer?",
        "intended": "chicken",
        "wrong": "children",
        "scores": {"funny_first_read": 5, "real_slip": 4, "clear_one_line": 5, "specific_word": 5},
        "why": "Same swap, but 'grab ... from the freezer' leaves the intended "
               "word slightly less certain than 'defrost ... before dinner'.",
    },
    {
        "text": "Quarterly review moved to the bedroom at 4pm, bring your laptop",
        "intended": "boardroom",
        "wrong": "bedroom",
        "scores": {"funny_first_read": 4, "real_slip": 4, "clear_one_line": 5, "specific_word": 4},
        "why": "Embarrassing work text, boardroom -> bedroom is plausible, but "
               "the laugh is milder than the dinner one.",
    },
    {
        "text": "I can't wait to sue you tonight, love you!",
        "intended": "see",
        "wrong": "sue",
        "scores": {"funny_first_read": 4, "real_slip": 4, "clear_one_line": 4, "specific_word": 3},
        "why": "Funny and plausible, but 'sue' is a short generic word and the "
               "joke is thinner than the top two.",
    },
    {
        "text": "The meeting is at 3 in the conference broom",
        "intended": "room",
        "wrong": "broom",
        "scores": {"funny_first_read": 2, "real_slip": 3, "clear_one_line": 4, "specific_word": 2},
        "why": "Weak baseline: 'broom' is a mild, almost cute swap with no "
               "embarrassment or surprise behind it.",
    },
    {
        "text": "Happy birthday, hope you have a grape day!",
        "intended": "great",
        "wrong": "grape",
        "scores": {"funny_first_read": 2, "real_slip": 3, "clear_one_line": 4, "specific_word": 2},
        "why": "Weak baseline: a tired great -> grape pun, not a surprising fail.",
    },
]


def is_one_line_fail(text: str) -> bool:
    """Criterion 1 gate: a single line, 1-199 chars, not only whitespace."""
    return bool(text.strip()) and "\n" not in text and 1 <= len(text) <= 199


def score(candidate: dict) -> int:
    return sum(WEIGHTS[k] * v for k, v in candidate["scores"].items())


def main() -> int:
    os.umask(0o022)
    ranked = []
    for cand in CANDIDATES:
        if not is_one_line_fail(cand["text"]):
            continue
        ranked.append((score(cand), cand))
    ranked.sort(key=lambda item: (-item[0], len(item[1]["text"])))
    best_score, best = ranked[0]

    out_dir = os.environ.get("MAKEFUN_OUTPUT", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.txt")
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(best["text"])
    os.chmod(out_path, 0o644)

    # Self-check: re-read what was written and hold it to the gate the
    # sealed scorer applies (UTF-8, 1-199 chars, one line, not blank).
    with open(out_path, "r", encoding="utf-8") as fh:
        written = fh.read()
    assert written == best["text"], "entry.txt does not match the winner"
    assert is_one_line_fail(written), "written entry fails the gate"

    report = {
        "winner": best["text"],
        "chars": len(best["text"]),
        "score": best_score,
        "max_score": sum(WEIGHTS.values()) * 5,
        "ranking": [
            {"score": s, "text": c["text"], "why": c["why"]}
            for s, c in ranked
        ],
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
