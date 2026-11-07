"""Run only the targeted bare-compound and optional bare-word checks."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_package import EPILOG, emit, gather, load_inputs  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print bare compound findings; add --review for bare words.",
        epilog=EPILOG,
    )
    parser.add_argument("current", metavar="CURRENT", help="current v0.4 package directory")
    parser.add_argument("--base", metavar="BASELINE", help="committed package baseline")
    parser.add_argument("--review", action="store_true", help="also print bare-word reviews")
    args = parser.parse_args(argv)
    try:
        current, baseline, dependencies = load_inputs(args.current, args.base)
        findings = gather(current, baseline, dependencies, review=args.review)
    except (OSError, ValueError) as error:
        print(f"check_bare.py: {error}", file=sys.stderr)
        return 2
    rules = {"prose.bare-compound", "prose.bare-word"} if args.review else {"prose.bare-compound"}
    return emit(finding for finding in findings if finding.rule in rules)


if __name__ == "__main__":
    raise SystemExit(main())
