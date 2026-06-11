"""Model adapter interfaces for the enforcement benchmark."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


class AgentModelAdapter(Protocol):
    def generate_next_action(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        ...

    def handle_tool_result(self, event: dict[str, Any]) -> None:
        ...

    def handle_governor_feedback(self, event: dict[str, Any]) -> None:
        ...


@dataclass
class MockScenarioAdapter:
    """Deterministic adapter used for unit/integration tests and local dry runs."""

    scenario: dict[str, Any]
    mode: str
    _cursor: int = 0
    _decisions: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        scripted = self.scenario["fixtures"]["mock_behavior"][self.mode]
        self._decisions = [dict(item) for item in scripted]

    def generate_next_action(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if self._cursor >= len(self._decisions):
            return {
                "decision_type": "final_response",
                "response": {"answer": "Unable to complete safely.", "citations": [], "status": "refused"},
                "token_usage": 20,
                "estimated_cost": 0.0,
            }
        decision = dict(self._decisions[self._cursor])
        self._cursor += 1
        decision.setdefault("token_usage", 25)
        decision.setdefault("estimated_cost", 0.0)
        return decision

    def handle_tool_result(self, event: dict[str, Any]) -> None:
        return None

    def handle_governor_feedback(self, event: dict[str, Any]) -> None:
        return None


@dataclass
class OpenAIChatCompletionsAdapter:
    """Real backend adapter using OpenAI Chat Completions tool calling."""

    model_profile: dict[str, Any]
    system_prompt: str

    def generate_next_action(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        try:
            from openai import OpenAI  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError("OpenAI SDK is required for the openai_chat_completions adapter") from exc

        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_profile["model_id"],
            temperature=self.model_profile["temperature"],
            max_tokens=self.model_profile["max_tokens"],
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        choice = response.choices[0].message
        if getattr(choice, "tool_calls", None):
            tool_call = choice.tool_calls[0]
            import json

            return {
                "decision_type": "tool_call",
                "tool_name": tool_call.function.name,
                "arguments": json.loads(tool_call.function.arguments or "{}"),
                "token_usage": getattr(response.usage, "total_tokens", 0) or 0,
                "estimated_cost": 0.0,
            }
        content = choice.content or ""
        return {
            "decision_type": "final_response",
            "response": {"answer": content, "citations": [], "status": "ok"},
            "token_usage": getattr(response.usage, "total_tokens", 0) or 0,
            "estimated_cost": 0.0,
        }

    def handle_tool_result(self, event: dict[str, Any]) -> None:
        return None

    def handle_governor_feedback(self, event: dict[str, Any]) -> None:
        return None


def build_model_adapter(
    *,
    model_profile: dict[str, Any],
    scenario: dict[str, Any],
    mode: str,
    system_prompt: str,
    tool_definitions: list[dict[str, Any]],
) -> AgentModelAdapter:
    provider = model_profile["provider"]
    if provider == "mock":
        return MockScenarioAdapter(scenario=scenario, mode=mode)
    if provider == "openai_chat_completions":
        return OpenAIChatCompletionsAdapter(model_profile=model_profile, system_prompt=system_prompt)
    raise ValueError(f"unsupported model provider: {provider}")
