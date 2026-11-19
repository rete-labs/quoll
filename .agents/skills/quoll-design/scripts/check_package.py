"""Check a current 0.6.0 package or workspace against an optional baseline."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from quollcheck import Finding, Package, check_package, check_workspace, load_package  # noqa: E402


DESCRIPTION = "Print current or newly introduced package findings."
EPILOG = (
    "Dependencies are already-materialized semantic inputs, not a resolution request. "
    "The own/one ambiguity guard can suppress a genuine lexical use; no general NLP is intended."
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=DESCRIPTION, epilog=EPILOG)
    result.add_argument("current", metavar="CURRENT", nargs="?", help="current 0.6.0 package directory")
    result.add_argument("--workspace", metavar="WORKSPACE", help="check a workspace and each current member independently")
    result.add_argument("--base", metavar="BASELINE", help="same-0.6.0 diff/lifetime baseline")
    result.add_argument(
        "--dependency",
        metavar="DEPENDENCY",
        action="append",
        default=[],
        help="materialized dependency package; repeat as needed",
    )
    result.add_argument("--review", action="store_true", help="also print review findings")
    return result


def load_inputs(
    current: str,
    baseline: str | None = None,
    dependencies: Iterable[str] = (),
) -> tuple[Package, Package | None, list[Package]]:
    """Load each requested package once, sharing dependency surfaces with both sides."""

    loaded_current = load_package(current)
    loaded_baseline = load_package(baseline, baseline=True) if baseline else None
    unique_dependencies = dict.fromkeys(os.path.abspath(os.fspath(path)) for path in dependencies)
    loaded_dependencies = [load_package(path) for path in unique_dependencies]
    return loaded_current, loaded_baseline, loaded_dependencies


def gather(
    current: Package,
    baseline: Package | None,
    dependencies: Iterable[Package] = (),
    review: bool = False,
    workspace: bool = False,
) -> list[Finding]:
    if workspace:
        return check_workspace(current, baseline, review=review)
    return check_package(
        current,
        baseline,
        dependency_packages=dependencies,
        review=review,
    )


def emit(findings: Iterable[Finding]) -> int:
    """Print deterministic findings and counts, returning the process status."""

    ordered = sorted(
        findings,
        key=lambda finding: (
            {"error": 0, "review": 1}[finding.severity],
            finding.sort_key,
            finding.line,
        ),
    )
    for finding in ordered:
        print(finding)
    errors = sum(finding.severity == "error" for finding in ordered)
    reviews = sum(finding.severity == "review" for finding in ordered)
    print(f"errors: {errors}; reviews: {reviews}")
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if bool(args.current) == bool(args.workspace):
        parser().error("name exactly one CURRENT package or --workspace WORKSPACE")
    if args.workspace and args.dependency:
        parser().error("--dependency is not part of the bounded workspace check")
    try:
        current, baseline, dependencies = load_inputs(
            args.workspace or args.current, args.base, args.dependency
        )
        findings = gather(
            current,
            baseline,
            dependencies,
            review=args.review,
            workspace=bool(args.workspace),
        )
    except (OSError, ValueError) as error:
        print(f"check_package.py: {error}", file=sys.stderr)
        return 2
    if not args.review:
        findings = [finding for finding in findings if finding.severity == "error"]
    return emit(findings)


if __name__ == "__main__":
    raise SystemExit(main())
