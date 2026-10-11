# Architecture

## Request flow
```text
Agent / Demo UI
      |
      v
Action API
      |
      v
Input validation + canonical action hash
      |
      v
Deterministic Policy Engine
      |------------------------------|
      |              |               |
    ALLOW           BLOCK            HOLD
      |              |               |
      v              v               v
Simulated        Audit event      Pending approval
execution        + response       (different approver)
      |                              |
      v                              v
Audit event <--- hash-bound approval + revalidation
      |
      v
SHA-256 hash-chained audit log
```

## Trust boundaries
- The proposed action is untrusted input.
- Text contained in the action arguments is data, not policy or instructions for the gateway.
- Deterministic policy is the final authority. An optional AI risk assessor may add context, but it cannot grant permission.
- The executor only updates in-memory or demo records.
- The audit log records decisions and actions. Verification checks each event hash and previous-event link.

## Fail-closed behavior
If validation fails, the agent is unknown, the action type is unknown, permission is absent, policy evaluation fails, or required approval cannot be verified, do not execute. Record the reason where possible.

## Audit-chain note
A hash chain detects event edits, deletions, and reordering when checked against the retained chain. An attacker who can rewrite the entire database and recompute every hash may evade a chain-only design. Production systems should anchor checkpoints outside the database.
