"""Shared helpers for the LLM-based contract enforcement benchmark."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.governor.common import json_fingerprint, load_yaml_or_json

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_ROOT = REPO_ROOT / "benchmark" / "enforcement"
SCENARIOS_ROOT = BENCHMARK_ROOT / "scenarios"
FIXTURES_ROOT = BENCHMARK_ROOT / "fixtures"
CONFIG_ROOT = BENCHMARK_ROOT / "config"
MODEL_PROFILES_ROOT = CONFIG_ROOT / "model_profiles"
TAMPERED_ROOT = FIXTURES_ROOT / "tampered"
ORACLE_ROOT = BENCHMARK_ROOT / "oracle"
CONTRACTS_ROOT = REPO_ROOT / "contracts" / "enforcement"
RESULTS_ROOT = REPO_ROOT / "results" / "enforcement"

RUN_LEDGER_FILE = "run_ledger.json"
TRACE_FILE = "trace.jsonl"
SUMMARY_FILE = "summary.json"

MODES = ["no_contract", "advisory", "guarded", "strict"]
TOOLS = ["search_policy", "create_ticket", "approve_request", "store_memory", "send_notification"]
REQUIRED_LEDGER_KEYS = [
    "run_id",
    "scenario_id",
    "mode",
    "contract_id",
    "provider",
    "model_id",
    "replication_id",
    "actions",
    "artifacts",
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_scenario(path: Path) -> dict[str, Any]:
    data = read_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain an object")
    return data


def load_contract(path: Path) -> dict[str, Any]:
    return load_yaml_or_json(path)


def load_model_profile(path: Path) -> dict[str, Any]:
    return load_yaml_or_json(path)


def compute_contract_fingerprint(contract: dict[str, Any]) -> str:
    payload = {key: value for key, value in contract.items() if key != "contract_fingerprint"}
    return json_fingerprint(payload)


def compute_agent_configuration_fingerprint(
    *,
    system_prompt: str,
    model_profile: dict[str, Any],
    tool_definitions: list[dict[str, Any]],
    memory_policy: str,
    runtime_version: str,
) -> str:
    return json_fingerprint(
        {
            "system_prompt": system_prompt,
            "model_profile": {
                "provider": model_profile["provider"],
                "model_id": model_profile["model_id"],
                "declared_model_version": model_profile["declared_model_version"],
                "temperature": model_profile["temperature"],
                "max_tokens": model_profile["max_tokens"],
                "timeout": model_profile["timeout"],
                "retry_policy": model_profile["retry_policy"],
                "seed": model_profile.get("seed"),
            },
            "tool_definitions": tool_definitions,
            "memory_policy": memory_policy,
            "runtime_version": runtime_version,
        }
    )


def scenario_paths(root: Path) -> list[Path]:
    return sorted(root.glob("S-*.json"))


def load_scenarios_index(root: Path = SCENARIOS_ROOT) -> dict[str, dict[str, Any]]:
    return {
        str(data["scenario_id"]): data
        for data in (load_scenario(path) for path in scenario_paths(root))
    }


def ensure_relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)
