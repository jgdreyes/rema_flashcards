#!/usr/bin/env python3
"""
Generate (or prune) per-belt Streamlit page files under pages/curriculum/.

Each file gives Streamlit a real route at /curriculum/<belt_key> so the
browser back button works natively.

Usage:
    python bin/dev/generate_belt_pages.py

Run this whenever a belt is added to or removed from ripple_effect_curriculum.json.
"""

import json
import os

REPO_ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CURRICULUM   = os.path.join(REPO_ROOT, "data", "ripple_effect_curriculum.json")
PAGES_DIR    = os.path.join(REPO_ROOT, "pages", "curriculum")
PAGE_TEMPLATE = """\
from pages.curriculum_page import _show_detail
_show_detail("{belt_key}")
"""


def main():
    with open(CURRICULUM) as f:
        belts = json.load(f)

    belt_keys = {belt["belt_key"] for belt in belts}
    os.makedirs(PAGES_DIR, exist_ok=True)

    # Create or overwrite a page file for each belt in the JSON
    for key in belt_keys:
        path = os.path.join(PAGES_DIR, f"{key}.py")
        content = PAGE_TEMPLATE.format(belt_key=key)
        with open(path, "w") as f:
            f.write(content)
        print(f"  [+] {os.path.relpath(path, REPO_ROOT)}")

    # Remove page files for belts no longer in the JSON
    for fname in os.listdir(PAGES_DIR):
        if not fname.endswith(".py"):
            continue
        key = fname[:-3]
        if key not in belt_keys:
            path = os.path.join(PAGES_DIR, fname)
            os.remove(path)
            print(f"  [-] {os.path.relpath(path, REPO_ROOT)}")

    print(f"\nDone. {len(belt_keys)} belt page(s) in pages/curriculum/")


if __name__ == "__main__":
    main()