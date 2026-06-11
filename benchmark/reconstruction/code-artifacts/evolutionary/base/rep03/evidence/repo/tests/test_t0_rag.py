#!/usr/bin/env python3
"""T0 tests for the basic enterprise policy assistant."""

from __future__ import annotations

import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import EnterprisePolicyAssistant
from app.documents import FALLBACK_RESPONSE, POLICY_DOCUMENTS
from app.retriever import retrieve_best_match


class EnterprisePolicyAssistantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assistant = EnterprisePolicyAssistant()

    def test_vacation_query_returns_vacation_policy(self) -> None:
        response = self.assistant.answer("How many vacation days do employees get?")
        self.assertIn("15 vacation days", response.answer)

    def test_password_reset_query_returns_password_policy(self) -> None:
        response = self.assistant.answer("How do I reset my password?")
        self.assertIn("self-service password reset portal", response.answer)

    def test_unrelated_query_returns_fallback(self) -> None:
        response = self.assistant.answer("What is the cafeteria lunch menu today?")
        self.assertEqual(FALLBACK_RESPONSE, response.answer)

    def test_tie_behavior_is_deterministic(self) -> None:
        result = retrieve_best_match("employees policy", POLICY_DOCUMENTS)
        self.assertIsNotNone(result)
        self.assertEqual("vacation-policy", result.document_id)


if __name__ == "__main__":
    unittest.main()
