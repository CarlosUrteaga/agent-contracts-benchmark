"""Basic RAG enterprise policy assistant for T0."""

from __future__ import annotations

from app.documents import FALLBACK_RESPONSE, POLICY_DOCUMENTS
from app.retriever import retrieve_best_match
from app.schemas import AssistantResponse


class EnterprisePolicyAssistant:
    """Answer policy questions from a fixed in-code corpus."""

    def answer(self, query: str) -> AssistantResponse:
        document = retrieve_best_match(query, POLICY_DOCUMENTS)
        if document is None:
            return AssistantResponse(answer=FALLBACK_RESPONSE)
        return AssistantResponse(answer=document.content)
