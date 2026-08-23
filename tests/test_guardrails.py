import unittest
from src.guardrail import PolicyGuardrailEngine

class TestPolicyGuardrailEngine(unittest.TestCase):

    def setUp(self):
        self.engine = PolicyGuardrailEngine(policy_path="data/authority-policy.json")

    def test_permitted_adult_referral(self):
        """Standard review for household with adult members only should be permitted."""
        referral = {
            "referral_id": "RF-TEST-001",
            "requested_action": "Review award",
            "summary": "Resident reports change in hours."
        }
        history = {
            "household": [{"name": "Adult A", "date_of_birth": "1990-01-01"}]
        }
        decision = self.engine.evaluate(referral, resident_history=history)
        self.assertTrue(decision.is_permitted)
        self.assertFalse(decision.requires_escalation)
        self.assertFalse(decision.is_handoff)
        self.assertEqual(decision.clause, "Section 2.4")

    def test_section_3_2_suspension_blocked(self):
        """Suspension request must trigger a supervisor escalation."""
        referral = {
            "referral_id": "RF-TEST-002",
            "requested_action": "Suspend assistance pending investigation",
            "summary": "Anonymous report alleging undeclared employment."
        }
        history = {"household": [{"name": "Adult B", "date_of_birth": "1985-05-12"}]}
        decision = self.engine.evaluate(referral, resident_history=history)
        self.assertFalse(decision.is_permitted)
        self.assertTrue(decision.requires_escalation)
        self.assertFalse(decision.is_handoff)
        self.assertEqual(decision.clause, "Section 3.2")

    def test_section_3_4_payment_details_blocked(self):
        """Bank details change must trigger a supervisor escalation."""
        referral = {
            "referral_id": "RF-TEST-003",
            "requested_action": "Update payment details",
            "summary": "Resident requested bank account modification."
        }
        history = {"household": [{"name": "Adult C", "date_of_birth": "1978-11-20"}]}
        decision = self.engine.evaluate(referral, resident_history=history)
        self.assertFalse(decision.is_permitted)
        self.assertTrue(decision.requires_escalation)
        self.assertFalse(decision.is_handoff)
        self.assertEqual(decision.clause, "Section 3.4")

    def test_section_3_9_minor_safeguarding_handoff(self):
        """Household with a minor (<18 as of 2026-03-17) must trigger a caseworker hand-off."""
        referral = {
            "referral_id": "RF-TEST-004",
            "requested_action": "Review award",
            "summary": "New child in household."
        }
        history = {
            "household": [
                {"name": "Parent", "date_of_birth": "1995-02-10"},
                {"name": "Child", "date_of_birth": "2025-11-01"}  # Age < 18
            ]
        }
        decision = self.engine.evaluate(referral, resident_history=history)
        self.assertFalse(decision.is_permitted)
        self.assertFalse(decision.requires_escalation)
        self.assertTrue(decision.is_handoff)
        self.assertEqual(decision.clause, "Section 3.9")

    def test_section_5_2_missing_household_fallback(self):
        """Missing or unverified household composition must default to hand-off."""
        referral = {
            "referral_id": "RF-TEST-005",
            "requested_action": "Review award",
            "summary": "Address check."
        }
        decision = self.engine.evaluate(referral, resident_history=None)
        self.assertFalse(decision.is_permitted)
        self.assertFalse(decision.requires_escalation)
        self.assertTrue(decision.is_handoff)
        self.assertIn("Section 3.9", decision.clause)

if __name__ == "__main__":
    unittest.main()