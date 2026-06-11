"""Deterministic keyword-overlap retrieval for the T0 assistant."""

from __future__ import annotations

import re

from app.schemas import PolicyDocument

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a",
    "an",
    "and",
    "at",
    "before",
    "do",
    "for",
    "how",
    "i",
    "in",
    "is",
    "my",
    "of",
    "or",
    "the",
    "to",
    "today",
    "what",
    "within",
}


def tokenize(text: str) -> set[str]:
    """Normalize text to lowercase alphanumeric tokens."""

    return {
        token for token in TOKEN_PATTERN.findall(text.lower()) if token not in STOPWORDS
    }


def retrieve_best_match(
    query: str, documents: list[PolicyDocument]
) -> PolicyDocument | None:
    """Return the top matching document by overlap count and document order."""

    query_tokens = tokenize(query)
    best_document: PolicyDocument | None = None
    best_score = 0

    for document in documents:
        score = len(query_tokens & tokenize(document.content))
        if score > best_score:
            best_document = document
            best_score = score

    return best_document
