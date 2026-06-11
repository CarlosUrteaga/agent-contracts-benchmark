"""Typed structures for the T0 enterprise policy assistant."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyDocument:
    """A single policy document in the fixed T0 corpus."""

    document_id: str
    title: str
    content: str


@dataclass(frozen=True)
class AssistantResponse:
    """A minimal text-only assistant response for T0."""

    answer: str
