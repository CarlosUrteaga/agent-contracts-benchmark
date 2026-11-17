# Copyright (c) 2026 Jorge Carlos Urteaga Reyesvera
# SPDX-License-Identifier: Apache-2.0

"""Adapter connecting the enforcement benchmark to the vogtcon library per run."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

import vogtcon
from vogtcon import (
    ActionProposal,
    EnforcementPolicy,
    ExecutionContext,
    Governor,
    GovernedToolExecutor,
    GovernorInput,
    ToolExecutionOutcome,
    Violation,
)


def violation_to_dict(violation: Violation) -> dict[str, Any]:
    """Convert a vogtcon Violation model into the benchmark's legacy dict format."""
    payload: dict[str, Any] = {
        "rule": violation.rule,
        "phase": violation.phase,
        "severity": violation.severity,
    }
    if violation.action is not None:
        payload["action"] = violation.action
    return payload


@dataclass
class RuntimeExecutionResult:
    decision: str
    violations: list[dict[str, Any]]
    executed: bool
    result: Any | None
    governor_latency: float


class VogtconRunAdapter:
    """Per-run adapter managing contract loading, execution context, and governance via vogtcon."""

    def __init__(
        self,
        contract_path: str | Path,
        *,
        mode: str | None = None,
        run_id: str = "run",
    ) -> None:
        self.contract_path = Path(contract_path)
        self.document = vogtcon.load_contract(self.contract_path)
        self.contract = self.document.contract
        self.contract_dict = dict(self.document.original)
        self.mode = str(mode) if mode is not None else str(self.contract_dict.get("mode", "no_contract"))
        self.run_id = run_id

        self.governor = Governor()
        self.executor = GovernedToolExecutor(self.governor)
        self.policy = EnforcementPolicy(mode=self.mode)

    def validate_pre(
        self,
        observed_agent_fingerprint: str,
        observed_contract_fingerprint: str,
    ) -> tuple[list[dict[str, Any]], float]:
        started = time.perf_counter()
        context = ExecutionContext(
            state={},
            available_tools=[],
            observed_agent_fingerprint=observed_agent_fingerprint,
            observed_contract_fingerprint=observed_contract_fingerprint,
            final_properties={},
            forbidden_outcomes_triggered=[],
        )
        request = GovernorInput(
            run_id=self.run_id,
            contract=self.contract,
            phase="pre_execution",
            context=context,
            policy=self.policy,
        )
        decision = self.governor.evaluate(request)
        latency = time.perf_counter() - started
        violations = [violation_to_dict(v) for v in decision.violations]
        return violations, latency

    def execute_tool(
        self,
        action: dict[str, Any],
        state: dict[str, Any],
        available_tools: Sequence[str],
        tool_fn: Callable[[dict[str, Any]], Any],
        *,
        action_index: int | None = None,
    ) -> RuntimeExecutionResult:
        started = time.perf_counter()
        tool_duration = 0.0

        def wrapped_tool(proposal: ActionProposal) -> Any:
            nonlocal tool_duration
            t0 = time.perf_counter()
            try:
                return tool_fn(proposal.arguments)
            finally:
                tool_duration = time.perf_counter() - t0

        iteration_val = action.get("iteration")
        iteration_int = int(iteration_val) if iteration_val is not None and int(iteration_val) >= 1 else None
        proposal = ActionProposal(
            tool_name=str(action["tool_name"]),
            arguments=dict(action.get("arguments", {})),
            iteration=iteration_int,
        )
        context = ExecutionContext(
            state=dict(state),
            available_tools=list(available_tools),
            observed_agent_fingerprint=None,
            observed_contract_fingerprint=None,
            final_properties={},
            forbidden_outcomes_triggered=[],
        )
        request = GovernorInput(
            run_id=self.run_id,
            contract=self.contract,
            phase="runtime",
            context=context,
            action=proposal,
            policy=self.policy,
        )
        outcome: ToolExecutionOutcome[Any] = self.executor.execute(
            request,
            wrapped_tool,
            action_index=action_index,
        )
        total_time = time.perf_counter() - started
        governor_latency = max(0.0, total_time - tool_duration)

        decision_str = str(outcome.decision.decision) if outcome.decision.decision is not None else "allow"
        violations = [violation_to_dict(v) for v in outcome.decision.violations]

        return RuntimeExecutionResult(
            decision=decision_str,
            violations=violations,
            executed=outcome.executed,
            result=outcome.result,
            governor_latency=governor_latency,
        )

    def validate_post(
        self,
        response: dict[str, Any],
        run_ledger: dict[str, Any] | None,
        final_properties: dict[str, Any],
        forbidden_outcomes_triggered: Sequence[str],
    ) -> tuple[list[dict[str, Any]], float]:
        started = time.perf_counter()
        context = ExecutionContext(
            state={},
            available_tools=[],
            observed_agent_fingerprint=None,
            observed_contract_fingerprint=None,
            final_properties=dict(final_properties),
            forbidden_outcomes_triggered=list(forbidden_outcomes_triggered),
        )
        request = GovernorInput(
            run_id=self.run_id,
            contract=self.contract,
            phase="post_execution",
            context=context,
            response=dict(response),
            run_ledger=dict(run_ledger) if run_ledger is not None else None,
            policy=self.policy,
        )
        decision = self.governor.evaluate(request)
        latency = time.perf_counter() - started
        violations = [violation_to_dict(v) for v in decision.violations]
        return violations, latency
