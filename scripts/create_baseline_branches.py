#!/usr/bin/env python3
"""Create local t0-common and arm baseline branches from available remote refs."""

from __future__ import annotations

import argparse
import subprocess
import sys

from benchmark_constants import ARMS, EXPECTED_ARM_BRANCH_COUNT, arm_branch_name

T0_COMMON_BRANCH = "t0-common"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan or create local baseline branches needed before experiment branch generation."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the baseline branch plan without modifying Git state. This is the default behavior.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Create missing local baseline branches from matching remote refs.",
    )
    args = parser.parse_args()
    if args.apply and args.dry_run:
        parser.error("choose either --apply or --dry-run, not both")
    if not args.apply:
        args.dry_run = True
    return args


def run_git(*git_args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *git_args],
        check=False,
        text=True,
        capture_output=True,
    )


def existing_local_branches() -> set[str]:
    result = run_git("for-each-ref", "--format=%(refname:short)", "refs/heads")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "failed to enumerate local branches")
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def existing_remote_branches() -> set[str]:
    result = run_git("for-each-ref", "--format=%(refname:short)", "refs/remotes")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "failed to enumerate remote branches")
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def branch_plan() -> list[tuple[str, str]]:
    plan: list[tuple[str, str]] = [(f"origin/{T0_COMMON_BRANCH}", T0_COMMON_BRANCH)]
    for arm in ARMS:
        branch = arm_branch_name(arm)
        plan.append((f"origin/{branch}", branch))
    return plan


def print_plan(plan: list[tuple[str, str]], local_branches: set[str]) -> None:
    print("Required local baseline branches:")
    print(f"- {T0_COMMON_BRANCH}")
    for arm in ARMS:
        print(f"- {arm_branch_name(arm)}")
    print("")
    print("Baseline branch plan:")
    for source, target in plan:
        status = "already exists locally" if target in local_branches else "will create locally"
        print(f"- {source} -> {target} ({status})")
    print("")
    print(
        f"SUMMARY baseline_branches={EXPECTED_ARM_BRANCH_COUNT + 1} "
        f"arm_branches={EXPECTED_ARM_BRANCH_COUNT}"
    )


def apply_plan(plan: list[tuple[str, str]]) -> int:
    local_branches = existing_local_branches()
    remote_branches = existing_remote_branches()

    missing_remotes = [source for source, target in plan if target not in local_branches and source not in remote_branches]
    if missing_remotes:
        for source in missing_remotes:
            print(f"missing remote source branch: {source}", file=sys.stderr)
        return 1

    created = 0
    for source, target in plan:
        if target in local_branches:
            print(f"already present: {target}")
            continue
        result = run_git("branch", target, source)
        if result.returncode != 0:
            print(result.stderr.strip() or f"failed to create branch: {target}", file=sys.stderr)
            return 1
        print(f"created {target} from {source}")
        created += 1

    print(
        f"SUMMARY baseline_branches={EXPECTED_ARM_BRANCH_COUNT + 1} "
        f"arm_branches={EXPECTED_ARM_BRANCH_COUNT} "
        f"created={created}"
    )
    return 0


def main() -> int:
    args = parse_args()
    plan = branch_plan()
    local_branches = existing_local_branches()
    if args.dry_run:
        print_plan(plan, local_branches)
        return 0
    return apply_plan(plan)


if __name__ == "__main__":
    raise SystemExit(main())
