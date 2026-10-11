# Deterministic Policy Rules

The policy engine, not an AI model, makes the final authorization decision.

## Demo configuration
Known agents and permissions should be explicit in code or configuration. Example:
- `agent-01`: may `update_record`, may not `delete_record`
- `agent-02`: may `update_record` and `create_ticket`
- all other agent IDs: unknown and blocked

Supported demo action types:
- `update_record` — low-impact only when target and arguments are valid and permission exists
- `create_ticket` — simulated creation; permission required
- `delete_record` — treat as high-impact; HOLD or BLOCK according to the explicit policy
- any unknown action type — BLOCK

## Required decision order
1. Validate required fields and data types. Invalid input: BLOCK.
2. Is the agent known? If not: BLOCK.
3. Is the action type known? If not: BLOCK.
4. Does this agent have explicit permission for this action type? If not: BLOCK.
5. Does the action exceed safe limits, affect many records, or appear irreversible? BLOCK or HOLD according to the configured policy.
6. If human approval is required, return HOLD.
7. Only if all checks pass, return ALLOW.

## Approval and execution
- Requester cannot approve their own action.
- Store the canonical action hash at evaluation time.
- Approval refers to that exact hash, not merely an action ID.
- At execution, recompute the hash and compare it to the approved hash.
- Revalidate policy immediately before simulated execution.
- Any hash mismatch or policy failure prevents execution and requires reauthorization.

## Optional AI assessor
AI output is advisory only. It cannot override a BLOCK or create permission that policy does not grant. If unavailable or malformed, use deterministic rules and record the fallback path. Never execute based only on AI output.
