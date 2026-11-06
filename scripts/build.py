"""Build the static site: parse fragen.md into questions.json and copy site/ into dist/."""

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "fragen.md"
SITE_DIR = ROOT / "site"
DIST_DIR = ROOT / "dist"

LETTERS = ["A", "B", "C", "D"]
HEADING = re.compile(r"^###\s+(\d+)\.\s+(.+?)\s*$")
OPTION = re.compile(r"^-\s+([A-D])\)\s+(.+?)\s*$")
ANSWER = re.compile(r"^\*\*Richtige Antwort:\*\*\s*([A-D])\s*$")
EXPLANATION = re.compile(r"^\*\*Erklärung:\*\*\s*(.+?)\s*$")
BOLD = re.compile(r"\*\*(.+?)\*\*")


def parse(text: str) -> tuple[dict, list[dict]]:
    meta = {"title": "", "subtitle": "", "note": ""}
    questions: list[dict] = []
    current = None

    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if match := HEADING.match(line):
            current = {
                "id": int(match[1]),
                "question": match[2],
                "options": {},
                "answer": None,
                "explanation": None,
                "line": lineno,
            }
            questions.append(current)
        elif line.startswith("## ") or line == "---":
            current = None
        elif current is None:
            if line.startswith("# ") and not meta["title"]:
                meta["title"] = line[2:].strip()
            elif line.startswith("*") and not line.startswith("**") and line.endswith("*") and not meta["subtitle"]:
                meta["subtitle"] = line.strip("*").strip()
            elif line.startswith(">") and not meta["note"]:
                meta["note"] = BOLD.sub(r"\1", line.lstrip(">").strip())
        elif match := OPTION.match(line):
            current["options"][match[1]] = match[2]
        elif match := ANSWER.match(line):
            current["answer"] = match[1]
        elif match := EXPLANATION.match(line):
            current["explanation"] = match[1]

    return meta, questions


def validate(questions: list[dict]) -> list[str]:
    errors = []
    if not questions:
        errors.append("No questions found.")
    seen_ids = set()
    for q in questions:
        where = f"Line {q['line']} (question {q['id']})"
        if q["id"] in seen_ids:
            errors.append(f"{where}: duplicate question number.")
        seen_ids.add(q["id"])
        if sorted(q["options"]) != LETTERS:
            errors.append(f"{where}: expected options A-D, found {sorted(q['options']) or 'none'}.")
        if q["answer"] is None:
            errors.append(f"{where}: missing '**Richtige Antwort:** X'.")
        if q["explanation"] is None:
            errors.append(f"{where}: missing '**Erklärung:** ...'.")
    return errors


def main() -> int:
    meta, questions = parse(SOURCE.read_text(encoding="utf-8"))
    errors = validate(questions)
    if errors:
        print(f"{SOURCE.name} is invalid:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    for q in questions:
        del q["line"]

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    shutil.copytree(SITE_DIR, DIST_DIR)
    (DIST_DIR / "questions.json").write_text(
        json.dumps({**meta, "questions": questions}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Built {len(questions)} questions into {DIST_DIR.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
