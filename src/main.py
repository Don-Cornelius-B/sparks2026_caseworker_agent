import json
import os
import sys
from src.client import ResidentHistoryClient
from src.guardrail import PolicyGuardrailEngine

def run_caseworker_morning(
    queue_path: str = "data/referral-queue.json",
    policy_path: str = "data/authority-policy.json"
):
    print("=" * 80)
    print("  CALDER COUNTY CASEWORKER ASSISTANT — MORNING TRIAGE RUNNER")
    print("  Policy: ACA-2026/1 (Amended by ACA-2026/2) | Mode: Deterministic Guardrails")
    print("=" * 80)

    if not os.path.exists(queue_path):
        print(f"[-] Error: Referral queue file not found at {queue_path}")
        sys.exit(1)

    client = ResidentHistoryClient()
    guardrails = PolicyGuardrailEngine(policy_path=policy_path)

    # API health check
    health = client.check_health()
    if health.get("status") != "ok":
        print(f"[!] Warning: Resident History API on port 8083 is unreachable. ({health})")
        print("[!] Ensure 'python services/history_service.py --port 8083' is running.\n")

    with open(queue_path, "r", encoding="utf-8") as f:
        referrals = json.load(f)

    print(f"[*] Loaded {len(referrals)} overnight referrals for processing.\n")

    triaged_count = 0
    escalated_count = 0
    handoff_count = 0

    for idx, ref in enumerate(referrals, start=1):
        ref_id = ref.get("referral_id")
        resident_ref = ref.get("resident_ref")
        requested_action = ref.get("requested_action")
        urgency = ref.get("urgency", "Standard")
        summary = ref.get("summary", "")

        print("-" * 80)
        print(f"[{idx}/{len(referrals)}] Processing Referral: {ref_id} | Resident: {resident_ref}")
        print(f"  Source: {ref.get('source')} | Urgency: {urgency}")
        print(f"  Requested Action: {requested_action}")
        print(f"  Summary: {summary}")

        # Step 1: Fetch Resident History & Household Composition
        print(f"  -> [Step 1: History API] Fetching record for {resident_ref}...")
        history = client.get_resident(resident_ref)

        if "error" in history:
            print(f"     [!] Failed to retrieve history: {history.get('error')}")
            current_award = "Unknown"
            events_count = 0
            household_members = []
        else:
            current_award = f"£{history.get('award_monthly', 0.0)}/mo ({history.get('benefit_code', 'N/A')})"
            events_count = len(history.get("events", []))
            household_members = history.get("household", [])
            print(f"     [+] History retrieved: District={history.get('district')}, Award={current_award}, Members={len(household_members)}, Events={events_count}")

        # Step 2: Policy Interceptor Gate (Evaluating Referral + Household Context)
        print(f"  -> [Step 2: Guardrail Gate] Checking authority policy boundaries...")
        decision = guardrails.evaluate(ref, resident_history=history)

        # Step 3: Branching Decision Paths (Permitted vs Escalation vs Hand-off)
        if decision.requires_escalation:
            escalated_count += 1
            print(f"     [❌ SUPERVISOR ESCALATION] Engages {decision.clause}")
            print(f"     Reason: {decision.reason}")
            print(f"  -> [Step 3: Output] Generated Supervisor Escalation Package:")
            print(f"        Action Prevented: {requested_action}")
            print(f"        Policy Clause: {decision.clause} ({decision.description})")
            print(f"        Required Action: Supervisor must review context and authorize/reject mutation.")

        elif decision.is_handoff:
            handoff_count += 1
            print(f"     [🤝 CASEWORKER HAND-OFF] Engages {decision.clause}")
            print(f"     Reason: {decision.reason}")
            print(f"  -> [Step 3: Output] Generated Caseworker Hand-off Package (No Note Drafted):")
            print(f"        Safeguarding Flag: Household includes minor under 18 or unverified composition.")
            print(f"        Preserved Context: District={history.get('district', 'N/A')} | Current Award={current_award}")
            print(f"        Household Profile: {household_members}")
            print(f"        Required Action: Caseworker must exercise direct judgment and draft note manually.")

        else:
            triaged_count += 1
            print(f"     [✅ PERMITTED] Cleared under {decision.clause}")
            print(f"  -> [Step 3: Output] Drafted Caseworker Triage Proposal:")
            print(f"        Proposal: Recommend standard caseworker review for '{requested_action}'.")
            print(f"        Case Status: Active ({current_award}) | Total Prior Events: {events_count}")

    print("\n" + "=" * 80)
    print("  MORNING SEQUENCE COMPLETED")
    print(f"  Total Processed: {len(referrals)}")
    print(f"  • Permitted Triage Proposals: {triaged_count}")
    print(f"  • Caseworker Hand-offs (Sec 3.9): {handoff_count}")
    print(f"  • Supervisor Escalations (Sec 3.1-3.8): {escalated_count}")
    print("=" * 80)

if __name__ == "__main__":
    run_caseworker_morning()