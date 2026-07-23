#!/usr/bin/env python3
"""Find candidate INTRODUCING commits for a regression — pager-free, no bisection.

Wraps `git log` (with `--no-pager`, so it never traps you in a pager) over the file(s) a fix
touched, optionally pickaxing a distinctive token, and prints a short ranked list of candidate
commits (newest first). Copy the SHA that introduced the buggy behaviour into add_forward_event.py.

Tips:
  * The fix PR's description often names the regressing change ("regressed in #X" / "reverts commit Y")
    — that's the fastest source; this helper is the fallback.
  * Many passes are now in Rust, so the buggy logic may live under crates/ or in *_utils.py, not the
    pass's .py file. Pass several --file paths if unsure.

Examples:
  python scripts/find_introducing_commit.py --token max_trials \
      --file qiskit/transpiler/passes/layout/vf2_utils.py --file qiskit/transpiler/passes/layout/vf2_layout.py
  python scripts/find_introducing_commit.py --grep "VF2PostLayout" --file qiskit/transpiler/preset_passmanagers/__init__.py
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_CLONE = _REPO_ROOT / "environment" / "_builds" / "hist-vf2post-14120-base" / "qiskit"


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), "--no-pager", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed:\n{r.stderr.strip()}")
    return r.stdout


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="List candidate introducing commits (pager-free).")
    p.add_argument("--repo", default=str(_DEFAULT_CLONE), help="path to an existing qiskit clone")
    p.add_argument("--file", action="append", default=[], help="path(s) the fix touched (repeatable)")
    p.add_argument("--token", default=None, help="pickaxe: commits that added/removed this string")
    p.add_argument("--grep", default=None, help="filter commit messages by this regex")
    p.add_argument("--before", default=None, help="only commits before this SHA (e.g. the fix commit)")
    p.add_argument("--limit", type=int, default=15)
    args = p.parse_args(argv)

    repo = Path(args.repo)
    if not (repo / ".git").exists():
        raise SystemExit(f"{repo} is not a git clone. Point --repo at one of environment/_builds/*/qiskit, "
                         f"or `git -C \"{repo}\" fetch --all --tags` first.")

    rev = f"{args.before}^" if args.before else "--all"
    fmt = "%h  %cs  %s"
    cmd = ["log", f"--format={fmt}", f"-n{args.limit}", rev]
    if args.token:
        cmd.insert(1, f"-S{args.token}")
    if args.grep:
        cmd.insert(1, f"--grep={args.grep}")
        cmd.insert(1, "-i")
    if args.file:
        cmd += ["--"] + args.file

    print(f"# candidate introducing commits (repo={repo.name}, newest first)")
    print(f"#   token={args.token!r} grep={args.grep!r} files={args.file or 'all'}\n")
    out = _git(repo, *cmd).strip()
    if not out:
        print("(no commits matched — widen --file paths, drop --before, or try a different --token)")
        return 2
    print("  short    date        subject")
    for line in out.splitlines():
        print("  " + line)
    print("\nNext: pick the SHA that introduced the bug, then:")
    print("  python scripts\\add_forward_event.py --event-id <id> --env-id <env> --fault-type <type> "
          "--pr <PR> --reference \"<title>\" --introducing-sha <SHORT_SHA_ABOVE>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
