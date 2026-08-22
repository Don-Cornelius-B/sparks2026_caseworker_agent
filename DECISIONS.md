# Architectural & Design Decisions

1. Problem Chosen
Problem 5 — The Caseworker's Morning (Agentic AI / Guardrails)

2. Chronological Decision Log
Format of Log: `[HH : MM] - [ Decision Taken : Why Taken]`

19:25 - Created AI-USAGE and Decisions File : Initialized mandatory compliance and design documentation files for the hackathon baseline.
19:50 - Added data packs from the zip file given by Brite : Organized referral queue and resident history service into isolated data/ and services/ directories.
21:05 - Added Authority Policy as a JSON file (data/authority-policy.json) : Decoupled ACA-2026/1 policy rules from program code into a declarative data schema to withstand future policy changes without code rewrites.
21:12 - Implemented Resident History API Client (src/client.py) : Encapsulated all HTTP communication, connection timeouts, and 404/500 error handling using standard library urllib to guarantee zero-dependency execution.
21:50 - Created Standalone File Registry (FILE_DOCUMENTATION.txt) : Documented the individual role and boundary of every file in the repository for clean-clone reviews.
22:35 - Added .gitignore and guardrail.py : Configured Python cache isolation and implemented deterministic pre-execution guardrail checks for Section 3 policy restrictions.
23:00 - Added main.py demo script : Implemented the 3-step morning runner (Read Queue -> Fetch History -> Guardrail Triage/Escalate) with full stdout execution tracing.


3. Structural Incapability: What the Agent Cannot Do & How We Know

The Problem 5 specification mandates declaring what the agent is structurally incapable of doing without a human in the loop.

What the Agent Cannot Do:
1. Cannot Mutate Benefits or Eligibility: The agent cannot alter a resident's entitlement, award amount, or eligibility status 
2. Cannot Terminate, Suspend, or Reinstate Awards: The agent cannot change the active/suspended status of any resident record 
3. Cannot Execute or Cancel Payments: The agent cannot trigger, alter, or cancel financial disbursements 
4. Cannot Update Banking or Payment Details: The agent cannot overwrite bank account or card information 
5. Cannot Transmit External Communications: The agent cannot dispatch letters, emails, or notifications to residents or third parties 
6. Cannot Assert Findings of Fact Regarding Conduct: The agent cannot create authoritative records accusing a resident of fraud or undeclared work

How We Know:
Absence of Mutation APIs (Transport Boundary): The tool client (`src/client.py`) only implements HTTP `GET` methods querying read endpoints (`/residents/<ref>`, `/household`, `/events`). There are no `POST`, `PUT`, `PATCH`, or `DELETE` methods in the codebase. The agent has no network pathway to write to any system.
Pre-Execution Guardrail Interception: The `PolicyGuardrailEngine` intercepts the referral payload before any downstream tool call or proposal generation. If an action engages a Section 3 restriction, execution immediately forks to an escalation packet generator and halts further automated processing for that referral.
Non-Binding Proposal Schema: Outputs for permitted referrals are explicitly typed as non-binding draft triage proposals (`TRIAGED_DRAFT`). They have zero operational effect on a case until a human caseworker reviews and adopts them (Section 2.4).
Deterministic Code Enforcement Over Prompts: Safety boundaries are hardcoded in standard Python data structures and logic. The system does not rely on LLM system prompt compliance to maintain guardrails.