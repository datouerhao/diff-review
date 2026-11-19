"""Usage: python3 -m diff_review [patch-file]"""

import argparse
import json
from pathlib import Path
import sys

from .parser import parse_diff


def main():
    parser = argparse.ArgumentParser(description="Parse a unified text diff as JSON")
    parser.add_argument("patch", nargs="?", help="UTF-8 patch file; defaults to stdin")
    args = parser.parse_args()
    try:
        text = Path(args.patch).read_text(encoding="utf-8") if args.patch else sys.stdin.read()
        result = parse_diff(text)
    except (OSError, UnicodeError, ValueError) as error:
        print("diff-review: {}".format(error), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
