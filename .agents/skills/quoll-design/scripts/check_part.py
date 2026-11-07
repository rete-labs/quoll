"""Migration shim for the retired module-at-a-time checker."""

import sys


def main() -> int:
    print(
        "check_part.py is obsolete; use "
        "check_package.py CURRENT [--base BASELINE] [--review].",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
