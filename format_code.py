#!/usr/bin/env python
"""
Formatter and linter script.
Supports dry-run, fast mode, and Python version selection.
"""

import argparse
import logging
import os
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.DEBUG)
LOGGER.addHandler(CH)

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_PATH = REPO_ROOT / "common"


@dataclass
class RunResult:
    code: int
    stdout: str
    stderr: str


def get_env() -> dict:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["LC_ALL"] = "C.UTF-8"
    env["LANG"] = "C.UTF-8"
    return env


def get_modified_py_files(branch_name: str, dir_path: Path = APP_PATH) -> list[str]:
    """Return list of modified Python files: staged, unstaged, or different vs branch."""

    def git_diff(options: list[str]) -> list[str]:
        proc = subprocess.run(
            ["git", "diff"] + options,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=dir_path,
            encoding="utf-8",
            errors="replace",
            env=get_env(),
        )
        return proc.stdout.splitlines()

    branch_files = git_diff(["--name-only", branch_name])
    staged_files = git_diff(["--name-only", "--cached"])
    unstaged_files = git_diff(["--name-only"])

    all_files = set(branch_files + staged_files + unstaged_files)
    LOGGER.debug(f"All files: {all_files}")
    # Convert to absolute Path and filter Python files that exist
    python_files = []
    for f in all_files:
        abs_path = REPO_ROOT / Path(f)
        if abs_path.suffix == ".py" and abs_path.exists():
            try:
                if abs_path.is_relative_to(dir_path):
                    python_files.append(abs_path.resolve())
            except AttributeError:
                # For Python < 3.9, fallback
                if str(abs_path).startswith(str(dir_path.resolve()) + os.sep):
                    python_files.append(abs_path)
                    break
    LOGGER.info(f"Python files: {python_files}")
    return [str(f) for f in python_files]


def run_command(cmd: list[str], dir_path: Path = REPO_ROOT) -> RunResult:
    """Run a shell command and capture output."""
    LOGGER.info(f"Running command: {cmd}")
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=dir_path,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=get_env(),
    )
    return RunResult(proc.returncode, proc.stdout, proc.stderr)


class Formatter(ABC):
    """Abstract base class for a formatter/linter."""

    @abstractmethod
    def run(
        self,
        files: Iterable[str],
        dry_run: bool = False,
        py_version: str | None = None,
    ) -> RunResult: ...


class AutoflakeFormatter(Formatter):
    def run(self, files: Iterable[str], dry_run: bool = False, **kwargs) -> RunResult:
        cmd = [sys.executable, "-m", "autoflake"]
        if not dry_run:
            cmd += ["--in-place"]
        cmd += [
            "--remove-unused-variables",
            "--remove-all-unused-imports",
            "--recursive",
        ]
        return run_command(cmd + list(files))


class IsortFormatter(Formatter):
    def run(
        self,
        files: Iterable[str],
        dry_run: bool = False,
        py_version: str | None = None,
        **kwargs,
    ) -> RunResult:
        cmd = [sys.executable, "-m", "isort", "--profile", "black"]
        if dry_run:
            cmd += ["--diff", "--check-only"]
        if py_version:
            cmd += [f"--py {py_version}"]
        return run_command(cmd + list(files))


class BlackFormatter(Formatter):
    def run(
        self,
        files: Iterable[str],
        dry_run: bool = False,
        py_version: str | None = None,
        **kwargs,
    ) -> RunResult:
        py_version = py_version or f"{sys.version_info.major}{sys.version_info.minor}"
        cmd = [sys.executable, "-m", "black", f"-tpy{py_version}"]
        if dry_run:
            cmd += ["--check"]
        return run_command(cmd + list(files))


class RuffFormatter(Formatter):
    def run(self, files: Iterable[str], dry_run: bool = False, **kwargs) -> RunResult:
        cmd = [sys.executable, "-m", "ruff", "check"]
        cmd += (
            ["--diff"] if dry_run else ["--fix", "--exit-zero"]
        )  # Fix what it can, ignore remaining errors
        return run_command(cmd + list(files))


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--fast",
        action="store",
        help="Format only modified files compared to this branch",
    )
    parser.add_argument(
        "--dry",
        action="store_true",
        help="Dry-run mode, do not modify files",
    )
    parser.add_argument(
        "--py",
        type=str,
        default=f"{sys.version_info.major}{sys.version_info.minor}",
        help="Target Python version for formatters (e.g., 311 for Python 3.11)",
    )
    parser.add_argument(
        "filename",
        nargs="*",
        help=f"Files to format. Default: {APP_PATH}",
    )
    return parser.parse_args()


def format_code(args: argparse.Namespace) -> int:
    # Determine files to process
    if args.fast:
        files = get_modified_py_files(args.fast)
        if not files:
            LOGGER.warning(
                f"No modified Python files found vs branch {args.fast} Exiting.",
            )
            return 0
    elif args.filename:
        files = args.filename
    else:
        files = [APP_PATH]

    if args.debug:
        LOGGER.setLevel(logging.DEBUG)

    LOGGER.info(f"Files to format: {files}")
    LOGGER.info("*" * 80 + "\nRunning Formatters/Linters\n" + "*" * 80)

    # Sequence: Autoflake → isort → Black → Ruff
    formatters: list[Formatter] = [
        AutoflakeFormatter(),
        IsortFormatter(),
        BlackFormatter(),
        RuffFormatter(),
    ]

    final_code = 0
    for fmt in formatters:
        result = fmt.run(files, dry_run=args.dry, py_version=args.py)
        if args.dry:
            LOGGER.info(f"{fmt.__class__.__name__} stdout:\n{result.stdout}")
            LOGGER.info(f"{fmt.__class__.__name__} stderr:\n{result.stderr}")
        if result.code != 0:
            final_code = result.code  # record last non-zero exit code

    LOGGER.info("Formatting complete.")
    return final_code


if __name__ == "__main__":
    sys.exit(format_code(get_args()))
