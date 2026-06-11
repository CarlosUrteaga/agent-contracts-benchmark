"""Fixed in-code policy corpus for the T0 assistant."""

from __future__ import annotations

from app.schemas import PolicyDocument

POLICY_DOCUMENTS = [
    PolicyDocument(
        document_id="vacation-policy",
        title="Vacation Policy",
        content=(
            "Vacation policy: Full-time employees receive 15 vacation days per "
            "year. Requests should be submitted in the HR system at least two "
            "weeks before the planned leave."
        ),
    ),
    PolicyDocument(
        document_id="password-reset-policy",
        title="Password Reset Policy",
        content=(
            "Password reset policy: Employees must use the self-service password "
            "reset portal and complete multi-factor authentication before setting "
            "a new password."
        ),
    ),
    PolicyDocument(
        document_id="expense-policy",
        title="Expense Reimbursement Policy",
        content=(
            "Expense reimbursement policy: Employees must submit itemized receipts "
            "within 30 days of travel or purchase. Manager approval is required "
            "for any expense above 500 dollars."
        ),
    ),
]

FALLBACK_RESPONSE = (
    "I could not find a matching policy in the T0 policy corpus."
)
