-- jPOS EE Database Schema
-- Created: April 21, 2026
-- Purpose: Persistence layer for jPOS EE transaction processing, routing rules, and audit logs

-- ============================================================================
-- TRANSACTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS jposee_transactions (
    id SERIAL PRIMARY KEY,
    txn_id VARCHAR(50) UNIQUE NOT NULL,                -- Unique transaction ID
    txn_type VARCHAR(20) NOT NULL,                     -- Purchase, Refund, Transfer, etc.
    amount DECIMAL(15,2) NOT NULL,                     -- Transaction amount
    currency VARCHAR(3) DEFAULT 'USD',                 -- Currency code
    status VARCHAR(20) NOT NULL,                       -- success, failed, pending, reversed
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    card_last4 VARCHAR(4),                             -- Last 4 digits of card
    card_bin VARCHAR(6),                               -- Bank Identification Number
    merchant_id VARCHAR(50),                           -- Merchant identifier
    merchant_name VARCHAR(255),                        -- Merchant name
    merchant_category VARCHAR(50),                     -- Merchant category code
    iso_fields JSONB,                                  -- Full ISO 8583 message fields
    routing_info JSONB,                                -- Routing information
    gateway_response JSONB,                            -- Response from payment gateway
    duration_ms INTEGER,                               -- Processing time in milliseconds
    retry_count INTEGER DEFAULT 0,                     -- Number of retries
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_jposee_txn_txn_id ON jposee_transactions(txn_id);
CREATE INDEX idx_jposee_txn_status ON jposee_transactions(status);
CREATE INDEX idx_jposee_txn_timestamp ON jposee_transactions(timestamp DESC);
CREATE INDEX idx_jposee_txn_merchant_id ON jposee_transactions(merchant_id);
CREATE INDEX idx_jposee_txn_card_bin ON jposee_transactions(card_bin);


-- ============================================================================
-- ROUTING RULES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS jposee_routing_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(255) NOT NULL UNIQUE,
    rule_description TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,                       -- Higher number = higher priority
    
    -- Match Criteria (stored as JSONB for flexibility)
    criteria JSONB NOT NULL,                          -- Contains:
                                                       -- - message_type (ISO 8583 type)
                                                       -- - amount_min, amount_max
                                                       -- - bin_ranges (array)
                                                       -- - merchant_category
                                                       -- - custom_fields
    
    -- Action Configuration
    action JSONB NOT NULL,                            -- Contains:
                                                       -- - route (gateway name)
                                                       -- - transform_fields
                                                       -- - log_level
                                                       -- - timeout_ms
    
    -- Statistics
    hit_count INTEGER DEFAULT 0,                      -- Number of times rule matched
    success_count INTEGER DEFAULT 0,                  -- Successful transactions
    failed_count INTEGER DEFAULT 0,                   -- Failed transactions
    total_duration_ms INTEGER DEFAULT 0,              -- Cumulative processing time
    
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_jposee_rules_enabled ON jposee_routing_rules(enabled);
CREATE INDEX idx_jposee_rules_priority ON jposee_routing_rules(priority DESC);
CREATE INDEX idx_jposee_rules_created_at ON jposee_routing_rules(created_at DESC);


-- ============================================================================
-- AUDIT LOG TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS jposee_audit_logs (
    id SERIAL PRIMARY KEY,
    action_type VARCHAR(50) NOT NULL,                 -- LOGIN, RULE_CREATED, TXN_PROCESSED, etc.
    user_id INTEGER,
    username VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    
    resource_type VARCHAR(50),                        -- RoutingRule, Transaction, Config, etc.
    resource_id VARCHAR(100),
    
    result VARCHAR(20) NOT NULL,                      -- SUCCESS, FAILURE, PARTIAL
    error_message TEXT,
    
    details JSONB,                                    -- Action-specific details
    changes JSONB,                                    -- Before/after for updates
    
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_jposee_audit_action ON jposee_audit_logs(action_type);
CREATE INDEX idx_jposee_audit_user ON jposee_audit_logs(user_id);
CREATE INDEX idx_jposee_audit_timestamp ON jposee_audit_logs(timestamp DESC);
CREATE INDEX idx_jposee_audit_result ON jposee_audit_logs(result);
CREATE INDEX idx_jposee_audit_resource ON jposee_audit_logs(resource_type, resource_id);


-- ============================================================================
-- BATCH JOBS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS jposee_batch_jobs (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50) UNIQUE NOT NULL,
    batch_name VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL,                      -- pending, running, completed, failed, cancelled
    
    total_records INTEGER NOT NULL,
    processed_records INTEGER DEFAULT 0,
    successful_records INTEGER DEFAULT 0,
    failed_records INTEGER DEFAULT 0,
    
    file_path VARCHAR(500),                           -- Path to input file
    file_type VARCHAR(20),                            -- csv, xml, json
    
    mapping JSONB,                                    -- Field mapping configuration
    rules JSONB,                                      -- Processing rules
    
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_jposee_batch_status ON jposee_batch_jobs(status);
CREATE INDEX idx_jposee_batch_batch_id ON jposee_batch_jobs(batch_id);
CREATE INDEX idx_jposee_batch_created_at ON jposee_batch_jobs(created_at DESC);


-- ============================================================================
-- BATCH JOB RESULTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS jposee_batch_results (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER REFERENCES jposee_batch_jobs(id) ON DELETE CASCADE,
    record_number INTEGER,
    txn_id VARCHAR(50),
    
    status VARCHAR(20),                               -- success, failed
    error_message TEXT,
    
    input_data JSONB,
    processed_data JSONB,
    response_data JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_jposee_batch_results_batch_id ON jposee_batch_results(batch_id);
CREATE INDEX idx_jposee_batch_results_status ON jposee_batch_results(status);


-- ============================================================================
-- ALERT CONFIGURATION TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS jposee_alert_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Default alert configurations
INSERT INTO jposee_alert_config (config_key, config_value, description) VALUES
    ('error_rate_threshold', '1.0', 'Alert if error rate exceeds percentage'),
    ('latency_threshold_ms', '1000', 'Alert if average latency exceeds milliseconds'),
    ('transaction_per_sec_min', '100', 'Alert if TPS drops below this threshold'),
    ('connection_timeout_ms', '5000', 'Connection timeout in milliseconds'),
    ('retry_max_attempts', '3', 'Maximum retry attempts for failed transactions'),
    ('log_level', 'info', 'Logging level: debug, info, warn, error')
ON CONFLICT DO NOTHING;


-- ============================================================================
-- PERFORMANCE METRICS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS jposee_metrics (
    id SERIAL PRIMARY KEY,
    metric_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    transactions_per_sec DECIMAL(10,2),               -- TPS
    error_rate_percent DECIMAL(5,2),                  -- Error percentage
    avg_latency_ms DECIMAL(10,2),                     -- Average latency
    p95_latency_ms DECIMAL(10,2),                     -- 95th percentile latency
    p99_latency_ms DECIMAL(10,2),                     -- 99th percentile latency
    throughput_mbps DECIMAL(10,2),                    -- Throughput in MB/s
    
    active_transactions INTEGER,                      -- Current active transactions
    queue_depth INTEGER,                              -- Pending transactions in queue
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_jposee_metrics_time ON jposee_metrics(metric_time DESC);


-- ============================================================================
-- ALERTS HISTORY TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS jposee_alerts_history (
    id SERIAL PRIMARY KEY,
    alert_level VARCHAR(20) NOT NULL,                 -- info, warning, error, critical
    alert_message TEXT NOT NULL,
    
    metric_name VARCHAR(100),
    threshold_value DECIMAL(15,2),
    actual_value DECIMAL(15,2),
    
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE,
    is_resolved BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_jposee_alerts_level ON jposee_alerts_history(alert_level);
CREATE INDEX idx_jposee_alerts_triggered ON jposee_alerts_history(triggered_at DESC);
CREATE INDEX idx_jposee_alerts_resolved ON jposee_alerts_history(is_resolved);


-- ============================================================================
-- SYSTEM INFO TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS jposee_system_info (
    id SERIAL PRIMARY KEY,
    info_key VARCHAR(100) UNIQUE NOT NULL,
    info_value TEXT,
    
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Initialize system info
INSERT INTO jposee_system_info (info_key, info_value) VALUES
    ('jposee_version', '1.0.0'),
    ('database_version', '1.0.0'),
    ('last_startup', CURRENT_TIMESTAMP::TEXT),
    ('status', 'operational')
ON CONFLICT DO NOTHING;


-- ============================================================================
-- VIEWS
-- ============================================================================

-- View for dashboard statistics
CREATE OR REPLACE VIEW vw_jposee_dashboard_stats AS
SELECT
    COUNT(*) as total_transactions,
    COUNT(*) FILTER (WHERE status = 'success') as successful_transactions,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_transactions,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'success') / NULLIF(COUNT(*), 0), 2) as success_rate_percent,
    ROUND(AVG(duration_ms), 2) as avg_response_time_ms,
    DATE_TRUNC('day', timestamp) as transaction_day
FROM jposee_transactions
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', timestamp)
ORDER BY transaction_day DESC;


-- View for active alerts
CREATE OR REPLACE VIEW vw_jposee_active_alerts AS
SELECT
    id,
    alert_level,
    alert_message,
    metric_name,
    threshold_value,
    actual_value,
    triggered_at,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - triggered_at)) / 60 as minutes_active
FROM jposee_alerts_history
WHERE is_resolved = FALSE
ORDER BY triggered_at DESC;


-- ============================================================================
-- GRANTS (for application user)
-- ============================================================================
-- Uncomment and adjust user/password as needed
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO jposee_app;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO jposee_app;
-- GRANT SELECT ON ALL VIEWS IN SCHEMA public TO jposee_app;

COMMIT;
