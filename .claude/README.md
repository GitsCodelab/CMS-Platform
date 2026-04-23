# Token & Cost Tracking Infrastructure

This folder contains the configuration and logs for monitoring and controlling AI agent token usage and costs across chat sessions.

## Project Context Files

### `/docker-services.json` - Docker Service Documentation
- Complete list of all running services with ports and purposes
- Connection strings for databases (localhost vs container)
- Service dependencies and startup order
- Health checks and configuration details
- **USE THIS**: Before deploying, to understand which services are running

### `/tools.json` - Available Tools Reference
- Apache Airflow (workflow orchestration, DAG management)
- WSO2 API Manager (API gateway, lifecycle management)
- Apache Superset (BI/analytics - ready to deploy)
- Database tools and dev tools
- Quick reference commands
- **USE THIS**: When working with specific tools, to find configuration and access points

### `/architecture.json` - System Architecture & Data Flow
- Detailed explanation of each layer (presentation, API gateway, application, data, orchestration)
- How services communicate and depend on each other
- Data flow examples (user requests, API gateway, ETL pipelines)
- Network communication (Docker DNS, localhost vs service names)
- Startup sequence and scaling considerations
- **USE THIS**: To understand how components interact before making changes

### `/tech-stack.json` - Technology Stack Details
- Complete version information for all languages and frameworks
- Backend stack (FastAPI, SQLAlchemy, Pydantic, Uvicorn)
- Frontend stack (React, Vite, Tailwind CSS, OpenUI5)
- Database versions and drivers
- Package dependencies and directory structure
- Environment variables and configuration
- **USE THIS**: When debugging version conflicts or adding new packages

## Token & Cost Tracking Files

### `/settings.json` - Main Configuration
- **Pricing Models**: Claude Haiku, Opus, Sonnet rates
- **Token Limits**: Per-session budgets
- **Optimization Strategies**: Tool usage recommendations
- **Tracking Settings**: Log file paths
- **Budget Alerts**: Daily ($50), Weekly ($300), Monthly ($1000)

### `/settings.local.json` - Session-Specific Data
- Track current session tokens and costs
- Per-agent token allocation
- Budget remaining

### `/agents/` - Agent Definitions
- **profiles.json**: Cost estimates for each agent type
  - Explore agent: $0.10 per call
  - Implementation agent: $0.30 per call
  - Debugging agent: $0.20 per call
  
- **usage.json**: Cumulative usage per agent
  - Tracks total calls, total cost, efficiency metrics

### `/commands/` - Tool Operation Costs
- **operation_costs.json**: Average token/cost per tool
  - Most expensive: `semantic_search` (0.016 per call)
  - Most efficient: `grep_search` (0.006 per call)
  
- **usage_patterns.json**: Which operations are expensive vs efficient

### `/rules/` - Optimization Guidelines
- **optimization.json**: 5+ optimization strategies with % savings
  - Parallel operations: 30-40% savings
  - Batch edits: 25-35% savings
  - Grep over semantic: 50-75% savings
  
- **token_budgets.json**: Per-task token budgets
  - Quick fix: 5,000 tokens ($0.05)
  - Feature implementation: 25,000 tokens ($0.50)
  - Major refactoring: 50,000 tokens ($1.00)
  
- **common_patterns.json**: 6 common workflow patterns with cost estimates

### `/logs/` - Historical Data
- **sessions.jsonl**: Per-session metadata
  - Duration, tokens used, efficiency, cost
  
- **costs.jsonl**: Daily cost tracking
  - Total spend, budget category, cost savings
  
- **tokens.jsonl**: Token usage breakdown
  - Context vs tool operations vs response

## How to Use for Cost Control

### Before Starting Work
1. Review task type budget in `rules/token_budgets.json`
2. Check agent cost in `agents/profiles.json`
3. Plan tools to use based on `commands/operation_costs.json`

### During Work
1. Use `grep_search` instead of `semantic_search` when possible (75% cheaper)
2. Parallelize independent read/search operations (30-40% savings)
3. Use `multi_replace_string_in_file` instead of sequential edits (25-35% savings)
4. Apply patterns from `rules/optimization.json`

### After Session
1. Update `settings.local.json` with actual tokens/cost
2. Log session data in `logs/sessions.jsonl`
3. Calculate efficiency: `actual_tokens / budget_tokens * 100%`
4. Review optimization opportunities for next session

## Cost Optimization Quick Reference

| Operation | Cost | Alternative | Savings |
|-----------|------|-------------|---------|
| semantic_search | $0.016 | grep_search | 75% |
| sequential edits (10x) | $0.12 | multi_replace (1x) | 50% |
| sequential reads (5x) | $0.030 | parallel reads (1x) | 30% |
| read full file | $0.010 | read lines 1-50 | 60% |

## Budget Thresholds

- **Daily**: $50.00 (stop if exceeded)
- **Weekly**: $300.00 (warn if exceeded)
- **Monthly**: $1000.00 (track for future planning)

## Tracking Metrics

- **Efficiency**: (Budget - Actual) / Budget × 100%
  - Target: >85% efficiency
  - Excellent: >95%
  
- **Tool Cost per Call**: Compare in `commands/operation_costs.json`
- **Pattern Cost**: Reference `rules/common_patterns.json`

## Integration with Chat

When starting new session, reference these budgets:
- Quick question: Use ~1,000 tokens
- Code review: Use ~5,000 tokens
- Feature build: Use ~25,000 tokens
- Full refactor: Use ~50,000 tokens

Monitor actual usage in `settings.local.json` throughout session.

## Examples

### Example 1: Finding Code
❌ **Expensive**: Semantic search for "user authentication" = $0.016
✅ **Cheap**: grep_search for "def authenticate" = $0.006
**Savings**: 63%

### Example 2: Editing Multiple Files
❌ **Expensive**: 5 sequential file edits × $0.012 = $0.060
✅ **Cheap**: 1 multi_replace call = $0.020
**Savings**: 67%

### Example 3: Reading Files
❌ **Expensive**: read_file full 500-line file = $0.008
✅ **Cheap**: read_file lines 10-50 = $0.002
**Savings**: 75%

---
**Last Updated**: 2024-12-19
**Total Setup Cost**: ~$0.25 (one-time infrastructure investment)
**Ongoing Benefit**: Track and optimize token usage across all sessions
