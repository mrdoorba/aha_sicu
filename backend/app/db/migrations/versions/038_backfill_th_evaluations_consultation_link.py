"""Backfill TH saved evaluations with the TH approved consultation link

Updates historical TH approved evaluations so stored scoring_summary and
email_output snapshots use th-bd2.ahacommerce.net instead of
cal-bd2.ahacommerce.net.

Revision ID: 038
Revises: 037
Create Date: 2026-04-30
"""

import json
from copy import deepcopy

import sqlalchemy as sa
from alembic import op

revision = "038"
down_revision = "037"
branch_labels = None
depends_on = None

OLD_LINK = "cal-bd2.ahacommerce.net"
NEW_LINK = "th-bd2.ahacommerce.net"
OLD_I18N_KEY = "closing.potential"
NEW_I18N_KEY = "closing.potentialTh"


def _load_jsonb(value: object) -> object:
    return json.loads(value) if isinstance(value, str) else value


def _rewrite_calculator_results(
    calc_results: object,
    from_link: str,
    to_link: str,
    from_key: str,
    to_key: str,
) -> tuple[object, bool]:
    if not isinstance(calc_results, dict):
        return calc_results, False

    updated = deepcopy(calc_results)
    summary = updated.get("scoring_summary")
    if not isinstance(summary, dict):
        return calc_results, False

    changed = False

    closing_message = summary.get("closing_message")
    if isinstance(closing_message, str):
        replaced = closing_message.replace(from_link, to_link)
        if replaced != closing_message:
            summary["closing_message"] = replaced
            changed = True

    closing_message_i18n = summary.get("closing_message_i18n")
    if isinstance(closing_message_i18n, dict) and closing_message_i18n.get("key") == from_key:
        closing_message_i18n["key"] = to_key
        changed = True

    return (updated if changed else calc_results), changed


def _rewrite_email_output(email_output: object, from_link: str, to_link: str) -> tuple[object, bool]:
    if not isinstance(email_output, str):
        return email_output, False
    updated = email_output.replace(from_link, to_link)
    return updated, updated != email_output


def _backfill(from_link: str, to_link: str, from_key: str, to_key: str) -> None:
    conn = op.get_bind()
    rows = conn.execute(
        sa.text(
            "SELECT id, calculator_results, email_output "
            "FROM evaluations "
            "WHERE marketplace = 'TH' AND verdict = '✔️'"
        )
    ).fetchall()

    for row in rows:
        evaluation_id = row[0]
        calculator_results = _load_jsonb(row[1])
        email_output = row[2]

        new_calculator_results, calc_changed = _rewrite_calculator_results(
            calculator_results,
            from_link,
            to_link,
            from_key,
            to_key,
        )
        new_email_output, email_changed = _rewrite_email_output(
            email_output,
            from_link,
            to_link,
        )

        if not calc_changed and isinstance(calculator_results, dict):
            summary = calculator_results.get("scoring_summary")
            if isinstance(summary, dict):
                closing_message_i18n = summary.get("closing_message_i18n")
                if isinstance(closing_message_i18n, dict) and closing_message_i18n.get("key") == from_key:
                    new_calculator_results = deepcopy(calculator_results)
                    new_calculator_results["scoring_summary"]["closing_message_i18n"]["key"] = to_key
                    calc_changed = True

        if not calc_changed and not email_changed:
            continue

        conn.execute(
            sa.text(
                "UPDATE evaluations "
                "SET calculator_results = CAST(:calculator_results AS jsonb), "
                "    email_output = :email_output "
                "WHERE id = :evaluation_id"
            ),
            {
                "evaluation_id": evaluation_id,
                "calculator_results": json.dumps(new_calculator_results),
                "email_output": new_email_output,
            },
        )


def upgrade() -> None:
    _backfill(OLD_LINK, NEW_LINK, OLD_I18N_KEY, NEW_I18N_KEY)


def downgrade() -> None:
    _backfill(NEW_LINK, OLD_LINK, NEW_I18N_KEY, OLD_I18N_KEY)
