# Architectural & Design Decisions

1. Problem Chosen
Problem 5 — The Caseworker's Morning (Agentic AI / Guardrails)

2. Chronological Decision Log
Format of Log: `[HH : MM] - [ Decision Taken : Why Taken]`

DAY-1 : 
19:25 - Created AI-USAGE and Decisions File : Initialized mandatory compliance and design documentation files for the hackathon baseline.
19:50 - Added data packs from the zip file given by Brite : Organized referral queue and resident history service into isolated data/ and services/ directories.
21:05 - Added Authority Policy as a JSON file (data/authority-policy.json) : Decoupled ACA-2026/1 policy rules from program code into a declarative data schema to withstand future policy changes without code rewrites.
21:12 - Implemented Resident History API Client (src/client.py) : Encapsulated all HTTP communication, connection timeouts, and 404/500 error handling using standard library urllib to guarantee zero-dependency execution.
21:50 - Created Standalone File Registry (FILE_DOCUMENTATION.txt) : Documented the individual role and boundary of every file in the repository for clean-clone reviews.
22:35 - Added .gitignore and guardrail.py : Configured Python cache isolation and implemented deterministic pre-execution guardrail checks for Section 3 policy restrictions.
23:00 - Added main.py demo script : Implemented the 3-step morning runner (Read Queue -> Fetch History -> Guardrail Triage/Escalate) with full stdout execution tracing.

DAY-2:
14:10 - Recieved Challenge at 10:00 and checked the existing codebase to see if major changes are needed.
14:40 - Concluded that Minor changes are enough since the existing codebase on how input is processed is dynamic enough to handle the new requirements.
15:30 - Updated guardrail.py for Amendment ACA-2026/2 : Implemented dynamic date_of_birth evaluation across household records to detect minors under 18 as of 17 March 2026, establishing distinct caseworker hand-off decisions separate from supervisor escalations.
15:50 - Updated main.py for 3-way outcome routing : Implemented distinct branches for Permitted Triage Drafts (Sec 2.4), Caseworker Hand-offs for minor safeguarding (Sec 3.9), and Supervisor Escalations (Sec 3.1-3.8), preserving retrieved context without note generation on hand-offs.
17:10 - Created Unittest to test all the conditions and Edge cases:
    1. Test with dummy data representing an adult-only household
    2. Test with dummy data representing a household with a minor
20:00 - Updated tests to include new conditions for ACA-2026/2
20:05 - Tested all conditions and edge cases and everything was working as expected. Implemented a full system verification script in testing.txt


3. Structural Incapability: What the Agent Cannot Do & How We Know

What the Agent Cannot Do:
1. Cannot Mutate Benefits or Eligibility: The agent cannot alter a resident's entitlement, award amount, or eligibility status 
2. Cannot Terminate, Suspend, or Reinstate Awards: The agent cannot change the active/suspended status of any resident record 
3. Cannot Execute or Cancel Payments: The agent cannot trigger, alter, or cancel financial disbursements 
4. Cannot Update Banking or Payment Details: The agent cannot overwrite bank account or card information 
5. Cannot Transmit External Communications: The agent cannot dispatch letters, emails, or notifications to residents or third parties 
6. Cannot Assert Findings of Fact Regarding Conduct: The agent cannot create authoritative records accusing a resident of fraud or undeclared work

How We Know:

-> Absence of Mutation APIs (Transport Boundary): The tool client (`src/client.py`) only implements HTTP `GET` methods querying read endpoints (`/residents/<ref>`, `/household`, `/events`). There are no `POST`, `PUT`, `PATCH`, or `DELETE` methods in the codebase. The agent has no network pathway to write to any system.

-> Pre-Execution Guardrail Interception: The `PolicyGuardrailEngine` intercepts the referral payload before any downstream tool call or proposal generation. If an action engages a Section 3 restriction, execution immediately forks to an escalation packet generator and halts further automated processing for that referral.

-> Non-Binding Proposal Schema: Outputs for permitted referrals are explicitly typed as non-binding draft triage proposals (`TRIAGED_DRAFT`). They have zero operational effect on a case until a human caseworker reviews and adopts them (Section 2.4).

-> Deterministic Code Enforcement Over Prompts: Safety boundaries are hardcoded in standard Python data structures and logic. The system does not rely on LLM system prompt compliance to maintain guardrails.


4. Decisions of Change after Surprize challenge Dropped:

-> What was Changed :
    1. authority-policy.json : Since we had each policy in terms of JSON format, addition of a new policy wasn't that hard. 
    
-> What wasnt Changed :
    1. client.py : The client.py had no changes since the coding style and approach matched with the problem description perfectly.

