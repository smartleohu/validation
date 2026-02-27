import argparse
import logging
import os
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
LOGGER.addHandler(handler)


# ------------------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = REPO_ROOT / "src"


# ------------------------------------------------------------------------------
# Models
# ------------------------------------------------------------------------------

@dataclass(slots=True)
class RunResult:
    code: int
    stdout: str
    stderr: str


# ------------------------------------------------------------------------------
# Utils
# ------------------------------------------------------------------------------

def get_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["LC_ALL"] = "C.UTF-8"
    env["LANG"] = "C.UTF-8"
    return env


def run_command(cmd: list[str], cwd: Path = REPO_ROOT) -> RunResult:
    LOGGER.debug("Running: %s", " ".join(cmd))

    proc = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=get_env(),
    )

    return RunResult(proc.returncode, proc.stdout, proc.stderr)


def get_modified_py_files(branch: str, dir_path: Path) -> list[str]:
    def git_diff(options: list[str]) -> list[str]:
        result = run_command(["git", "diff", *options])
        return result.stdout.splitlines()

    branch_files = git_diff(["--name-only", branch])
    staged_files = git_diff(["--name-only", "--cached"])
    unstaged_files = git_diff(["--name-only"])

    all_files = set(branch_files + staged_files + unstaged_files)

    python_files: list[str] = []

    for file in all_files:
        abs_path = REPO_ROOT / file

        if abs_path.suffix == ".py" and abs_path.exists():
            try:
                if abs_path.is_relative_to(dir_path):
                    python_files.append(str(abs_path.resolve()))
            except AttributeError:
                if str(abs_path.resolve()).startswith(str(dir_path.resolve())):
                    python_files.append(str(abs_path.resolve()))

    return python_files


# ------------------------------------------------------------------------------
# Formatter Base
# ------------------------------------------------------------------------------

class Formatter(ABC):
    @abstractmethod
    def run(
        self,
        files: Iterable[str],
        dry_run: bool = False,
        py_version: str | None = None,
    ) -> RunResult:
        ...


# ------------------------------------------------------------------------------
# Formatters
# ------------------------------------------------------------------------------

class AutoflakeFormatter(Formatter):
    def run(self, files: Iterable[str], dry_run: bool = False, **_) -> RunResult:
        cmd = [
            sys.executable,
            "-m",
            "autoflake",
            "--remove-unused-variables",
            "--remove-all-unused-imports",
            "--recursive",
        ]

        if not dry_run:
            cmd.append("--in-place")

        return run_command(cmd + list(files))


class IsortFormatter(Formatter):
    def run(
        self,
        files: Iterable[str],
        dry_run: bool = False,
        py_version: str | None = None,
        **_,
    ) -> RunResult:
        cmd = [sys.executable, "-m", "isort", "--profile", "black"]

        if dry_run:
            cmd += ["--diff", "--check-only"]

        if py_version:
            cmd.append(f"--py={py_version}")

        return run_command(cmd + list(files))


class BlackFormatter(Formatter):
    def run(
        self,
        files: Iterable[str],
        dry_run: bool = False,
        py_version: str | None = None,
        **_,
    ) -> RunResult:
        cmd = [sys.executable, "-m", "black"]

        if dry_run:
            cmd.append("--check")

        if py_version:
            cmd.append(f"--target-version=py{py_version}")

        return run_command(cmd + list(files))


class RuffFormatter(Formatter):
    def run(self, files: Iterable[str], dry_run: bool = False, **_) -> RunResult:
        cmd = [sys.executable, "-m", "ruff", "check"]

        if dry_run:
            cmd.append("--diff")
        else:
            cmd += ["--fix", "--exit-zero"]

        return run_command(cmd + list(files))


# ------------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------------

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Code formatter runner")

    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--fast", help="Format only modified files vs branch")
    parser.add_argument("--dry", action="store_true", help="Dry-run mode")
    parser.add_argument(
        "--py",
        default=f"{sys.version_info.major}{sys.version_info.minor}",
        help="Target Python version (e.g. 311)",
    )
    parser.add_argument("filenames", nargs="*")

    return parser.parse_args()


# ------------------------------------------------------------------------------
# Main logic
# ------------------------------------------------------------------------------

def format_code(args: argparse.Namespace, dir_paths: list[Path]) -> int:
    if args.debug:
        LOGGER.setLevel(logging.DEBUG)

    if args.fast:
        files: list[str] = []
        for path in dir_paths:
            files += get_modified_py_files(args.fast, path)

        if not files:
            LOGGER.info("No modified Python files found.")
            return 0

    elif args.filenames:
        files = args.filenames
    else:
        files = [str(p) for p in dir_paths]

    LOGGER.info("Files to format: %s", files)

    formatters: list[Formatter] = [
        AutoflakeFormatter(),
        IsortFormatter(),
        BlackFormatter(),
        RuffFormatter(),
    ]

    final_code = 0

    for formatter in formatters:
        result = formatter.run(files, dry_run=args.dry, py_version=args.py)

        if result.stdout:
            LOGGER.info(result.stdout)

        if result.stderr:
            LOGGER.error(result.stderr)

        if result.code != 0:
            final_code = result.code

    LOGGER.info("Formatting complete. Exit code: %s", final_code)
    return final_code


if __name__ == "__main__":
    sys.exit(format_code(get_args(), [APP_PATH]))
