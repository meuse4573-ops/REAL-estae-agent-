# MASTER DEVELOPMENT PLAN
# Real Estate AI Deal-Execution Agent (Hermes-Based)
# Project: GuardianAI - Your Deal Co-Pilot

=============================================================================
# PROJECT OVERVIEW

**Project Name**: GuardianAI (internal) / "Your Deal Co-Pilot" (customer-facing)
**Foundation**: Open-source Hermes Agent (nousresearch/hermes-agent)
**Target**: Florida real estate agents & Transaction Coordinators
**Core Promise**: "The more you use it, the smarter it gets. It grows WITH you."

=============================================================================
# TECHNICAL STACK

| Layer | Technology |
|-------|-----------|
| Base Framework | Hermes Agent (modified) |
| Database | PostgreSQL (multi-tenant) |
| Vector DB | Chroma / Weaviate / Qdrant |
| Message Broker | Redis / RabbitMQ |
| Worker Queues | Celery |
| OCR | LayoutLMv3 / Donut + Google Cloud Vision fallback |
| HTR | TrOCR (handwriting) |
| LLM | GPT-4 / Gemini (API) + fine-tuned open models |
| XAI | SHAP / LIME |
| External APIs | ATTOM, Mashvisor, Gmail API, Microsoft Graph, CRM APIs |
| Deployment | Docker, load-balanced stateless workers |

=============================================================================
# PROJECT STRUCTURE

```
guardian-ai/
├── hermes-core/              # (existing Hermes code, untouched base)
├── guardian_ai/              # (ALL modifications go here)
│   ├── soul/
│   │   └── SOUL.md           # Real estate persona (DONE)
│   ├── core/
│   │   ├── domain_guard.py   # Domain restriction middleware
│   │   ├── tenant_guard.py   # Multi-tenant isolation
│   │   ├── friction_model.py # Predictive friction modeling
│   │   ├── prioritizer.py    # Deal prioritization matrix
│   │   ├── orchestrator.py   # Multi-agent delegation
│   │   ├── approval_system.py # Human-in-the-loop approvals
│   │   ├── audit_logger.py   # Immutable audit trail
│   │   ├── morning_brief.py  # Daily briefing
│   │   ├── health_checker.py # Periodic deal health checks
│   │   └── reminder_engine.py # Proactive reminders
│   ├── skills/
│   │   └── florida_re/       # Florida real estate skills
│   │       ├── SKILL.md
│   │       ├── far_bar_contracts.md
│   │       ├── disclosures.md
│   │       └── frec_regulations.md
│   ├── tools/
│   │   ├── document_tools.py    # PDF/OCR extraction
│   │   ├── communication_tools.py # Email/SMS parsing
│   │   ├── risk_tools.py         # Deal safety scoring
│   │   ├── compliance_tools.py   # Florida checklist
│   │   ├── action_tools.py       # Tasks, CRM updates
│   │   ├── signature_tools.py    # DocuSign/dotloop integration
│   │   ├── wire_fraud_guard.py   # Wire fraud detection
│   │   ├── offer_tools.py        # Offer/counter-offer drafting
│   │   ├── cma_tools.py          # Comparable market analysis
│   │   ├── calendar_tools.py     # Google/Outlook calendar
│   │   └── voice_tools.py        # Call logging, transcription
│   ├── ai_framework/           # AI/ML depth layer
│   │   ├── prompts/             # Prompt templates with few-shot
│   │   ├── schemas/             # Output validation JSON schemas
│   │   ├── rag/                 # Hybrid RAG utilities
│   │   └── reasoning/           # Chain-of-thought logging
│   ├── subagents/
│   │   ├── auditor.py        # Compliance, signatures, checklists
│   │   ├── communicator.py   # Drafting, sentiment, channels
│   │   ├── analyst.py        # Data, market insights, ATTOM
│   │   ├── strategist.py     # Orchestration, prioritization
│   │   └── watchman.py       # Deadlines, monitoring
│   ├── memory/
│   │   ├── postgres_schema.sql
│   │   ├── memory_manager.py
│   │   └── vector_store.py   # For Agentic RAG
│   ├── gateway/
│   │   ├── email_gateway.py  # Gmail, Outlook
│   │   ├── crm_gateway.py    # Follow Up Boss, kvCORE, LionDesk
│   │   └── browser_extension/ # Zero-Dashboard experience
│   ├── learning/
│   │   ├── rlhf_loop.py     # Training signal capture
│   │   ├── fine_tuner.py    # Model fine-tuning pipeline
│   │   └── preference_learner.py # Per-agent preferences
│   └── config/
│       └── florida_config.yaml
├── tests/
│   ├── unit/
│   ├── integration/
│   └── florida_specific/
├── docs/
└── requirements.txt
```

=============================================================================
# PHASE 0: ENVIRONMENT SETUP

Step 0.1: GitHub Connection
- ✅ GitHub connected to: https://github.com/meuse4573-ops/REAL-estae-agent-.git
- ✅ SOUL.md pushed to repo
- Future: Regular commits as we build

Step 0.2: Project Structure Creation
- Create guardian_ai/ folder structure
- Move SOUL.md to guardian_ai/soul/

================================================================================
# PHASE 0.5: SECURITY LAYER (Week 1)

Step 0.5.1: Authentication & Token Management
File: `guardian_ai/core/security.py`
- JWT authentication with 15-min access tokens + 7-day refresh tokens
- Token rotation on each request
- Revocation list for compromised tokens

Step 0.5.2: API Key Vault
- HashiCorp Vault or AWS Secrets Manager pattern
- All API keys (ATTOM, CRM, email) stored in vault, never in code
- Automatic key rotation schedule

Step 0.5.3: Data Encryption
- Row-level AES-256 encryption for PII columns: buyer_name, seller_name, SSN, financial_data
- Encryption at rest (PostgreSQL TDE) and in transit (TLS 1.3)
- Key management via KMS (AWS KMS or HashiCorp Vault Transit)

## Error Handling: Circuit Breaker for External APIs
- If ATTOM fails 3 times, switch to cached data + alert
- Fallback LLM: primary GPT-4, fallback Gemini, emergency local Llama-3
- Graceful degradation: if OCR confidence < 50%, immediately flag for human review instead of retrying
- Dead letter queue: failed tasks go to DLQ for manual inspection after 3 retries
- Exponential backoff: 1s, 2s, 4s, 8s, 16s between retries

Step 0.5.4: SQL Injection Prevention
- ALL queries use parameterized statements only
- ORM layer (SQLAlchemy) with enforced parameterization
- Regular security audits with SQLMap

Step 0.5.5: XSS Prevention
- Sanitize all AI-generated outputs before displaying
- Content Security Policy (CSP) headers on all responses
- HTML encoding for all user-facing text

Step 0.5.6: Rate Limiting
- 100 requests/min per tenant
- 1000 requests/day per IP
- Burst allowance: 20 requests in 1-second window, then throttle

Step 0.5.7: Wire Fraud Detection
- Flag if wire instructions change mid-transaction
- Require phone callback verification for any wire instruction modification
- Dual-approval for wiring above $100K
- Audit trail for all wire-related communications

Step 0.5.8: Backup & Recovery
- Daily encrypted PostgreSQL dumps to S3
- 7-day retention for daily backups
- Monthly archives retained for 1 year
- Point-in-time recovery (PITR) enabled
- Disaster recovery plan with < 4 hour RTO

================================================================================
# PHASE 1: FOUNDATION & IDENTITY (Week 1)

Step 1.1: SOUL.md — Agent Persona
Status: ✅ DONE
- Real estate-only domain restriction
- Refusal template for non-real-estate requests
- Florida-specific focus (FAR/BAR, FREC, Chapter 475)
- Self-learning emphasis
- Human-in-the-loop mandate
- Proactive, not reactive personality

Step 1.2: Domain Restriction Middleware
File: `guardian_ai/core/domain_guard.py`
Purpose: Hard-coded filter that runs BEFORE any LLM call

Logic:
```
IF user_request.contains(real_estate_keywords) → ALLOW
ELIF user_request.is_general_knowledge → REFUSE with template
ELIF user_request.is_coding/math/creative → REFUSE with template
ELSE → ASK CLARIFICATION: "How does this relate to your real estate transaction?"
```

Real estate keywords:
contract, deal, closing, inspection, lender, buyer, seller, title, escrow,
contingency, addendum, FAR/BAR, MLS, appraisal, earnest money, disclosure,
E&O, broker, agent, TC, transaction coordinator, earnest deposit, purchase
agreement, title insurance, deed, mortgage, pre-approval, loan commitment,
homestead, property tax, closing costs, escrow officer, title company,
listing agreement, buyer's agent, seller's agent, dual agent, commission,
representation, disclosure, contingencies, financing contingency,
inspection contingency, appraisal contingency, sale of buyer's property

Step 1.3: Configuration System
File: `guardian_ai/config/florida_config.yaml`
Contents:
- Florida counties and their specific requirements
- FAR/BAR contract version mappings
- FREC regulation references
- Common Florida disclosure forms list
- Default deal timeline templates
  - Inspection: 15 days (Florida standard)
  - Financing: 30-45 days
  - Closing: 45-60 days (financed), 30-45 days (cash)
- Hurricane/flood zone disclosure triggers
- Wind mitigation form requirements

=============================================================================
# PHASE 2: MEMORY & DATA LAYER (Week 1-2)

Step 2.1: PostgreSQL Schema Design
File: `guardian_ai/memory/postgres_schema.sql`

```sql
-- Tenants (brokerages or individual agents)
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    settings JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Deals
CREATE TABLE deals (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    address TEXT NOT NULL,
    buyer_name TEXT,
    seller_name TEXT,
    status VARCHAR(50), -- pending, active, under_contract, closing, closed, cancelled
    deal_safety_score DECIMAL(5,2),
    contract_date DATE,
    closing_date DATE,
    listing_number VARCHAR(50),
    mls_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    deal_id UUID REFERENCES deals(id),
    type VARCHAR(50), -- contract, addendum, disclosure, inspection, appraisal, title, other
    name VARCHAR(255),
    file_path TEXT,
    extracted_data JSONB,
    ocr_confidence DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Communications
CREATE TABLE communications (
    id UUID PRIMARY KEY,
    deal_id UUID REFERENCES deals(id),
    channel VARCHAR(20), -- email, sms, phone, webhook
    sender VARCHAR(255),
    recipient VARCHAR(255),
    subject TEXT,
    content TEXT,
    sentiment_score DECIMAL(5,2),
    urgency_flag BOOLEAN DEFAULT FALSE,
    is_deal_related BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Contacts
CREATE TABLE contacts (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    name VARCHAR(255),
    role VARCHAR(50), -- buyer, seller, lender, title, inspector, appraiser, co_agent
    email VARCHAR(255),
    phone VARCHAR(50),
    company VARCHAR(255),
    avg_response_time_minutes INTEGER,
    sentiment_baseline DECIMAL(5,2),
    communication_style JSONB, -- {tone: "formal", length: "short"}
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tasks
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    deal_id UUID REFERENCES deals(id),
    description TEXT NOT NULL,
    priority INTEGER, -- 1-5, 1 highest
    deadline TIMESTAMP,
    status VARCHAR(20), -- pending, in_progress, completed, blocked
    created_by_ai BOOLEAN DEFAULT TRUE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Audit Trail (immutable)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    deal_id UUID REFERENCES deals(id),
    tenant_id UUID REFERENCES tenants(id),
    action_type VARCHAR(50), -- ai_suggestion, human_decision, document_seen, etc.
    ai_output TEXT,
    human_decision VARCHAR(20), -- approved, edited, rejected, ignored
    human_correction TEXT,
    full_context JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Agent Preferences (self-learning)
CREATE TABLE agent_preferences (
    tenant_id UUID REFERENCES tenants(id),
    preference_key VARCHAR(100),
    preference_value TEXT,
    confidence_score DECIMAL(5,2),
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (tenant_id, preference_key)
);

-- RLHF Training Data
CREATE TABLE rlhf_data (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    input_context TEXT,
    ai_output TEXT,
    human_correction TEXT,
    correction_type VARCHAR(50), -- email_style, extraction, risk_flag, deadline_prediction
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Communication Baselines (for friction model)
CREATE TABLE communication_baselines (
    contact_id UUID REFERENCES contacts(id),
    role VARCHAR(50),
    avg_response_minutes DECIMAL(10,2),
    response_variance DECIMAL(10,2),
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Deal Risk History
CREATE TABLE deal_risks (
    id UUID PRIMARY KEY,
    deal_id UUID REFERENCES deals(id),
    risk_type VARCHAR(50), -- financing, inspection, title, communication, deadline
    severity INTEGER, -- 1-5
    description TEXT,
    detected_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    resolution TEXT
);

-- Indexes for performance
CREATE INDEX idx_deals_tenant ON deals(tenant_id);
CREATE INDEX idx_deals_status ON deals(status);
CREATE INDEX idx_documents_deal ON documents(deal_id);
CREATE INDEX idx_communications_deal ON communications(deal_id);
CREATE INDEX idx_contacts_tenant ON contacts(tenant_id);
CREATE INDEX idx_tasks_deadline ON tasks(deadline) WHERE status = 'pending';
CREATE INDEX idx_audit_deal ON audit_logs(deal_id);
CREATE INDEX idx_audit_tenant ON audit_logs(tenant_id);
```

Step 2.2: Multi-Tenant Data Isolation
File: `guardian_ai/core/tenant_guard.py`
Rule: EVERY database query MUST include `tenant_id` filter
Enforcement: Middleware that injects tenant_id from authenticated session
Pattern:
```python
def get_deals(tenant_id: str) -> List[Deal]:
    query = db.query(Deal).filter(Deal.tenant_id == tenant_id)
    return query.all()
```

Step 2.3: Memory Manager
File: `guardian_ai/memory/memory_manager.py`
Methods:
- store_deal_context(deal_id, context)
- get_deal_history(deal_id)
- store_contact_baseline(contact_id, metrics)
- get_agent_preferences(tenant_id)
- log_rlhf_signal(tenant_id, correction)
- get_deal_documents(deal_id)
- get_deal_communications(deal_id, days_back=30)

Step 2.4: Vector Store (for Agentic RAG)
File: `guardian_ai/memory/vector_store.py`
- Store document embeddings
- Store email thread embeddings
- Store historical deal patterns
- Support semantic search for deal Q&A

Step 2.5: Zero-Dashboard Browser Extension (EARLY BUILD)
File: `guardian_ai/gateway/browser_extension/`
Purpose: Build the Zero-Dashboard experience EARLY — functional with basic features by Week 3.
- Gmail/Outlook sidebar showing deal context
- Basic risk alerts (simple threshold-based)
- Email reading and classification
- Deal pipeline sidebar
- WHY: Agents need to see the AI working inside their existing tools from Day 1. Advanced features (inline drafting, one-click approvals, Deal Safety Score indicators) added in Phase 8.

Step 2.5a: Scalability Infrastructure
- PostgreSQL read replicas for query-heavy ops (deal listing, search)
- PgBouncer connection pooling (max 100 connections per replica)
- Redis caching layer: cache deal scores for 1 hour, contact baselines for 24 hours
- Database partitioning: partition audit_logs and rlhf_data by month
- Celery task routing: high priority queue for urgent deal checks, low for daily syncs

**Error Handling & Resilience (Applies to Phase 2):**
- Circuit breaker: If database read replica fails, fallback to primary
- Connection pool exhaustion handling: queue requests, alert if PgBouncer max reached
- Redis cache miss fallback: query database directly if cache unavailable
- Dead letter queue for failed sync tasks
- Exponential backoff: 1s, 2s, 4s, 8s, 16s between retries

================================================================================
# PHASE 3: DOCUMENT INTELLIGENCE (Week 2-3)

Step 3.1: PDF Extraction Tool
File: `guardian_ai/tools/document_tools.py` → `extract_pdf_data()`
Stack:
- LayoutLMv3 or Donut (open-source document understanding)
- Fallback: PyPDF2 + regex for simple PDFs
- Validation: Cross-reference with ATTOM API for property data
Output: Structured JSON with parties, dates, property info, contingencies

Step 3.2: OCR for Scanned Documents
File: `guardian_ai/tools/document_tools.py` → `extract_scan_data()`
Stack:
- OpenCV for image enhancement (denoise, deskew, contrast)
- Tesseract OCR (open-source)
- Confidence scoring per word
- Retry with different preprocessing if confidence < 80%

Step 3.3: Handwriting Recognition
File: `guardian_ai/tools/document_tools.py` → `extract_handwriting()`
Stack:
- TrOCR (open-source handwriting recognition)
- Human-in-the-loop flag for confidence < 70%
- Store human corrections as RLHF training data

Step 3.4: Date Extraction Engine
File: `guardian_ai/tools/document_tools.py` → `extract_key_dates()`
Logic:
- Custom NER for date types:
  - Inspection deadline
  - Financing commitment deadline
  - Closing date
  - Contingency deadlines (appraisal, financing, sale of buyer's property)
- Rule-based calculation for derived dates ("closing = contract_date + 45 days")
- Florida-specific calendar (holidays, business days only)
- Conflict detection: flag if dates don't match between contract and addendum

Step 3.5: Party Extraction & Validation
File: `guardian_ai/tools/document_tools.py` → `extract_parties()`
Logic:
- Advanced NER for names, roles, companies
- Fuzzy matching against known contacts
- Cross-reference with ATTOM API for property ownership records
- Flag if buyer name doesn't match pre-approval letter

Step 3.6: Florida Disclosure Detection
File: `guardian_ai/tools/compliance_tools.py` → `check_florida_disclosures()`
Detect required Florida disclosures:
- Seller's Property Disclosure (AS IS or Traditional)
- Lead-Based Paint Disclosure (pre-1978 homes)
- Florida Homestead Exemption (seller must disclose)
- Coastal Property Disclosure (if property within 1,000 ft of coastline)
- Flood Zone Disclosure (Elevation Certificate requirements)
- Wind Mitigation Form Disclosure (if home built after 2002)
- Property Tax Disclosure
- Asbestos Disclosure (commercial properties)

=============================================================================
# PHASE 4: COMMUNICATION INTELLIGENCE (Week 3-4)

Step 4.1: Email Thread Parser
File: `guardian_ai/tools/communication_tools.py` → `parse_email_thread()`
Stack:
- Gmail API + Microsoft Graph API integration
- Thread-aware parsing (maintain conversation context)
- Fine-tuned LLM for abstractive summarization
Extract:
- Deal status (active, stalled, falling apart)
- Intent (wants to proceed, wants out, needs info)
- Unresolved issues (what's blocking progress)
- Commitments made (promises to deliver)

Step 4.2: SMS Extraction
File: `guardian_ai/tools/communication_tools.py` → `parse_sms()`
Stack:
- SMS gateway integration or CRM texting module
- Short-text NLP model (fine-tuned on real estate SMS patterns)
Extract:
- Updates (appraisal scheduled, inspection done)
- Confirmations (yes, I'll be there)
- Urgent flags (problems, issues, cancellations)

Step 4.3: Sentiment & Urgency Detection
File: `guardian_ai/tools/communication_tools.py` → `analyze_sentiment()`
Stack:
- Multi-label classification model
  - Tone: positive / neutral / negative
  - Urgency: low / medium / high
- Fine-tuned on real estate communication dataset
- Track sentiment trajectory per contact (getting better or worse?)

Step 4.4: Predictive Friction Model
File: `guardian_ai/core/friction_model.py`
Logic:
- Baseline learning: Track avg_response_time per contact
  - Lenders: baseline 2-4 hours
  - Buyers: baseline 4-8 hours
  - Sellers: baseline 8-24 hours
- Anomaly detection: Statistical deviation from baseline
  - Flag when response time > 2x baseline
- Sentiment decay: Track tone changes over time
- Output: Risk flag + recommended action
  - "Call lender directly" / "Request extension" / "Escalate to agent"

Step 4.5: Silent Party Detector
File: `guardian_ai/tools/communication_tools.py` → `detect_silent_parties()`
Logic:
- Dynamic baselines per contact role (lenders slower than buyers)
- Criticality weighting:
  - Title company silence = HIGH (blocks closing)
  - Lender silence = HIGH (financing contingency)
  - Inspector silence = LOW (can reschedule)
- Flag after: 2x baseline response time + deal stage proximity factor

=============================================================================
# PHASE 5: PREDICTIVE RISK & SCORING (Week 4-5)

Step 5.1: Deal Safety Score Engine
File: `guardian_ai/tools/risk_tools.py` → `calculate_deal_health()`
Inputs:
- Document completeness (Auditor sub-agent)
- Communication velocity (Friction model)
- Sentiment trends (Analyst sub-agent)
- Deadline proximity (Watchman sub-agent)
- External market data (interest rates, appraisal trends)

Output:
- 0-100 score
- XAI explanation using SHAP values showing which factors contributed
- Breakdown by category: Documents (25%), Communication (25%), Timeline (25%), Market (25%)

Step 5.2: Causal Risk Prediction
File: `guardian_ai/tools/risk_tools.py` → `predict_deal_risks()`
Logic patterns:
```
IF lender_silent AND financing_deadline < 5_days AND interest_rates_spiked
  → HIGH RISK: financing contingency extension needed

IF inspection_report_received AND major_issues_found AND buyer_sentiment_negative
  → HIGH RISK: deal may fall through

IF title_search_shows_lien AND seller_communication_evasive
  → HIGH RISK: closing delay likely

IF appraisal_coming_in_low AND buyer_cash_short AND seller_not_motivated
  → HIGH RISK: appraisal gap conflict
```

Step 5.3: Deal Prioritization Matrix
File: `guardian_ai/core/prioritizer.py`
Formula:
```
Priority Score = (100 - Deal Safety Score) * 0.4
               + (Days to Close / 30) * 0.3
               + (Financial Impact / Max Impact) * 0.2
               + (Agent Preference Weight) * 0.1
```
Output: Ranked list of deals requiring immediate attention

Step 5.4: Risk Categories (Florida-Specific)
File: `guardian_ai/tools/risk_tools.py`
- Financing Risk: lender delays, rate changes, appraisal gaps
- Inspection Risk: major repairs, repair negotiations, inspection period expiry
- Title Risk: liens, clouds on title, ownership disputes
- Communication Risk: silent parties, sentiment decline
- Timeline Risk: deadline misses, closing delays
- Market Risk: price reductions, competing offers, market conditions

=============================================================================
# PHASE 6: SUB-AGENT ORCHESTRATION (Week 5-6)

Step 6.1: Auditor Sub-Agent
File: `guardian_ai/subagents/auditor.py`
Role: Compliance, signatures, checklists

Tools:
- document_tools: extract and analyze documents
- compliance_tools: validate against Florida checklist

Tasks:
- Cross-reference documents against Florida checklist
  - Contract with all required signatures
  - Disclosure forms completed
  - Addendums signed
  - Lender documents received
- Detect missing signatures using computer vision
- Flag incorrect or incomplete forms
- Verify E&O requirements for brokerage
- Validate FAR/BAR contract compliance

Step 6.2: Communicator Sub-Agent
File: `guardian_ai/subagents/communicator.py`
Role: External interactions, drafting, sentiment

Tools:
- communication_tools: parse and analyze communications

Tasks:
- Draft personalized follow-up emails
  - Based on recipient's communication style
  - Based on deal context and urgency
- Draft strategic reminders
  - Timing based on recipient's baseline
  - Tone adjusted to sentiment
- Analyze recipient communication style
  - Formal vs casual
  - Detailed vs brief
- Route messages through correct channel (email vs SMS vs phone)

Step 6.3: Analyst Sub-Agent
File: `guardian_ai/subagents/analyst.py`
Role: Data interpretation, market insights

Tools:
- risk_tools: deal safety, risk prediction
- External APIs: ATTOM, Mashvisor

Tasks:
- Pull comparable sales data (ATTOM)
  - Recent sales in area
  - Price trends
  - Days on market
- Analyze market trends (Mashvisor)
  - Rental rates
  - Cap rates
  - Investment potential
- Calculate financial scenarios
  - Cash to close
  - Loan impact
  - Closing cost estimates
- Generate appraisal risk assessments

Step 6.4: Strategist Sub-Agent
File: `guardian_ai/subagents/strategist.py`
Role: Orchestration, deal flow monitoring

Tools: All other sub-agents via delegate_task

Tasks:
- Calculate overall Deal Safety Score
  - Synthesize inputs from all sub-agents
  - Weight by deal stage and risk type
- Prioritize deals across portfolio
  - Apply prioritization matrix
  - Factor in agent preferences
- Generate morning briefs
  - Top 3 urgent deals
  - New risks overnight
  - Deadlines today/tomorrow
  - Recommended actions
- Recommend proactive actions
  - What should agent do today?
  - What's about to become a problem?

Step 6.5: Watchman Sub-Agent
File: `guardian_ai/subagents/watchman.py`
Role: Deadlines, external monitoring, anomaly detection

Tools:
- Cron scheduler for periodic checks
- API monitors for external portals

Tasks:
- Monitor deadline proximity
  - Countdown to each critical date
  - Alert at 7 days, 3 days, 1 day, day-of
- Check external portals
  - Lender portal for status updates
  - Title company for commitment
- Detect silent parties
  - Run friction model on all contacts
  - Flag anomalies
- Trigger proactive alerts
  - Send notification before problem occurs

Step 6.6: Delegation Framework
File: `guardian_ai/core/orchestrator.py`

Example delegation flow:
```
strategist receives: "Prepare for closing on 123 Main St"
  → delegates to auditor: "Verify all docs signed for closing"
      → auditor checks: contract, addendums, disclosures, lender docs, title
      → auditor returns: "All signed except seller's final bill statement"
  → delegates to analyst: "Check title commitment status"
      → analyst queries: title company API
      → analyst returns: "Clear to close, awaiting wiring instructions"
  → delegates to communicator: "Draft closing reminder to buyer"
      → communicator drafts: personalized email with closing time, wire instructions reminder
      → communicator returns: draft for approval
  → delegates to watchman: "Confirm wire transfer scheduled"
      → watchman checks: buyer communication for wire confirmation
      → watchman returns: "Wire confirmed for 2pm today"
strategist synthesizes results → presents unified briefing to human
```

=============================================================================
# PHASE 7: HUMAN-IN-THE-LOOP ACTIONS (Week 6-7)

Step 7.1: Draft Approval System
File: `guardian_ai/core/approval_system.py`

Flow:
1. AI drafts email/reminder/task
2. Presents to human with full context:
   - Why: "Lender is 24h overdue"
   - What: "Follow-up email about financing commitment"
   - To whom: "John Smith, Loan Officer"
3. Human clicks: APPROVE / EDIT / REJECT
4. If EDIT: human modifies, AI learns from delta (RLHF)
5. If REJECT: AI asks why, stores reason for future improvement

Step 7.2: One-Click Approval UI
Integration: Browser extension or email client plugin

Display:
- Draft content
- AI reasoning: "Sending because lender is 24h overdue and financing deadline is in 3 days"
- Recipient info
- Approve button (green) + Edit button (yellow) + Reject button (red)

Step 7.3: Auto Task Creation
File: `guardian_ai/tools/action_tools.py` → `create_task()`

Triggers:
- Document received → create "Review document" task
- Deadline approaching → create "Follow up on X" task
- Risk detected → create "Address risk: [description]" task
- Communication received → create "Review message from X" task

Properties:
- Priority auto-set by Deal Safety Score (lower score = higher priority)
- Deadline auto-calculated based on deal timeline
- Assignee based on role (agent handles risks, TC handles documents)

Step 7.4: Intelligent CRM Updates
File: `guardian_ai/gateway/crm_gateway.py`

Logic:
- Push factual updates:
  - Deal status change
  - New documents
  - Closing date
- Push AI insights:
  - "Buyer sentiment improved after inspection resolution"
  - "Lender communication velocity slowed - potential delay"
  - "Deal Safety Score dropped from 85 to 62"
- Push risk flags:
  - "Financing deadline in 3 days - lender unresponsive"
- NEVER overwrite human-entered data without confirmation

Step 7.5: Morning Brief Generation
File: `guardian_ai/core/morning_brief.py`

Trigger: Cron job at 7:00 AM agent's timezone

Contents:
- Top 3 urgent deals (by priority matrix)
- New risks detected overnight
- Silent parties flagged
- Deadlines today/tomorrow
- Recommended proactive actions

Format: Email or browser notification

=============================================================================
# PHASE 8: GATEWAY & INTEGRATIONS (Week 7-8)

Step 8.1: Email Gateway
File: `guardian_ai/gateway/email_gateway.py`

Integrations:
- Gmail API (OAuth2)
- Microsoft Graph API (Outlook)

Features:
- Read threads in background (polling or webhook)
- Parse and store emails in database
- Draft replies in compose window
- Approval buttons inline
- Webhook for real-time new email detection

Rate Limiting:
- Handle Gmail API quotas (100 queries/second, 100k/day)
- Implement exponential backoff
- Queue messages if rate limited

Step 8.2: CRM Gateway
File: `guardian_ai/gateway/crm_gateway.py`

Integrations:
- Follow Up Boss API
- kvCORE API
- LionDesk API

Features:
- Bi-directional sync:
  - Pull: contact data, deal status, communications
  - Push: AI insights, risk flags, suggested tasks
- Custom field mapping per CRM (each CRM has different field names)
- Real-time webhook updates
- Fallback to polling if webhooks not available

================================================================================
# PHASE 9: SCHEDULED TASKS & AUTOMATION (Week 8)

Step 9.1: Periodic Deal Health Checks
File: `guardian_ai/core/health_checker.py`

Trigger: Every 2 hours

Actions:
- Recalculate Deal Safety Scores for all active deals
- Update friction model baselines
- Check for new communications since last check
- Re-prioritize if conditions changed
- Flag any deals that crossed risk thresholds

Step 9.2: Proactive Reminder Engine
File: `guardian_ai/core/reminder_engine.py`

Logic:
- Before deadline: remind at 7 days, 3 days, 1 day, day-of
- After silence: remind based on contact's baseline (not generic 24h)
  - If lender baseline is 2 hours → remind after 4 hours
  - If seller baseline is 24 hours → remind after 48 hours
- Escalation: if no response after 2 reminders, suggest phone call not email
- Channel preference: respect agent's preference for email vs SMS vs phone

Step 9.3: Background Processing (Celery)
File: `guardian_ai/tasks/`

Task Queues:
- High priority queue: urgent deal checks, risk alerts, wire fraud verification
- Default queue: daily syncs, market data refresh, preference updates
- Low priority queue: analytics aggregation, report generation, archive tasks

Tasks:
- document_ocr_queue: Process uploaded documents asynchronously
- communication_sync: Sync emails/SMS periodically
- risk_recalculation: Update deal scores in background
- market_data_refresh: Update external market data daily
- signature_status_check: Poll DocuSign/dotloop for signature status updates
- wire_fraud_monitor: Check for wire instruction changes

**Error Handling & Resilience (Applies to Phase 9):**
- Circuit breaker: If DocuSign/dotloop API fails 3 times, alert agent and use cached signature status
- Dead letter queue for failed async tasks (document OCR, communication sync)
- Fallback: If Celery workers unavailable, process tasks synchronously with timeout
- Rate limiting for external API calls (ATTOM, CRM webhooks)

================================================================================
# PHASE 10: COMPLIANCE & AUDIT (Week 8-9)

Step 10.1: Immutable Audit Trail
File: `guardian_ai/core/audit_logger.py`

Logs EVERYTHING:
- AI saw: document X, email Y, text Z
- AI suggested: draft email, risk flag, task creation
- Human decided: approved / edited / rejected / ignored
- Timestamp, tenant_id, deal_id, full context
- User session ID

Storage:
- Append-only PostgreSQL table
- Encrypted at rest
- Tamper-evident (hash chain)
- No updates or deletes allowed (only inserts)

Step 10.2: E&O Compliance Reports
File: `guardian_ai/tools/compliance_tools.py`

Generate on demand:
- Full deal timeline with all AI suggestions and human decisions
- Document checklist completion proof (which docs received, which pending)
- Communication log with timestamps
- Risk flags and how they were addressed
- Export to PDF for insurance claims

Step 10.3: Florida Regulatory Compliance
File: `guardian_ai/config/frec_compliance.py`

- Track FREC continuing education requirements
- Verify license status for involved agents
- Log all communication for FREC audit requirements
- Ensure proper disclosure protocols

=============================================================================
# PHASE 11: CONTINUOUS LEARNING (RLHF) (Week 9-10)

**Error Handling & Resilience (Applies to all phases):**
- Circuit breaker for external APIs: if ATTOM fails 3 times, switch to cached data + alert
- Fallback LLM: primary GPT-4, fallback Gemini, emergency local Llama-3
- Graceful degradation: if OCR confidence < 50%, immediately flag for human review instead of retrying
- Dead letter queue: failed tasks go to DLQ for manual inspection after 3 retries
- Exponential backoff: 1s, 2s, 4s, 8s, 16s between retries

Step 11.1: Training Signal Capture
File: `guardian_ai/learning/rlhf_loop.py`

Capture EVERY interaction:

| Signal Type | Example | Training Data |
|-------------|---------|---------------|
| Email approved | Agent approves draft | Positive reward for that style |
| Email edited | Agent modifies draft | Store delta, learn correction |
| Risk overridden | Agent dismisses flag | Adjust model weights |
| Extraction corrected | Agent fixes extracted date | NER training data |
| Task completed late | Deadline missed | Deadline prediction adjustment |
| Preference changed | Agent changes email tone | Update preference model |

Step 11.2: Model Fine-Tuning Pipeline
File: `guardian_ai/learning/fine_tuner.py`

Weekly batch process:
1. Aggregate RLHF data from past week
2. Filter for high-confidence signals (multiple corrections of same type)
3. Fine-tune communication model:
   - LoRA adapter on base LLM (GPT-4 or open model)
   - Focus on real estate email patterns
4. Fine-tune extraction model:
   - LayoutLMv3 fine-tuning on corrected documents
   - Improve date/entity extraction
5. Update friction model weights:
   - Adjust baseline thresholds based on overrides
6. Deploy new models per tenant (personalized to each agent)

Step 11.3: Preference Learning
File: `guardian_ai/learning/preference_learner.py`

Track per agent:
- Email tone: formal / casual, detailed / brief
- Working hours: when to send reminders (avoid nights/weekends)
- Risk tolerance: how early to flag issues (aggressive vs conservative)
- Communication channel preferences: email vs SMS vs phone
- Preferred task assignment: what agent handles vs delegates to TC

Step 11.4: Market Adaptation
File: `guardian_ai/learning/market_learner.py`

Learn Florida-specific patterns:
- Seasonal patterns: Q1 busy, Q3 slow
- Typical closing timelines by area
- Common inspection issues (older homes = more findings)
- Lender behavior patterns (which lenders are fast/slow)

================================================================================
# PHASE 11.5: AI/ML FRAMEWORK (Week 10)

Step 11.5.1: Prompt Templates with Few-Shot Examples
File: `guardian_ai/ai_framework/prompts/`
- Create prompt templates for each task type:
  - Document extraction prompts with 3-5 few-shot examples
  - Email summarization prompts with real estate context
  - Risk assessment prompts with chain-of-thought examples
  - Communication drafting prompts with tone/style examples
- Template versioning and A/B testing capability

Step 11.5.2: Chain-of-Thought Reasoning
- Force AI to show work before giving answer
- Structured reasoning output: [OBSERVATION] → [ANALYSIS] → [CONCLUSION]
- Required for: risk assessments, compliance checks, deal scoring
- Log reasoning chains for audit and debugging

Step 11.5.3: Hallucination Guardrail
- Verify every AI claim against source document text
- Citation requirement: every factual claim must reference source paragraph/page
- Confidence threshold: flag outputs with < 70% confidence for human review
- Cross-validate extracted data against multiple sources when available

Step 11.5.4: Output Validation Schema
- JSON schema enforcement for structured outputs
- Document extraction: validate required fields present and correctly typed
- Deal scoring: validate score is within 0-100 range with valid breakdown
- Communication drafts: validate no PII leakage, proper formatting
- Reject and regenerate if output fails schema validation

Step 11.5.5: Hybrid RAG System
- Combine vector similarity (Chroma) + BM25 keyword search
- Reciprocal Rank Fusion (RRF) to merge results from both retrieval methods
- Vector search for semantic matches: "Find docs about seller concessions"
- BM25 for exact matches: contract clause references, specific dates
- Query expansion: automatically generate related sub-queries

Step 11.5.6: Document Chunking Strategy
- Split by paragraph, 20% overlap between chunks
- Max 512 tokens per chunk
- Metadata enrichment: tag chunks with document type, section, page number
- Hierarchical chunking: section-level + paragraph-level embeddings
- Smart chunk boundaries: respect table structures and list items

Step 11.5.7: Reranking with Cross-Encoder
- Cross-encoder model to score relevance of retrieved chunks
- Re-rank top 20 vector/BM25 results down to top 5
- Fine-tune reranker on real estate Q&A pairs
- Latency budget: reranking must add < 200ms to query time

Step 11.5.8: AI Framework Directory
File: `guardian_ai/ai_framework/`
```
ai_framework/
├── prompts/                  # Prompt templates with few-shot examples
│   ├── extraction_prompts.yaml
│   ├── summarization_prompts.yaml
│   ├── risk_assessment_prompts.yaml
│   └── drafting_prompts.yaml
├── schemas/                  # Output validation schemas
│   ├── document_extraction.json
│   ├── deal_score.json
│   └── email_draft.json
├── rag/                      # RAG utilities
│   ├── hybrid_search.py
│   ├── chunker.py
│   └── reranker.py
└── reasoning/               # Chain-of-thought utilities
    └── cot_logger.py
```

================================================================================
# PHASE 12: TESTING & POLISH (Week 10-11)

Step 12.1: Unit Tests
File: `tests/unit/`

Test each tool independently:
- test_domain_guard.py: ensure it refuses non-RE requests
- test_document_extraction.py: various PDF types, scans
- test_sentiment_analysis.py: known email samples
- test_friction_model.py: baseline tracking, anomaly detection
- test_deal_safety_score.py: score calculation accuracy

Step 12.2: Integration Tests
File: `tests/integration/`

End-to-end scenarios:
- upload_contract → extract_data → detect_missing_doc → draft_reminder → human_approves → send_email → log_audit
- email_received → parse_thread → detect_sentiment → update_risk_score → create_task

Multi-agent delegation tests:
- complex task across sub-agents
- proper result synthesis

Gateway integration tests:
- email_read → AI_processing → CRM_update

Step 12.3: Florida-Specific Validation
File: `tests/florida_specific/`

- Test with actual FAR/BAR contracts (anonymized)
- Validate Florida checklist compliance
- Test hurricane disclosure triggers
- Verify FREC regulation references
- Test Chapter 475 compliance

Step 12.4: Performance Testing
- Document extraction speed (<5 seconds for standard contract)
- Email parsing latency (<1 second per email)
- Deal safety score calculation (<2 seconds)
- Concurrent user load testing

Step 12.5: Property-Based Testing
File: `tests/property/`
- Generate 1000 random date combinations, verify timeline calculations
- Test with invalid, overlapping, and boundary date scenarios
- Florida business day calculations across holidays
- Property types: residential, commercial, vacant land variations

Step 12.6: Contract Fuzzing
File: `tests/fuzzing/`
- Test with 50 corrupted/malformed PDFs (truncated, corrupted, non-standard layouts)
- Ensure no crashes or hangs on malformed documents
- Validate graceful error handling and recovery
- OCR fallback behavior verification

Step 12.7: Load Testing
- Simulate 100 concurrent agents, 1000 deals each
- Measure response times under load
- Verify PostgreSQL read replicas handle query load
- Test PgBouncer connection pooling under load
- Redis cache hit rate under concurrent access
- Target: <200ms p95 response time at full load

Step 12.8: Chaos Testing
- Randomly kill 30% of Celery workers, verify system recovers in < 30 seconds
- Test circuit breaker activation during external API failures
- Verify DLQ processing after worker recovery
- Database connection recovery after network partition
- Validate fallback LLM switch when primary fails

Step 12.9: Security Testing
File: `tests/security/`
- SQL injection prevention: verify parameterized queries prevent injection
- XSS prevention: sanitize AI outputs before display
- PII encryption verification: confirm AES-256 encryption on sensitive fields
- Rate limiting enforcement: verify 100 req/min per tenant limits
- JWT token validation and revocation testing
- Wire fraud detection: verify instruction change triggers callback

=============================================================================
# PHASE 13: DEPLOYMENT (Week 11-12)

Step 13.1: Docker Containerization
```dockerfile
FROM python:3.11-slim
COPY guardian_ai/ /app/guardian_ai/
COPY hermes-core/ /app/hermes-core/
RUN pip install -r requirements.txt
ENV PYTHONPATH=/app
CMD ["python", "-m", "guardian_ai.main"]
```

Step 13.2: Cloud Deployment Architecture

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
   │ Worker 1│         │ Worker 2│         │ Worker 3│
   └────┬────┘         └────┬────┘         └────┬────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────▼───────┐
                    │  PostgreSQL   │
                    │  (RDS/CloudSQL)│
                    └───────────────┘
```

AWS/GCP:
- PostgreSQL: Managed database (RDS/Cloud SQL)
- Redis: Managed cache (ElastiCache/Memorystore)
- Celery workers: Auto-scaling based on queue depth
- API Gateway for authentication

Step 17.3: Monitoring & Observability

Agent performance:
- Deal Safety Score accuracy (human override rate)
- Human approval rates (>90% approval = good)
- Email draft acceptance rate

System health:
- API response times
- Queue depths
- Error rates by type
- OCR success rate

Learning metrics:
- RLHF signal volume per week
- Model improvement curves
- Preference convergence (how stable are preferences)

================================================================================
# CRITICAL SUCCESS PRINCIPLES

1. **Hermes is your foundation, not your cage**
   - Use its agent loop, memory, tool system
   - Replace its generic SOUL with your real estate persona

2. **Florida first, Florida deep**
   - Perfect understanding of FAR/BAR contracts
   - Beats mediocre support for 50 states

3. **Self-learning is your moat**
   - Every competitor can copy features
   - They cannot copy your agent's learned understanding

4. **Trust through transparency**
   - Show your work
   - Every AI suggestion must include WHY

5. **Human sovereignty**
   - The agent suggests, the human decides
   - No exceptions

6. **Zero-Dashboard or nothing**
   - If agents have to learn a new interface, you've lost

7. **Domain lockdown**
   - Strictly refuse non-real-estate requests
   - Be hyper-specialized, not generalist

8. **Proactive, not reactive**
   - Predict problems before they happen
   - Don't just react to issues

================================================================================
# FLORIDA LEGAL REFERENCE

## FAR/BAR Contract Types
- Contract for Sale and Purchase
- Residential Contract
- Vacant Land Contract
- Commercial Contract
- Assignment of Contract

## Florida-Specific Disclosures
- Seller's Property Disclosure (AS IS)
- Seller's Property Disclosure (Traditional)
- Lead-Based Paint Disclosure
- Flood Zone Disclosure
- Coastal Property Disclosure
- Wind Mitigation Disclosure
- Homestead Exemption Notice
- Property Tax Information
- Asbestos Disclosure (commercial)

## FREC Regulations
- Chapter 475, Florida Statutes
- License requirements
- Commission disclosure
- Transaction brokerage disclosure

## Florida Timeline Standards
- Earnest money deposit: 3 days
- Loan application: 3 days
- Lender documents: 3 days after approval
- Inspection period: 10-15 days
- Financing commitment: 30-45 days
- Title commitment: 10-20 days before closing
- Closing: 45-60 days (financed), 30-45 days (cash)

================================================================================
# PHASE 14: REAL ESTATE POWER FEATURES (Week 12-13)

Step 14.1: Signature Tools
File: `guardian_ai/tools/signature_tools.py`
- DocuSign API integration
- dotloop API integration
- Track signature status in real-time
- Send reminders for unsigned documents
- Store signed documents with audit trail
- Signature verification

Step 14.2: Wire Fraud Guard
File: `guardian_ai/tools/wire_fraud_guard.py`
- Monitor for wire instruction changes in communications
- Compare current wire instructions against baseline
- Flag any modification immediately
- Enforce phone callback verification: agent must call title company directly
- Dual-approval for wire transfers above $100K
- Audit trail for all wire-related communications

Step 14.3: Offer Tools
File: `guardian_ai/tools/offer_tools.py`
- Counter-offer drafting with strategy notes
- Multiple offer comparison matrix
- Bidding war tracker
- Offer timeline management
- Seller response follow-up automation

Step 14.4: CMA Tools
File: `guardian_ai/tools/cma_tools.py`
- Pull comparables from MLS/ATTOM
- Generate professional CMA report
- Adjust for condition, location, upgrades
- Historical price trend analysis
- Days on market comparison

Step 14.5: Calendar Tools
File: `guardian_ai/tools/calendar_tools.py`
- Schedule inspections
- Schedule closings
- Set deadline reminders
- Google Calendar integration
- Outlook Calendar integration
- Automatic reminder notifications

Step 14.6: Voice Tools
File: `guardian_ai/tools/voice_tools.py`
- Log phone calls with transcription
- Transcribe voicemails automatically
- Extract key points from conversations
- Sentiment analysis on voice communications
- Call summary for deal context

================================================================================
# PHASE 15: BUSINESS OPERATIONS (Week 13-14)

Step 15.1: Onboarding Wizard
File: `guardian_ai/onboarding/`
5-step setup wizard:
1. Connect email (Gmail/Outlook OAuth)
2. Connect CRM (FUB, kvCORE, LionDesk)
3. Upload first contract or import existing deals
4. Set preferences (tone, working hours, notification preferences)
5. Welcome dashboard with quick tutorial

Step 15.2: Migration Tool
File: `guardian_ai/migration/`
- CSV import from Dotloop
- CSV import from SkySlope
- Import from TCdocs
- Batch deal migration
- Field mapping UI
- Migration validation and error reporting

Step 15.3: Analytics Dashboard
File: `guardian_ai/dashboard/`
Metrics:
- Deals closed (monthly/quarterly/yearly)
- Hours saved (estimated based on task automation)
- Risks prevented (deal-killers caught before closing)
- ROI calculator: subscription cost vs. deals protected
- Agent productivity trends
- Communication efficiency metrics

Step 15.4: Billing System
File: `guardian_ai/billing/`
Pricing tiers:
- $49/month per agent (unlimited deals)
- OR $15 per closed deal (pay-per-deal)
- Free trial: 3 deals free, no credit card required
- Annual subscription discount: 2 months free

Step 15.5: Feature Flags
File: `guardian_ai/feature_flags/`
- Gradual rollout of new capabilities per tenant
- A/B testing capability for new features
- Per-tenant feature enablement
- Beta program for early adopters
- Rollback capability if issues detected

================================================================================
# TAGLINES FOR CUSTOMER MESSAGING

- "Your Silent Guardian. Your Crystal Ball. Your Deal Co-Pilot."
- "It doesn't just manage your deals — it protects them."
- "The more you use it, the smarter it gets."
- "Zero dashboards. Zero new interfaces. Zero learning curve."
- "Predict problems before they become closing nightmares."

================================================================================
# END OF PLAN