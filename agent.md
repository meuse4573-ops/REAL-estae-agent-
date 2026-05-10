# AGENT CONTEXT FILE
# Real Estate AI Deal-Execution Agent (Hermes-Based)
# Target State: Florida (Initial Launch Market)

## PROJECT IDENTITY

You are building a *"super-intelligent, hyper-specialized AI Deal-Execution Agent"* for real estate professionals. This is NOT a generic AI assistant. This is a domain-restricted, self-learning autonomous agent that acts as a "Silent Guardian" and "Crystal Ball" for real estate transactions.
You are NOT building from scratch. You are taking the open-source Hermes Agent codebase

*Project Codename*: GuardianAI (internal) / "Your Deal Co-Pilot" (customer-facing)
*Foundation*: Open-source Hermes Agent (nousresearch/hermes-agent) — heavily modified, restricted, and hyper-specialized
*Target User*: High-volume real estate agents and Transaction Coordinators (TCs) in Florida
*Core Promise*: "The more you use it, the smarter it gets. It grows WITH you."

---

## CORE DIRECTIVE (NON-NEGOTIABLE)

The agent MUST operate EXCLUSIVELY within real estate deal execution. It must:
- STRICTLY REFUSE general knowledge queries, creative writing, coding help, math problems, or non-real-estate tasks
- Politely decline out-of-scope requests with: "I'm your Real Estate Deal Co-Pilot, specialized in transaction management. I can't help with [request], but I'm here to protect your deals, predict problems, and keep your transactions on track."
- NEVER hallucinate legal advice — always cite specific Florida statutes/contract clauses when making compliance recommendations
- ALWAYS maintain human-in-the-loop for any external action (sending emails, texts, updating CRMs)

---

## THE 27 CORE CAPABILITIES (MASTER LIST)

### I. DOCUMENT INTELLIGENCE & EXTRACTION
1. *PDF Data Extraction*: Read PDFs and extract deal data automatically, validating against external APIs (ATTOM, public records)
2. *Messy Scan OCR*: Read scanned documents even when messy/low quality using enterprise OCR + image enhancement
3. *Handwritten Document Reading*: Read handwritten documents with human-in-the-loop for low-confidence extractions
4. *Key Date Extraction*: Extract and calculate inspection, financing, closing, and contingency deadlines based on contract logic
5. *Party Extraction*: Extract buyers, sellers, lenders, title companies, co-agents and cross-reference with public records

### II. COMMUNICATION & SENTIMENT INTELLIGENCE
6. *Email Thread Comprehension*: Read email threads and understand deal status, intent, unresolved issues, and commitments
7. *SMS Extraction*: Read text messages and pull out important updates
8. *Tone & Urgency Detection*: Detect tone and urgency to know when someone is slowing down (Predictive Friction)
9. *Silent Party Flagging*: Flag silent parties when someone has stopped replying based on historical baselines
10. *Zero-Dashboard Experience*: Work invisibly in the background inside Gmail, Outlook, and CRMs — no new interface to learn

### III. PREDICTIVE RISK & SCORING
11. *Deal Risk Identification*: Identify deal risks BEFORE they become closing problems using causal chain prediction
12. *Deal Health Score*: Score deal health with a simple, explainable "Deal Safety Score" (0-100)
13. *Deal Prioritization*: Prioritize deals by urgency so the agent focuses on the most dangerous ones first

### IV. HUMAN-IN-THE-LOOP ACTION EXECUTION
14. *Missing Document Detection*: Detect missing, incorrect, or incomplete documents against Florida state checklists
15. *Missing Signature Detection*: Detect missing signatures and remind the right person via their preferred channel
16. *Follow-up Email Drafting*: Draft highly personalized follow-up emails tailored to recipient and deal context
17. *Strategic Reminder Drafting*: Draft polite, strategically timed reminders considering recipient patterns
18. *Approval-Gated Sending*: Send messages ONLY after human approval (one-click approval)
19. *Auto Task Creation*: Create prioritized tasks automatically from deal activity
20. *Intelligent CRM Updates*: Update CRM records with insights, not just raw data
21. *Morning Brief Generation*: Generate a prioritized morning brief with recommended proactive actions
22. *Expert Q&A*: Answer complex questions like "What is missing?" or "What is next?" as an expert consultant

### V. DEAL MANAGEMENT & TRACKING
23. *Deal Summarization*: Summarize the deal in simple language instantly
24. *Portfolio Tracking*: Track all open deals at once in a prioritized view

### VI. AUDIT, COMPLIANCE & CONTINUOUS LEARNING
25. *Immutable Audit Trail*: Keep a full audit trail for E&O (Errors & Omissions) compliance
26. *Florida Deep Specialization*: Support Florida first for deep local contract language understanding ( FAR/BAR contracts)
27. *Continuous Self-Learning*: Learn continuously from approved edits — the agent GROWS as you use it more

---

## ADVANCED AI ARCHITECTURES (TECHNICAL FOUNDATION)

### 1. AGENTIC RAG (Retrieval-Augmented Generation)
- NOT simple keyword search
- Performs multi-hop reasoning across contracts, emails, and external data
- Dynamically formulates sub-queries, retrieves from diverse sources, synthesizes, iteratively refines
- Example: "Is this deal at risk?" → retrieves contract terms + lender emails + interest rate trends + title report → holistic assessment

### 2. PREDICTIVE FRICTION MODELING
- Analyzes communication velocity and sentiment decay per contact
- Learns baselines: "Lender John usually replies in 2 hours"
- Detects anomalies: "John hasn't replied in 24 hours + sentiment shifted negative → flag delay risk"
- Forecasts problems days/weeks before deadlines

### 3. MULTI-AGENT ORCHESTRATION ("The Expert Panel")
Complex tasks are decomposed and delegated to specialized sub-agents:

| Sub-Agent | Role | Tools |
|-----------|------|-------|
| *AUDITOR* | Compliance, signatures, checklists | Document analysis, Florida checklist DB, signature detection |
| *COMMUNICATOR* | External interactions, drafting, sentiment | Email/SMS drafting, tone analysis, channel selection |
| *ANALYST* | Data interpretation, market insights | ATTOM API, Mashvisor, financial modeling, comparables |
| *STRATEGIST* | Orchestration, deal flow monitoring, risk interpretation | Deal Safety Score engine, prioritization matrix, task delegation |
| *WATCHMAN* | Deadlines, external monitoring, anomaly detection | Calendar logic, API monitoring, silent party detection |

All sub-agents collaborate via Hermes's delegate_task capability.

### 4. CONTINUOUS LEARNING (RLHF — Reinforcement Learning from Human Feedback)
- EVERY human interaction is a training signal
- Agent approves draft email → positive reinforcement for that tone/style
- Agent corrects extracted data → fine-tune NER model
- Agent overrides risk flag → adjust friction model weights
- Result: The agent gets MORE ACCURATE and MORE PERSONALIZED the longer each agent uses it
- *TAGLINE*: "This agent doesn't just work for you — it grows WITH you."

---

## HERMES AGENT MODIFICATION STRATEGY

You are NOT building from scratch. You are taking the open-source Hermes Agent codebase and performing these modifications:

### Components to Modify/Extend:

1. *SOUL.md* → Rewrite with real estate transaction coordinator persona + strict domain boundaries
2. *Skills System* → Dynamic loading of Florida-specific legal knowledge, brokerage best practices, custom workflows
3. *Persistent Memory* →
   - Granular deal histories
   - Agent-specific preferences (tone, style, workflow)
   - Communication patterns per contact
   - Migrate SQLite → PostgreSQL with strict tenant_id isolation
4. *Tool System* → Custom real estate tools:
   - extract_real_estate_data (OCR/NLP models)
   - analyze_deal_sentiment (sentiment analysis)
   - generate_compliance_report (Florida checklist validation)
   - draft_communication (personalized email/SMS)
   - calculate_deal_health_score (risk scoring)
   - cross_reference_public_records (ATTOM API)
5. *Gateway* → Background integration with:
   - Gmail API, Microsoft Graph API (Outlook)
   - CRMs: Follow Up Boss, kvCORE, LionDesk
   - Webhooks for real-time events
6. *Scheduled Tasks (Cron)* → Morning briefs, deal health checks, proactive reminders
7. *Subagent Delegation* → Multi-agent orchestration framework using delegate_task
8. *Learning Loop* → RLHF implementation capturing every approval/correction/override

---

## FLORIDA-SPECIFIC REQUIREMENTS

### Legal Framework:
- FAR/BAR (Florida Association of Realtors / Florida Bar) contract templates
- Florida Real Estate Commission (FREC) regulations
- Chapter 475, Florida Statutes (Real Estate Brokerage)
- Florida-specific disclosure requirements (Seller's Property Disclosure, Lead-Based Paint, etc.)
- Florida Homestead exemption rules
- Florida title and escrow procedures

### Market Context:
- 216,180+ Realtors (largest state population)
- High transaction velocity (73.59 homes sold per 100k people)
- High agent density (9.54 per 1,000 people)
- Significant investor activity (build-to-rent, single-family rentals)
- Hurricane/disclosure considerations (flood zones, wind mitigation)

---

## COMPETITIVE MOAT

| Feature | Dotloop / SkySlope / TCdocs | YOUR AGENT |
|---------|---------------------------|------------|
| *Paradigm* | Reactive digital filing cabinet | Proactive AI co-pilot |
| *Alerts* | "Deadline passed" | "Deadline WILL pass if X doesn't happen by Y" |
| *Communication* | Generic templates | Hyper-personalized, context-aware, sentiment-informed |
| *Interface* | Separate dashboard to learn | Zero-Dashboard — lives inside Gmail/Outlook/CRM |
| *Learning* | Static — same on day 1 and day 1000 | Self-learning — grows with every interaction |
| *Risk Detection* | Surface-level checklist | Deep causal prediction + behavioral anomaly detection |
| *Compliance* | Basic document storage | Immutable audit trail + predictive E&O protection |

---

## SELF-LEARNING MANIFESTO (CRITICAL)

This agent has a core philosophical difference from every other real estate tool on the market:

> *"The agent grows as you use it. It learns YOUR style. It learns YOUR market. It learns YOUR contacts' behaviors. It becomes more valuable every single day."*

### How Self-Learning Works:
1. *Preference Learning*: Remembers how each agent likes emails drafted (formal vs. casual, short vs. detailed)
2. *Contact Baselines*: Builds response time and sentiment baselines for every lender, buyer, seller, co-agent
3. *Correction Memory*: Every corrected extraction or overridden flag improves future accuracy
4. *Market Adaptation*: Learns seasonal patterns, local market velocity, typical closing timelines
5. *Brokerage Customization*: Adapts to specific brokerage workflows and compliance requirements

### Self-Learning Data Capture:
- Email draft approvals/edits → Communication style model
- Data extraction corrections → NER/Extraction model
- Risk flag overrides → Friction model weights
- Task completion times → Deadline prediction model
- CRM update confirmations → Data mapping accuracy

---

## TECHNICAL STACK (REFERENCE)

| Layer | Technology |
|-------|-----------|
| *Base Framework* | Hermes Agent (modified) |
| *Database* | PostgreSQL (multi-tenant) |
| *Message Broker* | Redis / RabbitMQ |
| *Worker Queues* | Celery |
| *Vector DB* | Chroma / Weaviate / Qdrant |
| *OCR* | Google Cloud Vision / Amazon Textract / LayoutLMv3 |
| *HTR* | TrOCR (handwriting) |
| *LLM* | GPT-4 / Gemini (API) + fine-tuned open models |
| *XAI* | SHAP / LIME (explainable AI for Deal Safety Score) |
| *External APIs* | ATTOM, Mashvisor, Gmail API, Microsoft Graph, CRM APIs |
| *Deployment* | Docker, load-balanced stateless workers |

---

## CURRENT BUILD PHASE

*Phase*: Foundation Setup (Hermes cloned, initial modification)
*Next Milestones*:
1. Modify SOUL.md with real estate persona
2. Implement strict domain restriction middleware
3. Set up PostgreSQL multi-tenant schema
4. Create first custom tool: extract_real_estate_data
5. Implement Florida-specific skill loader
6. Build basic Auditor sub-agent for document checklist validation

---

## USER CONTEXT

- *Builder*: Solo developer
- *IDE*: OpenCode (AI-powered code editor)
- *Approach*: Open-source-first, cost-efficient, rapid iteration
- *Goal*: Build MVP for Florida real estate agents, prove product-market fit, then scale

---

## WHEN IN DOUBT

1. *Domain First*: If a feature doesn't directly help close a real estate deal faster or safer, don't build it
2. *Trust Through Transparency*: Every AI decision must be explainable — show your work
3. *Human Sovereignty*: The agent suggests, the human decides. Always.
4. *Florida Depth*: Better to be perfect in Florida than mediocre in 50 states
5. *Growth Mindset*: Every interaction makes the agent smarter — design for data capture

---

## KEY TAGLINES FOR CUSTOMER MESSAGING

- "Your Silent Guardian. Your Crystal Ball. Your Deal Co-Pilot."
- "It doesn't just manage your deals — it protects them."
- "The more you use it, the smarter it gets."
- "Zero dashboards. Zero new interfaces. Zero learning curve."
- "Predict problems before they become closing nightmares."