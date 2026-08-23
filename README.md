# Calder County Automated Caseworker Assistant

> **Problem Track 5:** The Caseworker's Morning (Agentic AI / Guardrails)  
> **Policy Reference:** Calder County Authority Policy ACA-2026/1  
> **Execution Environment:** Python 3.10+ (Standard Library Only — Zero Third-Party Dependencies)

---

## 1. What does this project do, and why did you build it?

### The Morning Intake Problem
In Calder County Social Services, caseworkers spend up to 40 minutes every morning performing repetitive, manual triage operations on overnight resident referrals. This routine workflow consists of three mechanical steps:
1. **Reading Overnight Referrals:** Ingesting intake requests submitted by housing teams, health visitors, district offices, and self-referrals.
2. **Retrieving Resident History:** Querying county databases for resident profiles, current award amounts, household compositions, and historical case events.
3. **Drafting Non-Binding Triage Notes:** Writing initial assessment summaries and categorizing urgency levels before actual casework begins.

### Why Deterministic Guardrails Are Necessary
While automating this sequence saves hundreds of staff hours annually, public sector casework carries strict legal and ethical boundaries. Generative AI models and LLM agents are inherently non-deterministic—they can suffer from hallucinations, prompt injections, or over-helpful behavior that attempts unauthorized actions.

Under **Calder County Authority Policy ACA-2026/1**:
- **Strictly Prohibited Mutations:** AI systems must **never** alter benefit entitlement amounts, suspend or terminate awards (even upon fraud allegations), execute payments, modify resident bank details, or send unapproved communications to residents.
- **Hard Code Interception:** Safety guardrails cannot rely on "soft" LLM system prompts. They must be enforced as **deterministic approval gates in application code** that evaluate requests before any downstream processing occurs.
- **Default-to-Escalate (Section 6.1):** Any action engaging a Section 3 restriction—or any unclassified, high-risk request—must halt automated processing immediately and generate a structured escalation package for a human supervisor.
- **Day 2 Policy Resilience:** Policy rules are decoupled from application logic into a declarative JSON schema ([`data/authority-policy.json`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/data/authority-policy.json)). When policy amendments occur, rules can be updated dynamically without touching or refactoring codebase logic.

---

## Compliance with "The Floor" Requirements

This implementation satisfies all five mandatory criteria established for Problem Track 5:

| Criterion | Requirement Summary | Implementation & Verification Evidence | Status |
| :--- | :--- | :--- | :---: |
| **1. Complete 3-Step Run** | Executes overnight queue, pulls API history, drafts non-binding triage notes. | [`src/main.py`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/src/main.py) completes all 12 overnight referrals sequentially without failure. | ✅ PASS |
| **2. Visible Execution Trace** | Real-time `stdout` trace inspectable by human supervisors. | CLI outputs structured logs per referral showing step-by-step API responses, guardrail checks, and decisions. | ✅ PASS |
| **3. Hard Code Approval Gate** | Interceptor prevents irreversible mutations pre-execution. | [`src/guardrail.py`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/src/guardrail.py) intercepts referrals before processing; [`src/client.py`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/src/client.py) lacks write HTTP methods. | ✅ PASS |
| **4. Refusal & Escalation** | Out-of-authority items are blocked and escalated without queue crash. | RF-2026-0415 (fraud suspension), RF-2026-0422 (reinstatement), and RF-2026-0423 (banking update) are safely escalated. | ✅ PASS |
| **5. Clean Clone Execution** | Zero `pip` dependencies; standard library Python 3.10+ only. | Uses standard Python modules (`json`, `urllib`, `dataclasses`, `http.server`, `argparse`). | ✅ PASS |

---

## 2. What does the architecture look like?

### Resilient Pipeline Flow

```mermaid
flowchart TD
    A["Overnight Referral Queue\n(data/referral-queue.json)"] --> B["CLI Intake Orchestrator\n(src/main.py)"]
    B --> Step1["Step 1: Fetch History Profile"]
    Step1 --> C["Resident History API Client\n(src/client.py)"]
    C -->|HTTP GET :8083| D["Mock Resident History Server\n(services/history_service.py)"]
    D -->|JSON Profile Data| C
    C --> Step2["Step 2: Policy Interceptor Gate"]
    Step2 --> E["Policy Guardrail Engine\n(src/guardrail.py)"]
    E <-->|Evaluate Rules| F["Declarative Policy Schema\n(data/authority-policy.json)"]
    E --> Decision{"Policy Check\nOutcome"}
    
    Decision -->|PERMITTED\n(Section 2.4)| Step3A["Step 3A: Draft Non-Binding Triage Proposal"]
    Decision -->|RESTRICTED\n(Section 3.1 - 3.8)| Step3B["Step 3B: Block & Generate Supervisor Escalation Package"]
    
    Step3A --> G["Caseworker Inspection Log (stdout)"]
    Step3B --> G
```

### Component Responsibility Matrix

| Component File | Role & Technical Responsibility | Key Architectural Boundary |
| :--- | :--- | :--- |
| [`data/authority-policy.json`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/data/authority-policy.json) | **Declarative Policy Schema:** Encodes Policy ACA-2026/1 Section 2 permitted actions and Section 3 match triggers. | Decouples policy rules from Python source code for Day 2 flexibility. |
| [`data/referral-queue.json`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/data/referral-queue.json) | **Intake Queue Dataset:** Contains 12 overnight intake referrals (RF-2026-0412 through RF-2026-0423). | Mock intake buffer representing overnight resident communications. |
| [`services/history_service.py`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/services/history_service.py) | **Mock History API Server:** Standalone HTTP server (`ThreadingHTTPServer`) running on port 8083. | Simulates county resident backend database (`/residents/<ref>`). |
| [`src/client.py`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/src/client.py) | **HTTP Transport Client:** `ResidentHistoryClient` utilizing standard library `urllib.request`. | **Read-Only Boundary:** Implements HTTP `GET` only; zero write methods exist. |
| [`src/guardrail.py`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/src/guardrail.py) | **Deterministic Guardrail Engine:** `PolicyGuardrailEngine` evaluating requests against policy rules pre-execution. | Hard code approval gate intercepting out-of-authority actions. |
| [`src/main.py`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/src/main.py) | **Intake Loop Orchestrator:** Manages the 3-step morning sequence, stdout execution tracing, and fault isolation. | Coordinates queue iteration, error handling, and terminal output. |
| [`FILE_DOCUMENTATION.txt`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/FILE_DOCUMENTATION.txt) | **Standalone File Registry:** Provides complete file role maps for clean-clone code audits. | Repository inventory and structural boundary documentation. |
| [`DECISIONS.md`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/DECISIONS.md) | **Decision Log & Incapability Spec:** Records architectural choices and structural incapability declarations. | Audit trail of design choices and safety proofs. |
| [`AI-USAGE.md`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/AI-USAGE.md) | **AI Disclosure Log:** Documents Gemini AI assistant usage during system development. | Hackathon governance and compliance tracking. |

---

## 3. How do I run this locally, and how do I deploy it?

### Local Execution (Zero-Dependency Setup)

#### Prerequisites
- **Python 3.10+** (Standard installation; no virtual environments or `pip install` required).

#### Step 1: Launch the Resident History API Service
Open Terminal 1 and start the mock backend server on port 8083:
```bash
python services/history_service.py --port 8083
```
*Expected Output:*
```text
Resident History API on http://127.0.0.1:8083  (12 residents)
```

#### Step 2: Execute the Caseworker Morning Agent
Open Terminal 2 and run the intake loop orchestrator:
```bash
python -m src.main
```

#### Sample Execution Trace Output Excerpt
```text
================================================================================
  CALDER COUNTY CASEWORKER ASSISTANT — MORNING TRIAGE RUNNER
  Policy Reference: ACA-2026/1 | Engine Mode: Deterministic Guardrails
================================================================================
[*] Loaded 12 overnight referrals for processing.

--------------------------------------------------------------------------------
[1/12] Processing Referral: RF-2026-0412 | Resident: R-20500
  Source: Housing Options | Urgency: Standard
  Requested Action: Review award
  Summary: Resident reports rent arrears following reduction in hours. Requests review of award.
  -> [Step 1: History API] Fetching record for R-20500...
     [+] History retrieved: District=Ash Hill, Award=£988.04/mo (HSP-A), Events=4
  -> [Step 2: Guardrail Gate] Checking authority policy boundaries...
     [✅ PERMITTED] Cleared under Section 2.4
  -> [Step 3: Output] Drafted Caseworker Triage Proposal:
        Proposal: Recommend standard caseworker review for 'Review award'.
        Case Status: Active (£988.04/mo (HSP-A)) | Total Prior Events: 4
--------------------------------------------------------------------------------
...
--------------------------------------------------------------------------------
[4/12] Processing Referral: RF-2026-0415 | Resident: R-20521
  Source: Counter-Fraud Unit | Urgency: High
  Requested Action: Suspend assistance pending investigation
  Summary: Anonymous report alleging undeclared employment. Unit requests assistance be suspended pending investigation.
  -> [Step 1: History API] Fetching record for R-20521...
     [+] History retrieved: District=Ash Hill, Award=£808.52/mo (HSP-B), Events=4
  -> [Step 2: Guardrail Gate] Checking authority policy boundaries...
     [❌ BLOCKED & ESCALATED] Engages Section 3.2
     Reason: Action 'Suspend assistance pending investigation' engages Section 3.2 (Suspension, termination, or reinstatement of an award). Trigger matched: 'suspend'.
  -> [Step 3: Output] Generated Supervisor Escalation Package:
        Action Prevented: Suspend assistance pending investigation
        Violation Clause: Section 3.2 (Suspension, termination, or reinstatement of an award)
        Supervisor Action Needed: Review referral context and authorize/reject mutation manually.
--------------------------------------------------------------------------------
...
================================================================================
  MORNING SEQUENCE COMPLETED
  Total Processed: 12 | Permitted Triaged: 9 | Blocked/Escalated: 3
================================================================================
```

---

### Production Deployment Blueprint

```
                     ┌─────────────────────────────────────────┐
                     │    Enterprise Kafka / SQS Bus          │
                     │    Topic: referral.intake.v1            │
                     └────────────────────┬────────────────────┘
                                          │
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│ Containerized Caseworker Agent (python:3.11-alpine)                           │
│                                                                               │
│  ┌───────────────────────────┐         ┌───────────────────────────────────┐  │
│  │ Environment Config        │         │ Policy Engine (Local Vault Sync)  │  │
│  │ RESIDENT_HISTORY_API_URL  │         │ /etc/policy/authority-policy.json │  │
│  └─────────────┬─────────────┘         └─────────────────┬─────────────────┘  │
│                │                                         │                    │
│                ▼                                         ▼                    │
│  ┌───────────────────────────┐         ┌───────────────────────────────────┐  │
│  │ HTTP Transport (mTLS)     │────────►│ Pre-Execution Guardrail Interceptor│  │
│  └───────────────────────────┘         └─────────────────┬─────────────────┘  │
└──────────────────────────────────────────────────────────┼────────────────────┘
                                                           │
                                   ┌───────────────────────┴───────────────────────┐
                                   ▼                                               ▼
                     ┌───────────────────────────┐                   ┌───────────────────────────┐
                     │ Kafka: triage.proposals.v1│                   │ Kafka: supervisor.alerts  │
                     └─────────────┬─────────────┘                   └─────────────┬─────────────┘
                                   │                                               │
                                   ▼                                               ▼
                     ┌───────────────────────────┐                   ┌───────────────────────────┐
                     │ Caseworker UI Dashboard   │                   │ Supervisor Approval Portal│
                     └───────────────────────────┘                   └───────────────────────────┘
```

1. **Containerization:** Packaged using a lightweight Docker container (`python:3.11-alpine`) running as a non-root user for security isolation.
2. **Scheduled Batch & Event Orchestration:** Deployed as a Kubernetes `CronJob` firing daily at 06:00 AM, or integrated with an event-driven worker consuming from an enterprise message bus (Apache Kafka / AWS SQS).
3. **Live System Integration:** Endpoints configured dynamically via environment variables (`RESIDENT_HISTORY_API_URL`), communicating over secure mTLS with OAuth2 Bearer token authentication managed via HashiCorp Vault / AWS Secrets Manager.
4. **Output Queue Routing:** Permitted draft proposals published to `caseworker.proposals.v1` for caseworker review; escalation packages routed directly to `supervisor.escalations.v1` with webhook notifications to team leads.

---

## 4. What decisions did you make, and why?

### Summary of Key Architectural Trade-offs

#### 1. Policy-as-Data Schema vs. Hardcoded `if/else` Statements
- **Decision:** Decoupled Calder County Policy ACA-2026/1 into a structured JSON configuration ([`data/authority-policy.json`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/data/authority-policy.json)) loaded dynamically by [`src/guardrail.py`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/src/guardrail.py).
- **Rationale:** Hardcoding policy rules directly into Python `if/else` logic creates tight coupling. When policy amendments occur on "Day 2", modifying Python code requires code reviews, unit test updates, and container re-deployments. Policy-as-Data allows legal and compliance teams to update match triggers dynamically without touching application code.

#### 2. Structural Incapability vs. LLM System Prompt Policing
- **Decision:** Restricted the HTTP client transport layer ([`src/client.py`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/src/client.py)) strictly to read-only `GET` requests, omitting all write methods (`POST`, `PUT`, `PATCH`, `DELETE`).
- **Rationale:** Relying solely on LLM prompts ("Do not alter bank details") introduces vulnerabilities to prompt injections or model hallucinations. Structural incapability ensures that even if an LLM attempted to execute a write action, the underlying software transport physically lacks the code to execute write network calls.

#### 3. Python Standard Library Only vs. Heavy Agent Frameworks (LangChain/CrewAI)
- **Decision:** Built the entire agent workflow using standard library Python 3.10+ modules without installing third-party `pip` packages.
- **Rationale:** Frameworks like LangChain add massive dependency chains, potential security vulnerabilities, breaking API changes, and unnecessary overhead. Standard library implementation guarantees zero supply chain risk, deterministic execution speed, instant clean-clone portability, and total transparency for security audits.

#### 4. Fault Isolation & Queue Continuity (Policy Section 4.3)
- **Decision:** Wrapped referral evaluation in localized exception handlers within [`src/main.py`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/src/main.py).
- **Rationale:** If an API lookup fails for a single resident record or a referral payload contains malformed fields, the system logs an isolated warning and continues processing the remaining queue items. This fulfills Policy Section 4.3, ensuring that individual referral failures do not stall the entire morning triage pipeline.

---

## 5. What would you improve if you continued working on it?

If given additional time to evolve the Calder County Caseworker Assistant, the following enhancements would be prioritized:

1. **Hybrid Semantic Guardrail Classification:**
   - *Current State:* Keyword and phrase trigger matching in [`src/guardrail.py`](file:///d:/Don/GithubClones/sparks2026_caseworker_agent/src/guardrail.py).
   - *Enhancement:* Integrate a small, local, deterministic embedding model (or regularized zero-shot classifier) to detect subtle policy violations that use indirect or non-standard language, ensuring high semantic coverage while maintaining local execution safety.

2. **Supervisor Webhook & Approval Portal:**
   - *Current State:* Supervisor escalation packages logged to `stdout`.
   - *Enhancement:* Develop an interactive web dashboard where senior caseworkers receive real-time push notifications for Section 3 escalations, view resident history side-by-side with requested actions, and issue 1-click cryptographic approvals or refusals.

3. **Tamper-Evident Cryptographic Audit Ledger (Policy Section 5):**
   - *Current State:* In-memory trace logging during intake execution.
   - *Enhancement:* Implement SHA-256 hash chaining (an append-only cryptographic ledger) for every referral ingest, guardrail evaluation, and generated proposal, creating a legally defensible audit trail compliant with Section 5 audit mandates.

4. **Automated Policy Regression & Diff Testing Suite:**
   - *Current State:* Manual verification against 12 mock referrals.
   - *Enhancement:* Build a CI/CD test harness that evaluates updated `authority-policy.json` schema releases against thousands of historical referral edge cases to highlight potential over-blocking or policy leaks prior to production deployment.

---

## Repository Structure

```text
sparks2026_caseworker_agent/
├── README.md                      # Primary technical guide and documentation
├── DECISIONS.md                   # Chronological decision log & Structural Incapability spec
├── AI-USAGE.md                    # Hackathon compliance AI disclosure log
├── FILE_DOCUMENTATION.txt         # Standalone file inventory and responsibility map
├── .gitignore                     # Git configuration ignoring Python cache files
├── data/
│   ├── authority-policy.json      # Declarative JSON schema for Policy ACA-2026/1
│   ├── authority-policy.md        # Raw text policy document for human reference
│   └── referral-queue.json        # 12 overnight intake referrals
├── services/
│   ├── history_service.py         # Mock Resident History REST API server (port 8083)
│   └── _history_data.json         # Mock resident database storage
└── src/
    ├── client.py                  # Read-only HTTP transport client (urllib)
    ├── guardrail.py               # PolicyGuardrailEngine pre-execution interceptor
    └── main.py                    # CLI intake loop orchestrator with trace logging
```