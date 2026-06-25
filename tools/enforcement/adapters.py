"""Model adapter interfaces for the enforcement benchmark."""

from __future__ import annotations

import json
import os
import time
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


def _trim_event_buffer(events: list[dict[str, Any]], *, limit: int = 4) -> None:
    if len(events) > limit:
        del events[:-limit]


def _format_tool_result_message(event: dict[str, Any]) -> str:
    return (
        "Recent tool result:\n"
        f"- tool_name: {event.get('tool_name')}\n"
        f"- arguments: {json.dumps(event.get('arguments', {}), sort_keys=True)}\n"
        f"- result: {json.dumps(event.get('result', {}), sort_keys=True)}"
    )


def _format_governor_feedback_message(event: dict[str, Any]) -> str:
    if event.get("type") == "recovery_ready":
        parts = [
            "Governor feedback:",
            f"- type: {event.get('type')}",
            f"- resolved_by_tool_name: {event.get('resolved_by_tool_name')}",
            f"- resolved_rule_ids: {event.get('resolved_rule_ids', [])}",
            f"- suggested_tool_name: {event.get('suggested_tool_name')}",
            f"- suggested_arguments: {json.dumps(event.get('suggested_arguments', {}), sort_keys=True)}",
        ]
        remediation_hint = event.get("remediation_hint")
        if remediation_hint:
            parts.append(f"- remediation_hint: {remediation_hint}")
        if event.get("do_not_repeat"):
            parts.append("- do_not_repeat: true")
        repeated_success_count = event.get("repeated_success_count")
        if repeated_success_count is not None:
            parts.append(f"- repeated_success_count: {repeated_success_count}")
        return "\n".join(parts)
    parts = [
        "Governor feedback:",
        f"- type: {event.get('type')}",
        f"- blocked_tool_name: {event.get('blocked_tool_name')}",
        f"- blocked_arguments: {json.dumps(event.get('blocked_arguments', {}), sort_keys=True)}",
        f"- rule_ids: {event.get('rule_ids', [])}",
    ]
    remediation_hint = event.get("remediation_hint")
    if remediation_hint:
        parts.append(f"- remediation_hint: {remediation_hint}")
    if event.get("do_not_repeat"):
        parts.append("- do_not_repeat: true")
    repeated_block_count = event.get("repeated_block_count")
    if repeated_block_count is not None:
        parts.append(f"- repeated_block_count: {repeated_block_count}")
    return "\n".join(parts)


def _augment_messages_with_agent_events(
    messages: list[dict[str, str]],
    *,
    tool_events: list[dict[str, Any]],
    feedback_events: list[dict[str, Any]],
) -> list[dict[str, str]]:
    augmented = list(messages)
    if tool_events:
        augmented.append({"role": "system", "content": _format_tool_result_message(tool_events[-1])})
    if feedback_events:
        augmented.append({"role": "system", "content": _format_governor_feedback_message(feedback_events[-1])})
    return augmented


@dataclass
class MockScenarioAdapter:
    """Deterministic adapter used for unit/integration tests and local dry runs."""

    scenario: dict[str, Any]
    mode: str
    _cursor: int = 0
    _decisions: list[dict[str, Any]] = field(default_factory=list)
    _tool_events: list[dict[str, Any]] = field(default_factory=list)
    _feedback_events: list[dict[str, Any]] = field(default_factory=list)

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
                "model_latency_ms": 0.0,
            }
        decision = dict(self._decisions[self._cursor])
        self._cursor += 1
        decision.setdefault("token_usage", 25)
        decision.setdefault("estimated_cost", 0.0)
        decision.setdefault("model_latency_ms", 0.0)
        return decision

    def handle_tool_result(self, event: dict[str, Any]) -> None:
        self._tool_events.append(dict(event))
        _trim_event_buffer(self._tool_events)

    def handle_governor_feedback(self, event: dict[str, Any]) -> None:
        self._feedback_events.append(dict(event))
        _trim_event_buffer(self._feedback_events)


@dataclass
class OpenAIChatCompletionsAdapter:
    """Real backend adapter using OpenAI Chat Completions tool calling."""

    model_profile: dict[str, Any]
    system_prompt: str
    _tool_events: list[dict[str, Any]] = field(default_factory=list)
    _feedback_events: list[dict[str, Any]] = field(default_factory=list)

    def _build_request_kwargs(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        request_messages = _augment_messages_with_agent_events(
            messages,
            tool_events=self._tool_events,
            feedback_events=self._feedback_events,
        )
        token_limit_parameter = str(self.model_profile.get("token_limit_parameter", "max_tokens"))
        if token_limit_parameter not in {"max_tokens", "max_completion_tokens"}:
            raise ValueError(f"unsupported token_limit_parameter: {token_limit_parameter}")
        kwargs: dict[str, Any] = {
            "model": self.model_profile["model_id"],
            "messages": request_messages,
            "tools": tools,
            "tool_choice": "auto",
            token_limit_parameter: self.model_profile["max_tokens"],
        }
        temperature = self.model_profile.get("temperature")
        if temperature is not None:
            kwargs["temperature"] = temperature
        return kwargs

    def _build_responses_request_kwargs(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        input_items: list[dict[str, Any]] = []
        for message in _augment_messages_with_agent_events(
            messages,
            tool_events=self._tool_events,
            feedback_events=self._feedback_events,
        ):
            input_items.append(
                {
                    "type": "message",
                    "role": message["role"],
                    "content": message["content"],
                }
            )
        response_tools: list[dict[str, Any]] = []
        for tool in tools:
            if tool.get("type") != "function":
                continue
            function = dict(tool.get("function", {}))
            response_tools.append(
                {
                    "type": "function",
                    "name": function["name"],
                    "description": function.get("description"),
                    "parameters": function.get("parameters"),
                    "strict": function.get("strict", False),
                }
            )
        kwargs: dict[str, Any] = {
            "model": self.model_profile["model_id"],
            "input": input_items,
            "text": {
                "format": {"type": "text"},
                "verbosity": str(self.model_profile.get("text_verbosity", "medium")),
            },
            "reasoning": {
                "effort": self.model_profile["reasoning_effort"],
                "summary": str(self.model_profile.get("reasoning_summary", "auto")),
            },
            "tools": response_tools,
            "tool_choice": "auto",
            "max_output_tokens": self.model_profile["max_tokens"],
            "store": bool(self.model_profile.get("store", True)),
            "include": list(
                self.model_profile.get(
                    "include",
                    ["reasoning.encrypted_content", "web_search_call.action.sources"],
                )
            ),
        }
        temperature = self.model_profile.get("temperature")
        if temperature is not None:
            kwargs["temperature"] = temperature
        return kwargs

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
        started = time.perf_counter()
        if self.model_profile.get("reasoning_effort"):
            kwargs = self._build_responses_request_kwargs(messages, tools)
            response = client.responses.create(**kwargs)
            model_latency_ms = round((time.perf_counter() - started) * 1000.0, 6)
            for output_item in response.output:
                if output_item.type == "function_call":
                    return {
                        "decision_type": "tool_call",
                        "tool_name": output_item.name,
                        "arguments": json.loads(output_item.arguments or "{}"),
                        "token_usage": _response_usage_tokens(response),
                        "estimated_cost": _response_cost(response),
                        "model_latency_ms": model_latency_ms,
                    }
            return {
                "decision_type": "final_response",
                "response": {"answer": response.output_text, "citations": [], "status": "ok"},
                "token_usage": _response_usage_tokens(response),
                "estimated_cost": _response_cost(response),
                "model_latency_ms": model_latency_ms,
            }
        kwargs = self._build_request_kwargs(messages, tools)
        response = client.chat.completions.create(**kwargs)
        model_latency_ms = round((time.perf_counter() - started) * 1000.0, 6)
        choice = response.choices[0].message
        if getattr(choice, "tool_calls", None):
            tool_call = choice.tool_calls[0]
            return {
                "decision_type": "tool_call",
                "tool_name": tool_call.function.name,
                "arguments": json.loads(tool_call.function.arguments or "{}"),
                "token_usage": getattr(response.usage, "total_tokens", 0) or 0,
                "estimated_cost": 0.0,
                "model_latency_ms": model_latency_ms,
            }
        content = choice.content or ""
        return {
            "decision_type": "final_response",
            "response": {"answer": content, "citations": [], "status": "ok"},
            "token_usage": getattr(response.usage, "total_tokens", 0) or 0,
            "estimated_cost": 0.0,
            "model_latency_ms": model_latency_ms,
        }

    def handle_tool_result(self, event: dict[str, Any]) -> None:
        self._tool_events.append(dict(event))
        _trim_event_buffer(self._tool_events)

    def handle_governor_feedback(self, event: dict[str, Any]) -> None:
        self._feedback_events.append(dict(event))
        _trim_event_buffer(self._feedback_events)


def _read_field(payload: Any, name: str, default: Any = None) -> Any:
    if isinstance(payload, dict):
        return payload.get(name, default)
    return getattr(payload, name, default)


def _response_usage_tokens(response: Any) -> int:
    usage = _read_field(response, "usage")
    if usage is None:
        return 0
    if hasattr(usage, "to_dict"):
        try:
            usage = usage.to_dict()
        except Exception:
            usage = usage
    total = _read_field(usage, "total_tokens", 0)
    try:
        return int(total or 0)
    except (TypeError, ValueError):
        return 0


def _response_cost(response: Any) -> float:
    metadata = _read_field(response, "_response_metadata", {})
    cost = _read_field(metadata, "cost")
    if cost in (None, ""):
        hidden = _read_field(response, "_hidden_params", {})
        cost = _read_field(hidden, "response_cost")
    try:
        return float(cost or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _normalize_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts: list[str] = []
        for item in content:
            text_value = _read_field(item, "text")
            if text_value:
                text_parts.append(str(text_value))
        return "\n".join(text_parts)
    return str(content or "")


def _optional_env(name: Any) -> str | None:
    if not name:
        return None
    value = os.getenv(str(name))
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


@dataclass
class LiteLLMAdapter:
    """Real backend adapter using LiteLLM with OpenAI-style tool calling."""

    model_profile: dict[str, Any]
    system_prompt: str
    _tool_events: list[dict[str, Any]] = field(default_factory=list)
    _feedback_events: list[dict[str, Any]] = field(default_factory=list)

    def generate_next_action(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        try:
            import litellm  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError("LiteLLM is required for the litellm adapter") from exc

        request_messages = _augment_messages_with_agent_events(
            messages,
            tool_events=self._tool_events,
            feedback_events=self._feedback_events,
        )
        kwargs: dict[str, Any] = {
            "model": self.model_profile["model_id"],
            "messages": request_messages,
            "tools": tools,
            "temperature": self.model_profile["temperature"],
            "max_tokens": self.model_profile["max_tokens"],
            **dict(self.model_profile.get("litellm_params", {})),
        }
        api_base = self.model_profile.get("api_base")
        api_base_from_env = _optional_env(self.model_profile.get("api_base_env"))
        if api_base_from_env:
            api_base = api_base_from_env
        if api_base:
            kwargs["api_base"] = api_base
        api_version = self.model_profile.get("api_version")
        api_version_from_env = _optional_env(self.model_profile.get("api_version_env"))
        if api_version_from_env:
            api_version = api_version_from_env
        if api_version:
            kwargs["api_version"] = api_version
        api_key_env = self.model_profile.get("api_key_env")
        if api_key_env:
            kwargs["api_key"] = _optional_env(api_key_env)

        started = time.perf_counter()
        response = litellm.completion(**kwargs)
        model_latency_ms = round((time.perf_counter() - started) * 1000.0, 6)

        choices = _read_field(response, "choices", []) or []
        if not choices:
            return {
                "decision_type": "final_response",
                "response": {"answer": "", "citations": [], "status": "refused"},
                "token_usage": _response_usage_tokens(response),
                "estimated_cost": _response_cost(response),
                "model_latency_ms": model_latency_ms,
            }
        choice = choices[0]
        message = _read_field(choice, "message", choice)
        tool_calls = _read_field(message, "tool_calls", []) or []
        if tool_calls:
            tool_call = tool_calls[0]
            function = _read_field(tool_call, "function", {})
            arguments_raw = _read_field(function, "arguments", "{}") or "{}"
            try:
                arguments = json.loads(arguments_raw)
            except json.JSONDecodeError:
                arguments = {}
            return {
                "decision_type": "tool_call",
                "tool_name": _read_field(function, "name", ""),
                "arguments": arguments,
                "token_usage": _response_usage_tokens(response),
                "estimated_cost": _response_cost(response),
                "model_latency_ms": model_latency_ms,
            }

        content = _normalize_content(_read_field(message, "content", ""))
        return {
            "decision_type": "final_response",
            "response": {"answer": content, "citations": [], "status": "ok"},
            "token_usage": _response_usage_tokens(response),
            "estimated_cost": _response_cost(response),
            "model_latency_ms": model_latency_ms,
        }

    def handle_tool_result(self, event: dict[str, Any]) -> None:
        self._tool_events.append(dict(event))
        _trim_event_buffer(self._tool_events)

    def handle_governor_feedback(self, event: dict[str, Any]) -> None:
        self._feedback_events.append(dict(event))
        _trim_event_buffer(self._feedback_events)


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
    if provider == "litellm":
        return LiteLLMAdapter(model_profile=model_profile, system_prompt=system_prompt)
    if provider == "openai_chat_completions":
        return OpenAIChatCompletionsAdapter(model_profile=model_profile, system_prompt=system_prompt)
    raise ValueError(f"unsupported model provider: {provider}")
