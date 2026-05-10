-- GuardianAI Multi-Tenant PostgreSQL Schema
-- Phase 2: Memory & Data Layer

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- TENANTS TABLE
-- Brokerages or individual agents as tenants
-- =============================================================================
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- DEALS TABLE
-- Core deal entity with multi-tenant isolation
-- =============================================================================
CREATE TABLE deals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    address TEXT NOT NULL,
    buyer_name TEXT,
    seller_name TEXT,
    status VARCHAR(50),
    deal_safety_score DECIMAL(5,2),
    contract_date DATE,
    closing_date DATE,
    listing_number VARCHAR(50),
    mls_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- DOCUMENTS TABLE
-- Store all deal-related documents with extracted data
-- =============================================================================
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    type VARCHAR(50),
    name VARCHAR(255),
    file_path TEXT,
    extracted_data JSONB DEFAULT '{}',
    ocr_confidence DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- COMMUNICATIONS TABLE
-- Track all communications per deal (email, SMS, phone, webhook)
-- =============================================================================
CREATE TABLE communications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    channel VARCHAR(20),
    sender VARCHAR(255),
    recipient VARCHAR(255),
    subject TEXT,
    content TEXT,
    sentiment_score DECIMAL(5,2),
    urgency_flag BOOLEAN DEFAULT FALSE,
    is_deal_related BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- CONTACTS TABLE
-- Store contact information with communication baselines
-- =============================================================================
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(255),
    role VARCHAR(50),
    email VARCHAR(255),
    phone VARCHAR(50),
    company VARCHAR(255),
    avg_response_time_minutes INTEGER,
    sentiment_baseline DECIMAL(5,2),
    communication_style JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- TASKS TABLE
-- AI-generated and human tasks with deadline tracking
-- =============================================================================
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    priority INTEGER,
    deadline TIMESTAMP,
    status VARCHAR(20),
    created_by_ai BOOLEAN DEFAULT TRUE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- AUDIT_LOGS TABLE (APPEND-ONLY)
-- Immutable audit trail for compliance and RLHF
-- =============================================================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID REFERENCES deals(id) ON DELETE SET NULL,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    action_type VARCHAR(50),
    ai_output TEXT,
    human_decision VARCHAR(20),
    human_correction TEXT,
    full_context JSONB DEFAULT '{}',
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Prevent UPDATE on audit_logs
CREATE OR REPLACE FUNCTION prevent_audit_update()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'UPDATE operations are not allowed on audit_logs table';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_logs_no_update
    BEFORE UPDATE ON audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION prevent_audit_update();

-- Prevent DELETE on audit_logs
CREATE OR REPLACE FUNCTION prevent_audit_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'DELETE operations are not allowed on audit_logs table';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_logs_no_delete
    BEFORE DELETE ON audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION prevent_audit_delete();

-- =============================================================================
-- AGENT_PREFERENCES TABLE
-- Self-learning storage for agent preferences
-- =============================================================================
CREATE TABLE agent_preferences (
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    preference_key VARCHAR(100),
    preference_value TEXT,
    confidence_score DECIMAL(5,2),
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (tenant_id, preference_key)
);

-- =============================================================================
-- RLHF_DATA TABLE
-- Training signal capture for continuous learning
-- =============================================================================
CREATE TABLE rlhf_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    input_context TEXT,
    ai_output TEXT,
    human_correction TEXT,
    correction_type VARCHAR(50),
    timestamp TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- COMMUNICATION_BASELINES TABLE
-- Per-contact response time and sentiment baselines for friction model
-- =============================================================================
CREATE TABLE communication_baselines (
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    role VARCHAR(50),
    avg_response_minutes DECIMAL(10,2),
    response_variance DECIMAL(10,2),
    last_updated TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- DEAL_RISKS TABLE
-- Track detected and resolved deal risks
-- =============================================================================
CREATE TABLE deal_risks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    risk_type VARCHAR(50),
    severity INTEGER,
    description TEXT,
    detected_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    resolution TEXT
);

-- =============================================================================
-- PERFORMANCE INDEXES
-- =============================================================================

-- Deals indexes
CREATE INDEX idx_deals_tenant ON deals(tenant_id);
CREATE INDEX idx_deals_status ON deals(status);

-- Documents indexes
CREATE INDEX idx_documents_deal ON documents(deal_id);

-- Communications indexes
CREATE INDEX idx_communications_deal ON communications(deal_id);

-- Contacts indexes
CREATE INDEX idx_contacts_tenant ON contacts(tenant_id);

-- Tasks indexes (partial index for pending tasks only)
CREATE INDEX idx_tasks_deadline ON tasks(deadline) WHERE status = 'pending';

-- Audit logs indexes
CREATE INDEX idx_audit_deal ON audit_logs(deal_id);
CREATE INDEX idx_audit_tenant ON audit_logs(tenant_id);

-- =============================================================================
-- PARTITIONING (for scalability)
-- Monthly partitioning for audit_logs and rlhf_data
-- =============================================================================

-- Partition audit_logs by month (example for January 2026)
CREATE TABLE audit_logs_2026_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- Partition rlhf_data by month
CREATE TABLE rlhf_data_2026_01 PARTITION OF rlhf_data
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- =============================================================================
-- UPDATED_AT TRIGGER
-- Automatically update updated_at on deals table
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_deals_updated_at
    BEFORE UPDATE ON deals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();