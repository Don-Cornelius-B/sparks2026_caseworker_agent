import json
import os
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Any, Optional, List

# Policy reference date for the morning intake batch
REFERRAL_BATCH_DATE = date(2026, 3, 17)

@dataclass
class GuardrailDecision:
    """Represents the structured outcome of an authority policy check."""
    is_permitted: bool
    requires_escalation: bool
    is_handoff: bool
    clause: str
    description: str
    reason: str

class PolicyGuardrailEngine:
    """
    Deterministic policy interceptor enforcing Calder County 
    Authority Policy ACA-2026/1 as amended by ACA-2026/2.
    """

    def __init__(self, policy_path: str = "data/authority-policy.json"):
        if not os.path.exists(policy_path):
            raise FileNotFoundError(f"Authority policy not found at: {policy_path}")
        with open(policy_path, "r", encoding="utf-8") as f:
            self.policy = json.load(f)
        self.restrictions = self.policy.get("section_3_restrictions", [])

    def _calculate_age(self, dob_str: str, as_of: date = REFERRAL_BATCH_DATE) -> Optional[int]:
        """Calculates age in years from a YYYY-MM-DD string as of the batch date."""
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            return as_of.year - dob.year - ((as_of.month, as_of.day) < (dob.month, dob.day))
        except (ValueError, TypeError):
            return None

    def evaluate(
        self, 
        referral: Dict[str, Any], 
        resident_history: Optional[Dict[str, Any]] = None
    ) -> GuardrailDecision:
        """
        Evaluates a referral and resident history against Section 3 restrictions.
        Branches into Permitted, Supervisor Escalation, or Caseworker Hand-off.
        """
        action = referral.get("requested_action", "")
        summary = referral.get("summary", "")
        combined_text = f"{action} {summary}".lower()

        # Step A: Check Section 3.1 to 3.8 Out-of-Authority Escalations
        for rule in self.restrictions:
            if rule.get("clause") == "3.9":
                continue  # Evaluated via household data below
            for trigger in rule.get("match_triggers", []):
                if trigger.lower() in combined_text:
                    return GuardrailDecision(
                        is_permitted=False,
                        requires_escalation=True,
                        is_handoff=False,
                        clause=f"Section {rule['clause']}",
                        description=rule.get("description", ""),
                        reason=(
                            f"Action '{action}' engages Section {rule['clause']} "
                            f"({rule.get('description', '')}). Matched trigger: '{trigger}'."
                        )
                    )

        # Step B: Check Section 3.9 Safeguarding Restriction (Minor in Household)
        if resident_history is None or "error" in resident_history:
            # Policy Section 5.2 & 6.1: Default to applying 3.9 if household cannot be established
            return GuardrailDecision(
                is_permitted=False,
                requires_escalation=False,
                is_handoff=True,
                clause="Section 3.9 (via 5.2 / 6.1)",
                description="Drafting triage note prohibited - unconfirmed household composition",
                reason="Household composition cannot be established from records. Defaulting to caseworker hand-off."
            )

        household = resident_history.get("household", [])
        for member in household:
            dob = member.get("date_of_birth")
            age = self._calculate_age(dob)
            if age is not None and age < 18:
                return GuardrailDecision(
                    is_permitted=False,
                    requires_escalation=False,
                    is_handoff=True,
                    clause="Section 3.9",
                    description="Drafting triage note prohibited for household with minor under 18",
                    reason=(
                        f"Household includes a minor ({member.get('name', 'Dependent')}, "
                        f"Age: {age}, DOB: {dob}). Requires human caseworker judgment from the outset."
                    )
                )

        # Step C: Permitted under Section 2.4 (Adults only, no restricted mutations)
        return GuardrailDecision(
            is_permitted=True,
            requires_escalation=False,
            is_handoff=False,
            clause="Section 2.4",
            description="Drafting triage note proposal",
            reason="Permitted to retrieve history and draft non-binding triage proposal."
        )