# Test Plan

Use pytest. Prioritize the safety invariants before visual polish.

## Required tests
1. Known agent + permitted small reversible update returns `ALLOW`.
2. Unknown agent returns `BLOCK`.
3. Unknown action type returns `BLOCK`.
4. Known agent without permission returns `BLOCK`.
5. Bulk or irreversible action returns `HOLD` or `BLOCK`, according to explicit policy.
6. Requester attempting to approve their own action is rejected and audited.
7. A different approver can approve an eligible `HOLD` action.
8. A changed argument after approval prevents execution.
9. An unapproved `HOLD` action cannot execute.
10. An approved unchanged action can execute in the simulator.
11. Every decision and rejected approval/execution attempt creates an audit event.
12. Audit verification passes for a valid chain.
13. Editing an event without updating its hash causes verification to fail.
14. AI assessor unavailable or malformed does not grant new permissions and records the fallback path.

## Manual demo checklist
- [ ] Submit a permitted update and show ALLOW.
- [ ] Submit an unknown agent and show BLOCK.
- [ ] Submit a bulk deletion and show HOLD/BLOCK.
- [ ] Approve with a different user identity.
- [ ] Change an argument and show execution refused.
- [ ] Disable/fail the optional AI assessor and show deterministic fallback.
- [ ] Demonstrate audit verification failure on a test copy or controlled test fixture.

## Test safety
Never demonstrate tampering by altering the only copy of valuable data. Use an isolated test database or a dedicated test fixture.
