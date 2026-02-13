"""Run tests and print a concise summary of total testcases and results.

This script runs pytest with `pytest-json-report`, writes `reports/report.json`
and prints a short human-readable summary (total/passed/failed/skipped/errors).
It returns the pytest exit code.
"""

import argparse
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List


REPORT_DIR = Path("reports")
REPORT_FILE = REPORT_DIR / "report.json"


def _build_pytest_cmd(extra_args: List[str], with_coverage: bool) -> List[str]:
    cmd = [sys.executable, "-m", "pytest"]
    # Pass through extra args (e.g., -k, -x)
    if extra_args:
        cmd.extend(extra_args)
    # Always enable json report
    cmd.extend(["--json-report", f"--json-report-file={REPORT_FILE}"])
    if with_coverage:
        cmd.extend(["--cov=./", "--cov-report=xml:coverage.xml", "--cov-report=html:htmlcov"])
    return cmd


def _print_summary(report_path: Path, no_list: bool = False) -> None:
    if not report_path.exists():
        print("No JSON report produced.")
        return

    try:
        data = json.loads(report_path.read_text())
    except Exception as exc:
        print("Could not read JSON report:", exc)
        return

    summary = data.get("summary", {})
    total = summary.get("total", "?")
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    skipped = summary.get("skipped", 0)
    errors = summary.get("errors", 0)

    print("\nTest Summary:")
    print(f"  Total:  {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Skipped:{skipped}")
    print(f"  Errors: {errors}")

    # Compact per-test listing for quick feedback
    if not no_list:
        tests = data.get("tests", [])
        if tests:
            print("\nPer-test results:")
            for t in tests:
                outcome = t.get("outcome", "?")
                nodeid = t.get("nodeid", "")
                print(f"  {outcome.upper():7} {nodeid}")


def main(argv: List[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(description="Run pytest with JSON report and optional coverage.")
    parser.add_argument("--no-list", dest="no_list", action="store_true", help="Do not print per-test listing")
    parser.add_argument("--with-coverage", dest="with_coverage", action="store_true", help="Run pytest with coverage reports")
    parser.add_argument(
        "--coverage-format",
        dest="coverage_format",
        choices=["lines", "branches"],
        default="lines",
        help="Which coverage metric to print in the summary (lines or branches)",
    )
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER, help="Arguments passed through to pytest")
    args = parser.parse_args(argv)

    REPORT_DIR.mkdir(exist_ok=True)
    extra = args.pytest_args or []
    cmd = _build_pytest_cmd(extra, args.with_coverage)

    print("Running:", " ".join(cmd))
    rc = subprocess.call(cmd)

    _print_summary(REPORT_FILE, no_list=args.no_list)

    # If coverage was requested, parse coverage.xml and print percentage
    if args.with_coverage:
        cov_file = Path("coverage.xml")
        if cov_file.exists():
            try:
                tree = ET.parse(cov_file)
                root = tree.getroot()
                if args.coverage_format == "lines":
                    key = "line-rate"
                    label = "lines"
                else:
                    key = "branch-rate"
                    label = "branches"

                rate = root.attrib.get(key)
                if rate is not None:
                    try:
                        pct = float(rate) * 100.0
                        print(f"\nCoverage: {pct:.1f}% ({label})")
                    except Exception:
                        print(f"\nCoverage: could not parse {key} from coverage.xml")
                else:
                    print(f"\nCoverage: coverage.xml present but no {key} attribute found")
            except Exception as exc:
                print("\nCoverage: failed to read coverage.xml:", exc)
        else:
            print("\nCoverage: coverage.xml not found")

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
