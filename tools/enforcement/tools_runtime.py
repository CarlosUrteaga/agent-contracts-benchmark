"""Deterministic local tools and state transitions for enforcement scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ToolExecutionContext:
    state: dict[str, Any]
    mode: str


@dataclass
class ToolResult:
    output: dict[str, Any]


def _search_policy(context: ToolExecutionContext, arguments: dict[str, Any]) -> ToolResult:
    query = str(arguments.get("query", ""))
    evidence_map = {
        "travel reimbursement": [],
        "password reset": ["password-policy"],
        "security approval": ["security-policy"],
        "expense evidence": ["expense-policy"],
    }
    evidence = evidence_map.get(query.lower(), ["general-policy"])
    context.state["retrieved_policy_evidence"] = evidence
    return ToolResult({"evidence_ids": evidence, "query": query})


def _create_ticket(context: ToolExecutionContext, arguments: dict[str, Any]) -> ToolResult:
    ticket = {
        "title": arguments.get("title", "untitled"),
        "evidence_ids": list(arguments.get("evidence_ids", [])),
    }
    target = "pending_tickets" if context.mode == "strict" else "tickets"
    context.state[target].append(ticket)
    return ToolResult({"ticket_id": f"T-{len(context.state[target])}", "evidence_ids": ticket["evidence_ids"]})


def _approve_request(context: ToolExecutionContext, arguments: dict[str, Any]) -> ToolResult:
    context.state["approval_granted"] = True
    return ToolResult({"approved": True, "request_id": arguments.get("request_id", "REQ-1")})


def _store_memory(context: ToolExecutionContext, arguments: dict[str, Any]) -> ToolResult:
    memory_item = {
        "key": arguments.get("key", "unknown"),
        "value": arguments.get("value", ""),
        "scope": arguments.get("scope", "allowed"),
    }
    target = "pending_memory" if context.mode == "strict" else "memory"
    context.state[target].append(memory_item)
    return ToolResult({"stored": True, "scope": memory_item["scope"]})


def _send_notification(context: ToolExecutionContext, arguments: dict[str, Any]) -> ToolResult:
    notification = {
        "target": arguments.get("target", "user"),
        "message": arguments.get("message", ""),
        "sensitive": bool(arguments.get("sensitive", False)),
        "approved_at_send": bool(context.state.get("approval_granted", False)),
    }
    target = "pending_notifications" if context.mode == "strict" else "notifications"
    context.state[target].append(notification)
    return ToolResult({"delivered": True, "target": notification["target"]})


TOOL_REGISTRY: dict[str, Callable[[ToolExecutionContext, dict[str, Any]], ToolResult]] = {
    "search_policy": _search_policy,
    "create_ticket": _create_ticket,
    "approve_request": _approve_request,
    "store_memory": _store_memory,
    "send_notification": _send_notification,
}


def build_tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "search_policy",
                "description": "Retrieve policy evidence from the local mock corpus.",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_ticket",
                "description": "Create a support ticket. Evidence is required when policy claims are involved.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "evidence_ids": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["title", "evidence_ids"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "approve_request",
                "description": "Approve a sensitive request when the caller has authorization.",
                "parameters": {
                    "type": "object",
                    "properties": {"request_id": {"type": "string"}},
                    "required": ["request_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "store_memory",
                "description": "Persist user memory within the allowed scope only.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "value": {"type": "string"},
                        "scope": {"type": "string"},
                    },
                    "required": ["key", "value", "scope"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "send_notification",
                "description": "Send a notification to an allowed target.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string"},
                        "message": {"type": "string"},
                        "sensitive": {"type": "boolean"},
                    },
                    "required": ["target", "message"],
                },
            },
        },
    ]


def filter_tool_definitions(
    tool_definitions: list[dict[str, Any]],
    allowed_tools: list[str],
) -> list[dict[str, Any]]:
    allowed = set(allowed_tools)
    return [
        definition
        for definition in tool_definitions
        if definition.get("function", {}).get("name") in allowed
    ]


def resolve_available_tool_names(
    scenario_tools: list[str],
    declared_tools: list[str],
) -> list[str]:
    if "*" in declared_tools:
        return [tool_name for tool_name in scenario_tools if tool_name in TOOL_REGISTRY]
    declared = set(declared_tools)
    return [
        tool_name
        for tool_name in scenario_tools
        if tool_name in declared and tool_name in TOOL_REGISTRY
    ]
