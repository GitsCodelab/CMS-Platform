# Quick Reference: Token Cost Control

## Start Every Session With This Checklist

```
□ Check today's cost so far in logs/costs.jsonl
□ Estimate task tokens needed from rules/token_budgets.json
□ Confirm you have budget remaining ($50 daily limit)
□ Review which tools to use from commands/operation_costs.json
```

## Token Budget by Task Type

| Task | Tokens | Cost | Time |
|------|--------|------|------|
| Quick fix | 5K | $0.05 | 5min |
| Code review | 10K | $0.10 | 10min |
| Bug debug | 15K | $0.30 | 15min |
| Feature build | 25K | $0.50 | 30min |
| Big refactor | 50K | $1.00 | 60min |

## Most Important Optimization Rules

1. **grep_search instead of semantic_search**: 75% cheaper
2. **Batch edits, don't sequence them**: 50% cheaper  
3. **Read line ranges, not full files**: 60% cheaper
4. **Parallelize independent operations**: 30% cheaper

## Tool Cost Ranking (cheapest to most expensive)

1. git_operations: $0.003
2. run_in_terminal: $0.005
3. grep_search: $0.006
4. database_query: $0.006
5. read_file: $0.004
6. file_creation: $0.010
7. file_edit: $0.012
8. semantic_search: $0.016 ⚠️ EXPENSIVE

## If You Run Out of Budget Today

- Switch to grep_search (not semantic)
- Use terminal for exploration instead of tools
- Read specific lines, not entire files
- Batch your edits together
- Use the Explore subagent for complex tasks (costs once)

## Estimated Daily Spend

- **Light usage** (bug fixes, reviews): $5-10/day
- **Normal usage** (features, refactoring): $20-30/day
- **Heavy usage** (major project work): $40-50/day

## Contact Information

If costs exceed $50/day, review optimization opportunities in:
- `rules/optimization.json` - 5+ strategies
- `commands/operation_costs.json` - tool costs
- `logs/sessions.jsonl` - what worked before

---
**Keep this in mind**: Using $0.006 grep_search instead of $0.016 semantic_search saves 63% per operation. This adds up quickly!
