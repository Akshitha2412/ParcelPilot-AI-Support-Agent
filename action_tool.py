import json
from pathlib import Path
from datetime import datetime


ESCALATION_FILE = Path("escalations.json")


# Roles allowed to create escalations
ALLOWED_ESCALATION_ROLES = {
    "manager"
}


def create_escalation(
    ticket_id: str,
    reason: str,
    confirmed: bool = False,
    user_role: str = "support"
) -> str:

    # --------------------------------------------------
    # 1. ACCESS CONTROL
    # --------------------------------------------------

    if user_role not in ALLOWED_ESCALATION_ROLES:

        return (
            "ACCESS_DENIED\n"
            "You do not have permission to create escalations. "
            "Manager approval is required."
        )

    # --------------------------------------------------
    # 2. HUMAN CONFIRMATION
    # --------------------------------------------------

    if not confirmed:

        return (
            "ESCALATION_READY\n"
            f"Ticket ID: {ticket_id}\n"
            f"Reason: {reason}\n\n"
            "User confirmation is required before "
            "creating the escalation."
        )

    # --------------------------------------------------
    # 3. CREATE ESCALATION
    # --------------------------------------------------

    escalation = {
        "ticket_id": ticket_id,
        "reason": reason,
        "created_at": datetime.now().isoformat(),
        "created_by_role": user_role,
        "status": "created"
    }

    # --------------------------------------------------
    # 4. LOAD EXISTING ESCALATIONS
    # --------------------------------------------------

    existing = []

    if ESCALATION_FILE.exists():

        try:

            with open(
                ESCALATION_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                existing = json.load(f)

        except (json.JSONDecodeError, FileNotFoundError):

            existing = []

    # --------------------------------------------------
    # 5. SAVE NEW ESCALATION
    # --------------------------------------------------

    existing.append(escalation)

    with open(
        ESCALATION_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            existing,
            f,
            indent=4
        )

    # --------------------------------------------------
    # 6. RETURN RESULT
    # --------------------------------------------------

    return (
        "ESCALATION_CREATED\n"
        f"Ticket ID: {ticket_id}\n"
        f"Reason: {reason}\n"
        "Status: created"
    )