#!/usr/bin/env python3
"""Generate a human-friendly summary for changes in the entries CSV.

The script expects two CSV files with the same format as
```
<phrase>,<reading>
```
and prints a Markdown summary that highlights added, removed, and updated
readings. The intent is to make GitHub release notes easier to read than the
raw line-based diff produced by Git.
"""
from __future__ import annotations

import argparse
import csv
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

Entry = Tuple[str, str]


def load_entries(path: Path) -> "OrderedDict[str, str]":
    """Load the phrase -> reading mapping from a CSV file.

    - Uses UTF-8 with BOM support.
    - Ignores blank lines.
    """

    entries: "OrderedDict[str, str]" = OrderedDict()

    if not path.exists():
        return entries

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for row_number, row in enumerate(reader, start=1):
            if not row:
                continue

            if len(row) < 2:
                # Treat single-column rows as having an empty reading.
                phrase = row[0].strip()
                reading = ""
            else:
                phrase = row[0].strip()
                reading = row[1].strip()

            if not phrase:
                # Skip entries without a phrase.
                continue

            # Keep the first occurrence to preserve ordering.
            if phrase not in entries:
                entries[phrase] = reading

    return entries


def collect_changes(
    before: "OrderedDict[str, str]", after: "OrderedDict[str, str]"
) -> Tuple[List[Tuple[str, str, str]], List[Entry], List[Entry]]:
    """Return updated, added, removed entries.

    The updated list contains (phrase, before_reading, after_reading).
    """

    before_keys = set(before.keys())
    after_keys = set(after.keys())

    updated: List[Tuple[str, str, str]] = []
    for phrase in before_keys & after_keys:
        prev = before[phrase]
        curr = after[phrase]
        if prev != curr:
            updated.append((phrase, prev, curr))

    added = [(phrase, after[phrase]) for phrase in after_keys - before_keys]
    removed = [(phrase, before[phrase]) for phrase in before_keys - after_keys]

    updated.sort(key=lambda item: item[0])
    added.sort(key=lambda item: item[0])
    removed.sort(key=lambda item: item[0])

    return updated, added, removed


def format_section(title: str, lines: Iterable[str]) -> List[str]:
    section_lines: List[str] = []
    buffered = list(lines)
    if not buffered:
        return section_lines

    section_lines.append(f"### {title}")
    section_lines.extend(buffered)
    section_lines.append("")
    return section_lines


def format_summary(
    csv_path: Path,
    updated: List[Tuple[str, str, str]],
    added: List[Entry],
    removed: List[Entry],
    limit: int,
) -> str:
    lines: List[str] = []

    lines.append(f"Changes in `{csv_path}`")
    lines.append("")

    if updated:
        shown = updated[:limit]
        lines.extend(
            format_section(
                f"Updated readings ({len(updated)})",
                (
                    f"- {phrase}\n"
                    f"  - before: `{before}`\n"
                    f"  - after:  `{after}`"
                    for phrase, before, after in shown
                ),
            )
        )
        if len(updated) > limit:
            lines.append(f"...and {len(updated) - limit} more updated entries.")
            lines.append("")

    if added:
        shown = added[:limit]
        lines.extend(
            format_section(
                f"Added entries ({len(added)})",
                (f"- {phrase} → `{reading}`" for phrase, reading in shown),
            )
        )
        if len(added) > limit:
            lines.append(f"...and {len(added) - limit} more added entries.")
            lines.append("")

    if removed:
        shown = removed[:limit]
        lines.extend(
            format_section(
                f"Removed entries ({len(removed)})",
                (f"- {phrase} → `{reading}`" for phrase, reading in shown),
            )
        )
        if len(removed) > limit:
            lines.append(f"...and {len(removed) - limit} more removed entries.")
            lines.append("")

    result = "\n".join(lines).strip()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarise CSV changes for releases")
    parser.add_argument("before", type=Path, help="Path to the previous CSV snapshot")
    parser.add_argument("after", type=Path, help="Path to the latest CSV snapshot")
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of entries to show per section (default: 50)",
    )

    args = parser.parse_args()

    before_entries = load_entries(args.before)
    after_entries = load_entries(args.after)

    updated, added, removed = collect_changes(before_entries, after_entries)

    if not (updated or added or removed):
        return

    summary = format_summary(args.after, updated, added, removed, args.limit)
    print(summary)


if __name__ == "__main__":
    main()
