"""Shared benchmark constants for protocol validation and branch planning."""

from __future__ import annotations

ARMS = [
    "base",
    "agent-card",
    "contract-first",
    "contract-flow",
]

STRATEGIES = [
    "evolutionary",
    "final-spec",
]

REPLICATIONS = [
    "rep01",
    "rep02",
    "rep03",
]

STEPS = [
    "T0",
    "C1",
    "C2",
    "C3",
    "C4",
    "C5",
    "C6",
]

STATUS_VALUES = [
    "pending",
    "completed",
    "failed",
]

AGENT_EXECUTORS = [
    "ralph-loop",
    "codex",
]

REQUIRED_DOCS = [
    "README.md",
    "README_PROTOCOL.md",
    "BENCHMARK_SPEC.md",
    "ARCHITECTURE_ARMS.md",
    "CHANGE_PROTOCOL.md",
    "METRICS_SPEC.md",
    "IMPLEMENTATION_PLAN.md",
    "PROMPT.md",
]

TEMPLATE_FILES = [
    "templates/manifest.template.json",
    "templates/run_ledger.template.json",
]

README_EXECUTION_ORDER = [
    "1. scaffold benchmark protocol",
    "2. create `t0-common`",
    "3. create arm baselines",
    "4. generate experiment branches",
    "5. execute trajectories",
    "6. aggregate metrics",
]

EXPECTED_ARM_BRANCH_COUNT = len(ARMS)
EXPECTED_EXPERIMENT_BRANCH_COUNT = len(ARMS) * len(STRATEGIES) * len(REPLICATIONS)


def arm_branch_name(arm: str) -> str:
    return f"arm/{arm}"


def experiment_branch_name(strategy: str, arm: str, replication: str) -> str:
    return f"exp/{strategy}/{arm}/{replication}"
