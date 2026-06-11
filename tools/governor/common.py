"""Shared constants and helpers for the contract benchmark."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ARMS = ["base", "agent-card", "contract-first", "contract-flow"]
STRATEGIES = ["evolutionary", "final-spec"]
REPLICATIONS = ["rep01", "rep02", "rep03"]

REQUIRED_MANIFEST_FIELDS = [
    "arm",
    "strategy",
    "replication",
    "step",
    "changed_files",
    "changed_file_count",
    "change_spread",
    "traceability_ratio",
    "test_failures",
    "contract_violations",
    "run_ledger_compliance",
    "capabilities_present",
    "governance_artifacts_present",
]

MANIFEST_FINGERPRINT_FILE = "manifest.fingerprint"
RUN_LEDGER_FILE = "run_ledger.json"
AGENT_CARD_FILE = "AGENT_CARD.md"
CONTRACTS_FILE = "CONTRACTS.md"
WORKFLOW_FILE = "WORKFLOW.md"

REPO_ROOT = Path(__file__).resolve().parents[2]
STEP_SPEC_PATH = REPO_ROOT / "benchmark" / "step_capabilities.yaml"


def _parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value == "":
        return ""
    if value in {"[]", "{}"}:
        return [] if value == "[]" else {}
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "~"}:
        return None
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _load_yaml_subset(text: str) -> Any:
    lines: list[tuple[int, str]] = []
    for original in text.splitlines():
        stripped = original.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(original) - len(original.lstrip(" "))
        lines.append((indent, original[indent:]))

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(lines):
            return {}, index
        current_indent, current_text = lines[index]
        if current_indent < indent:
            return {}, index
        if current_indent == indent and current_text.startswith("- "):
            return parse_list(index, indent)
        return parse_mapping(index, indent)

    def parse_list(index: int, indent: int) -> tuple[list[Any], int]:
        items: list[Any] = []
        while index < len(lines):
            current_indent, current_text = lines[index]
            if current_indent != indent or not current_text.startswith("- "):
                break
            rest = current_text[2:].strip()
            index += 1
            if not rest:
                nested, index = parse_block(index, indent + 2)
                items.append(nested)
                continue
            if ":" in rest:
                key, raw_value = rest.split(":", 1)
                item: dict[str, Any] = {}
                raw_value = raw_value.strip()
                if raw_value:
                    item[key.strip()] = _parse_scalar(raw_value)
                else:
                    nested, index = parse_block(index, indent + 2)
                    item[key.strip()] = nested
                while index < len(lines):
                    next_indent, next_text = lines[index]
                    if next_indent < indent + 2 or next_indent == indent:
                        break
                    if next_indent == indent + 2 and not next_text.startswith("- "):
                        child_key, child_raw_value = next_text.split(":", 1)
                        index += 1
                        child_raw_value = child_raw_value.strip()
                        if child_raw_value:
                            item[child_key.strip()] = _parse_scalar(child_raw_value)
                        else:
                            nested, index = parse_block(index, indent + 4)
                            item[child_key.strip()] = nested
                        continue
                    break
                items.append(item)
                continue
            items.append(_parse_scalar(rest))
        return items, index

    def parse_mapping(index: int, indent: int) -> tuple[dict[str, Any], int]:
        mapping: dict[str, Any] = {}
        while index < len(lines):
            current_indent, current_text = lines[index]
            if current_indent < indent or current_text.startswith("- "):
                break
            if current_indent > indent:
                raise ValueError(f"invalid indentation near: {current_text}")
            key, raw_value = current_text.split(":", 1)
            index += 1
            raw_value = raw_value.strip()
            if raw_value:
                mapping[key.strip()] = _parse_scalar(raw_value)
            else:
                nested, index = parse_block(index, indent + 2)
                mapping[key.strip()] = nested
        return mapping, index

    parsed, _ = parse_block(0, 0)
    return parsed


def load_yaml_or_json(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except ModuleNotFoundError:
            data = _load_yaml_subset(text)
        else:
            data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a mapping")
    return data


@lru_cache(maxsize=1)
def load_step_spec() -> dict[str, Any]:
    return load_yaml_or_json(STEP_SPEC_PATH)


def strategy_steps(strategy: str) -> list[dict[str, Any]]:
    spec = load_step_spec()
    return list(spec["strategies"][strategy]["steps"])


def all_steps() -> list[str]:
    return [item["step"] for item in strategy_steps("evolutionary")]


def first_step_for_strategy(strategy: str) -> str:
    return strategy_steps(strategy)[0]["step"]


def capabilities_for_step(step: str) -> list[str]:
    spec = load_step_spec()
    return list(spec["step_capabilities"][step])


def capability_label(step: str) -> str:
    spec = load_step_spec()
    return str(spec["step_metadata"][step]["label"])


def capability_id_for_step(step: str) -> str:
    spec = load_step_spec()
    return str(spec["step_metadata"][step]["capability_id"])


def governance_artifacts_for_arm(arm: str) -> list[str]:
    spec = load_step_spec()
    return list(spec["arms"][arm]["governance_artifacts"])


def contract_filename_for_arm(arm: str) -> str:
    spec = load_step_spec()
    return str(spec["arms"][arm]["contract_file"])


def reconstruction_conditions() -> dict[str, dict[str, Any]]:
    spec = load_step_spec()
    return dict(spec["reconstruction_conditions"])


def manifest_step(manifest: dict[str, Any]) -> str:
    step = manifest.get("step", manifest.get("step_id"))
    if not isinstance(step, str):
        raise ValueError("manifest is missing string step/step_id")
    return step


def json_fingerprint(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def manifest_content_for_fingerprint(manifest: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in manifest.items() if key != "_mutation"}
