# 3-Minute Demo Script

## Opening (20 seconds)
“AI agents can do more than answer questions: they can change data or trigger actions. SentinelGate is a policy-enforcement gateway that checks every proposed action before it reaches an executor.”

## Scenario 1 — Allowed action (30 seconds)
Submit a small, permitted update from a known agent. Show `ALLOW`, the reason, action hash, and audit event. Explain that permission and policy—not the model's confidence—authorize it.

## Scenario 2 — Unknown agent (25 seconds)
Submit the same type of action from an unknown agent. Show `BLOCK`. Explain the default-deny rule.

## Scenario 3 — High-impact action (30 seconds)
Submit a bulk deletion. Show `HOLD` or `BLOCK` based on the implemented rule. Explain that the action cannot execute until the required approval conditions are satisfied.

## Scenario 4 — Approval binding (45 seconds)
Show a pending action. Try approving as the requester and show rejection. Approve as a different identity, then change an argument. Attempt execution and show that the hash mismatch prevents execution.

## Scenario 5 — Audit integrity and fallback (30 seconds)
Show audit-chain verification. In a test fixture, alter an event and show verification failure. If the optional AI assessor is unavailable, show that deterministic policy still makes the decision and the fallback path is logged.

## Closing (20 seconds)
“SentinelGate does not blindly trust the agent. It enforces explicit permissions, separates requesters from approvers, binds approval to the exact action, and keeps a tamper-evident decision history.”
