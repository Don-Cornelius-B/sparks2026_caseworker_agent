import json
import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class GuardrailDecision:
    """Represents the outcome of an authority policy check."""
    is_permitted: bool
    requires_escalation: bool
    clause: str
    description: str
    reason: str

class PolicyGuardrailEngine:
    """
    Hard policy interceptor that validates requested referral actions
    against Calder County Authority Policy ACA-2026/1.
    """

    def __init__(self, policy_path: str = "data/authority-policy.json"):
        if not os.path.exists(policy_path):
            raise FileNotFoundError(f"Authority policy file not found at: {policy_path}")
        with open(policy_path, "r", encoding="utf-8") as f:
            self.policy_data = json.load(f)
        
        self.restrictions = self.policy_data.get("section_3_restrictions", [])

    def evaluate(self, referral: Dict[str, Any]) -> GuardrailDecision:
        """
        Evaluates a referral against Section 3 prohibitions.
        If an action matches a restricted trigger, halts processing and routes to escalation.
        """
        requested_action = referral.get("requested_action", "").strip()
        summary = referral.get("summary", "").strip()
        combined_text = f"{requested_action} {summary}".lower()

        # Check against declarative Section 3 prohibitions
        for rule in self.restrictions:
            for trigger in rule.get("match_triggers", []):
                if trigger.lower() in combined_text:
                    return GuardrailDecision(
                        is_permitted=False,
                        requires_escalation=True,
                        clause=f"Section {rule['clause']}",
                        description=rule["description"],
                        reason=(
                            f"Action '{requested_action}' engages Section {rule['clause']} "
                            f"({rule['description']}). Trigger matched: '{trigger}'."
                        )
                    )

        # Permitted under Section 2.4 (Proposals / non-binding triage notes)
        return GuardrailDecision(
            is_permitted=True,
            requires_escalation=False,
            clause="Section 2.4",
            description="Drafting non-binding triage note proposal",
            reason="Action permitted for non-binding casework triage proposal."
        )