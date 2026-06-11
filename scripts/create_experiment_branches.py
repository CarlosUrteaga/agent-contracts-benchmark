#!/usr/bin/env python3
"""Plan or create experiment branches from existing arm baselines."""

from __future__ import annotations

import argparse
import subprocess
import sys

from benchmark_constants import (
    ARMS,
    EXPECTED_ARM_BRANCH_COUNT,
    EXPECTED_EXPERIMENT_BRANCH_COUNT,
    REPLICATIONS,
    STRATEGIES,
    arm_branch_name,
    experiment_branch_name,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan or create experiment branches from existing arm baselines."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the branch plan without modifying Git state. This is the default behavior.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Create experiment branches. Requires existing arm baseline branches.",
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


def existing_branches() -> set[str]:
    result = run_git("for-each-ref", "--format=%(refname:short)", "refs/heads")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "failed to enumerate local branches")
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def branch_plan() -> list[tuple[str, str]]:
    plan: list[tuple[str, str]] = []
    for arm in ARMS:
        source = arm_branch_name(arm)
        for strategy in STRATEGIES:
            for replication in REPLICATIONS:
                target = experiment_branch_name(strategy, arm, replication)
                plan.append((source, target))
    return plan


def print_plan(plan: list[tuple[str, str]]) -> None:
    print("Arm baseline branches:")
    for arm in ARMS:
        print(f"- {arm_branch_name(arm)}")
    print("")
    print("Planned experiment branches:")
    for source, target in plan:
        print(f"- {source} -> {target}")
    print("")
    print(
        f"SUMMARY arm_branches={EXPECTED_ARM_BRANCH_COUNT} "
        f"experiment_branches={EXPECTED_EXPERIMENT_BRANCH_COUNT}"
    )


def apply_plan(plan: list[tuple[str, str]]) -> int:
    branches = existing_branches()
    missing_sources = [source for source in {source for source, _ in plan} if source not in branches]
    if missing_sources:
        for source in missing_sources:
            print(
                f"missing source branch: {source} "
                f"(create baseline branches first with "
                f"`python3 scripts/create_baseline_branches.py --apply`)",
                file=sys.stderr,
            )
        return 1

    for _, target in plan:
        if target in branches:
            print(f"branch already exists: {target}", file=sys.stderr)
            return 1

    for source, target in plan:
        result = run_git("branch", target, source)
        if result.returncode != 0:
            print(result.stderr.strip() or f"failed to create branch: {target}", file=sys.stderr)
            return 1
        print(f"created {target} from {source}")

    print(
        f"SUMMARY arm_branches={EXPECTED_ARM_BRANCH_COUNT} "
        f"experiment_branches={EXPECTED_EXPERIMENT_BRANCH_COUNT}"
    )
    return 0


def main() -> int:
    args = parse_args()
    plan = branch_plan()
    if args.dry_run:
        print_plan(plan)
        return 0
    return apply_plan(plan)


if __name__ == "__main__":
    raise SystemExit(main())
