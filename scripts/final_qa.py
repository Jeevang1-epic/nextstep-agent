from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


def run_command(command: list[str]) -> int:
    printable = " ".join(command)
    print(f"\n=== Running: {printable}")
    result = subprocess.run(command, cwd=ROOT_DIR, text=True)
    if result.returncode:
        print(f"FAILED: {printable} exited with {result.returncode}")
    else:
        print(f"PASSED: {printable}")
    return result.returncode


def main() -> int:
    pytest_tmp = Path(tempfile.mkdtemp(prefix="nextstep_final_qa_"))
    try:
        pytest_cache = str(pytest_tmp / ".pytest_cache")
        commands = [
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-o",
                "addopts=",
                "-o",
                f"cache_dir={pytest_cache}",
                "--basetemp",
                str(pytest_tmp),
            ],
            [sys.executable, "-m", "compileall", "nextstep_agent", "mcp_server"],
            [sys.executable, "evals/run_evals.py"],
            [
                sys.executable,
                "-m",
                "nextstep_agent.agent",
                "demo_pack/demo_school_notice.txt",
                "--current-date",
                "2026-07-02",
                "--trace",
            ],
            [
                sys.executable,
                "-m",
                "nextstep_agent.agent",
                "demo_pack/demo_invoice.txt",
                "--current-date",
                "2026-07-02",
                "--json",
            ],
        ]

        failures = 0
        for command in commands:
            failures += 1 if run_command(command) else 0

        if failures:
            print(f"\nFinal QA failed: {failures} command(s) failed.")
            return 1

        print("\nFinal QA passed.")
        return 0
    finally:
        shutil.rmtree(pytest_tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
