# Product Requirements Document — RAG Telecom Customer Care Chatbot

**Date:** 2026-06-19
**Author:** Dhaval Patel
**Version:** 1.1 — Added Plans & Pricing Knowledge Source

---

## Changelog

| Version | Date | Summary |
|---|---|---|
| 1.0 | 2026-06-10 | Initial release — FAQ, tickets, guides sources |
| 1.1 | 2026-06-19 | Added `plans` knowledge source (`data/plans.json`) to support plan and pricing queries |

---

## 1. Overview

A Retrieval-Augmented Generation (RAG) chatbot that resolves common telecom customer-support queries without live agent involvement. The bot answers questions about mobile connectivity, billing, SIM management, roaming, voice issues, account management, and **plan and pricing details** by grounding every response in curated knowledge — never hallucinating policy or pricing details.

---

## 2. Problem Statement

Telecom support centres handle a high volume of repetitive, resolvable queries (slow data, incorrect billing, SIM errors, roaming setup). These queries:

- Drain agent capacity from complex escalations
- Follow predictable resolution paths that are well documented internally
- Frustrate customers who wait on hold for answers available in an FAQ

There is no self-serve channel that combines FAQ lookup, historical resolution patterns, technical guide content, and **plan/pricing information** into a single, conversational interface.

**v1.1 Addition:** Early user feedback from the NovaCell prototype revealed a clear gap — plan and pricing questions ("What's your cheapest unlimited plan?", "Do you have a family plan?", "How much is roaming for a week in Europe?") returned wrong, vague, or hallucinated answers because the knowledge system contained no plan or pricing data. This version closes that gap by integrating the official plan catalog (`data/plans.json`) as a fourth knowledge source.

---

## 3. Goals

| Goal | Metric |
|---|---|
| Deflect Tier-1 support queries | >70% of sample questions answered without "call 611" escalation |
| Ground responses in verified knowledge | 0 answers generated from LLM-internal knowledge alone |
| Reduce time-to-answer | Under 10 seconds end-to-end (retrieval + generation) |
| Accessible to non-technical users | No login, no setup; works in a browser |
| **Answer plan & pricing questions correctly** | Plan/pricing questions return answers grounded in `data/plans.json`; 0 hallucinated prices or plan names |

---

## 4. Non-Goals

- Live CRM or billing system integration (real-time account data)
- Ticket creation or case management
- Authentication / personalised account lookup
- Languages other than English (v1)
- Mobile native app
- Personal account balance, usage, or billing lookup (the plans source contains public catalog data only, not per-account data)

---

## 5. Users

**Primary:** Telecom subscribers with Tier-1 support questions (connectivity issues, billing confusion, SIM problems, roaming queries, **plan selection and pricing queries**).

**Secondary:** Telecom support operations teams who maintain the knowledge sources (FAQ CSV, ticket database, PDF guides, **plans JSON**) that power the bot.

---

## 6. Functional Requirements

### 6.1 Conversational Interface

| ID | Requirement |
|---|---|
| FR-01 | Users can type a free-text question and receive a contextually grounded answer |
| FR-02 | Users can click a sample question from the sidebar to send it instantly |
| FR-03 | Conversation history is maintained within a session |
| FR-04 | A "Clear conversation" button resets the session |
| FR-05 | Responses stream token-by-token (no full-page wait) |

### 6.2 Knowledge Retrieval

| ID | Requirement |
|---|---|
| FR-06 | The system retrieves from **four** parallel knowledge collections: FAQ entries, resolved support tickets, telecom guide chunks, and **plan catalog entries** |
| FR-07 | Top-3 documents are fetched from each collection (**12 context documents** total per query) |
| FR-08 | Retrieved documents are labelled by source (FAQ / TICKETS / GUIDES / **PLANS**) in the prompt context |
| FR-09 | Embeddings are generated locally using `all-MiniLM-L6-v2` (no external embedding API cost) |

### 6.3 Answer Generation

| ID | Requirement |
|---|---|
| FR-10 | The LLM must use **only** retrieved context to answer — no internal knowledge fallback |
| FR-11 | When context is insufficient, the bot explicitly says so and directs the user to call 611 or use the MyTelecom app |
| FR-12 | LLM temperature is 0 (deterministic, factual output) |
| FR-13 | Model: `qwen/qwen3-32b` served via Groq API |

### 6.4 Knowledge Ingestion

| ID | Requirement |
|---|---|
| FR-14 | FAQ entries are loaded from `data/faq.csv` (1 row = 1 vector document) |
| FR-15 | Resolved tickets are loaded from `data/tickets.db` (SQLite; 1 ticket = 1 vector document) |
| FR-16 | PDF guide is chunked at 600 characters with 100-character overlap before embedding |
| FR-17 | All collections persist to `chroma_store/` on disk; ingest scripts are idempotent re-runs |
| **FR-20** | **Plan catalog entries are loaded from `data/plans.json` (1 plan object = 1 vector document); ingested via `ingest_plans.py`** |
| **FR-21** | **Each plan document is serialised to a human-readable text representation (name, price, features, eligibility, notes) before embedding, so semantic search matches natural-language pricing queries** |

### 6.5 CLI Interface

| ID | Requirement |
|---|---|
| FR-18 | A CLI mode (`main.py`) provides an interactive REPL for non-browser use |
| FR-19 | Typing `quit` exits the CLI session |

---

## 7. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | **Latency**: End-to-end response (first token) under 3 seconds on a standard laptop with internet access |
| NFR-02 | **Offline embeddings**: The embedding model runs locally; no embedding calls to external APIs |
| NFR-03 | **No credentials in code**: API keys are loaded from `.env`; `.env.example` ships without secrets |
| NFR-04 | **Portability**: Runs on Python 3.11+ with `uv sync` or `pip install -e .`; no OS-specific dependencies |
| NFR-05 | **Restartability**: Chroma store persists to disk; the app does not re-ingest on each start |
| NFR-06 | **Extensibility**: New knowledge sources can be added by writing a new `ingest_*.py` and registering the collection in `retriever.py` |

---

## 8. Data Sources

| Collection | Source | Format | Documents |
|---|---|---|---|
| `faq` | `data/faq.csv` | CSV (question, answer pairs) | 1 per row |
| `tickets` | `data/tickets.db` | SQLite (`tickets` table) | 1 per resolved ticket |
| `guides` | `data/telecom_guide.pdf` | PDF, chunked | 600-char chunks, 100-char overlap |
| **`plans`** | **`data/plans.json`** | **JSON array of plan objects** | **1 per plan** |

### Ticket Categories Covered

`connectivity`, `data`, `roaming`, `sim`, `billing`, `voice`, `device`, `account`

### Plan Categories Covered (v1.1)

`prepaid`, `postpaid`, `family`, `international_roaming`, `add-ons`, `student`, `senior`

### Sample Topics

- Mobile internet loss, slow 4G, intermittent signal drops, network outages
- Unexpected roaming charges, no service abroad
- SIM not recognised, eSIM activation failure, number porting delays
- Double billing, plan auto-renewal at wrong price, itemised bill download failure
- Call barring, echo on calls, VoLTE incompatibility
- App login failures, unauthorised plan changes
- **Plan comparison and selection, pricing tiers, eligibility requirements**
- **Roaming day/monthly pass options and cost comparisons**
- **Family plan pricing, extra line costs, promotional offers**
- **Student and senior discount plans**
- **International calling add-ons vs. roaming passes**

---

## 9. System Architecture

```
User question
     │
     ▼
Merged Retriever  (parallel invoke)
  ├── ChromaDB · faq        top-3 FAQ entries
  ├── ChromaDB · tickets    top-3 resolved ticket resolutions
  ├── ChromaDB · guides     top-3 PDF guide chunks
  └── ChromaDB · plans      top-3 plan catalog entries        ← NEW (v1.1)
     │
     ▼  (12 context documents, source-labelled)
ChatPromptTemplate
  ├── system: telecom assistant persona + context injection
  └── human: user question
     │
     ▼
Qwen3-32B on Groq  (temperature=0, reasoning_format=parsed)
     │
     ▼
StrOutputParser → streamed response to UI
```

**Embedding model:** `sentence-transformers/all-MiniLM-L6-v2` (local, HuggingFace)
**Vector store:** ChromaDB (persisted to `chroma_store/`)
**LLM:** `qwen/qwen3-32b` via Groq API
**Framework:** LangChain (LCEL chain)
**UI:** Streamlit

### New Ingestion Script (v1.1)

`ingest_plans.py` — loads `data/plans.json`, serialises each plan object into a descriptive text document (name, monthly price, features list, eligibility, promotional notes), embeds with `all-MiniLM-L6-v2`, and persists to the `plans` ChromaDB collection. Idempotent: safe to re-run when the JSON catalog is updated.

---

## 10. User Stories

| ID | As a... | I want to... | So that... |
|---|---|---|---|
| US-01 | Customer | Ask why my internet is slow and get step-by-step guidance | I can fix the issue without calling support |
| US-02 | Customer | Ask about unexpected charges on my bill | I understand what I was billed for |
| US-03 | Customer | Ask how to activate roaming before a trip | I don't get stranded without service abroad |
| US-04 | Customer | Click a sample question | I can explore the bot's capabilities without typing |
| US-05 | Customer | Clear the conversation | I can start a new query without prior context influencing answers |
| US-06 | Support operator | Update `faq.csv` and re-run `ingest_faq.py` | The bot reflects the latest policies without redeployment |
| US-07 | Support operator | Seed new tickets into `tickets.db` | Real resolved cases improve retrieval quality over time |
| **US-08** | **Customer** | **Ask what plans are available and their prices** | **I can make an informed decision without calling support** |
| **US-09** | **Customer** | **Ask whether there is a student or family discount** | **I know if I qualify for a cheaper plan** |
| **US-10** | **Customer** | **Ask about roaming pass options and costs before travelling** | **I can choose the right add-on for my trip duration** |
| **US-11** | **Customer** | **Ask about international calling add-ons** | **I understand the difference between calling from home and roaming abroad** |
| **US-12** | **Support operator** | **Update `data/plans.json` and re-run `ingest_plans.py`** | **The bot reflects the latest plan catalog without redeployment** |

---

## 11. Out-of-Scope (Future Iterations)

- **Account authentication** — personalised answers (e.g., "your current balance is…")
- **Live CRM integration** — real-time plan, usage, and billing data
- **Ticket creation** — escalating unresolved queries to a human agent queue
- **Multi-turn memory** — conversation history influencing retrieval (RAG with chat history)
- **Multilingual support** — non-English queries
- **Feedback / thumbs rating** — quality signal for retrieval tuning
- **Re-ranking** — cross-encoder re-ranking of retrieved documents before generation
- **Hybrid search** — combining dense vector search with BM25 keyword search
- **Evaluation harness** — automated RAGAS or similar metrics for retrieval/generation quality

---

## 12. Dependencies & Constraints

| Item | Detail |
|---|---|
| Groq API key | Required; free tier available at console.groq.com |
| HuggingFace embedding model | Auto-downloaded on first run; ~90 MB |
| Python 3.11+ | Minimum runtime version |
| `uv` or `pip` | Package management |
| Disk space | ChromaDB store grows with ingested data |
| Network | Groq API calls require internet access; embeddings are local |
| **`data/plans.json`** | **Official plan catalog JSON; maintained by support operations; must be re-ingested via `ingest_plans.py` after any update** |

---

## 13. Acceptance Criteria (v1.1)

The following test cases must pass before the v1.1 release is considered complete:

### Plan/Pricing Questions (new — must work after change)

| Question | Expected Answer |
|---|---|
| "What's your cheapest unlimited plan?" | Prepaid Unlimited at $45/month. A strong answer may also note Student Unlimited ($30) and the 55+ Plan as cheaper options subject to eligibility. |
| "Do you have a family plan?" | Family Unlimited — 4 lines for $140/month (~$35/line), unlimited 5G, with a 20% intro offer for the first 3 months. Extra lines $30/month. |
| "I'm going to Europe for about a week. What are my roaming options?" | International Day Pass ($10/day) or International Monthly Pass ($50/month, 15 GB). For ~7 days the Monthly Pass is better value ($50 vs ~$70). |
| "Is there a discount for students?" | Student Unlimited at $30/month, unlimited 5G; requires valid enrollment at an accredited college/university, reverified annually. |
| "What's the difference between the International Calling Pack and a roaming pass?" | International Calling Pack ($15/month) discounts calls made FROM the US to other countries; it does not cover usage while physically abroad — that requires a Day Pass or Monthly Pass. |

### Regression — Original Sources (must still work)

| Question | Expected Answer |
|---|---|
| "My mobile data is really slow. How do I fix it?" | Troubleshooting guidance from FAQ/tickets/guide (toggle airplane mode, check data limits, reset network settings). |

### Out-of-Scope Refusal (must be safely declined)

| Question | Expected Response |
|---|---|
| "What is my current bill / balance?" | A safe response directing the user to their account portal or the MyTelecom app — the bot holds public plan data only, not personal account data. |
| "I am visiting London for 3 days in May, build me a trip plan." | A safe "I can't help with that here" response — outside telecom support scope. |
