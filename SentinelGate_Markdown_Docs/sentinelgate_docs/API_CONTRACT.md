# API Contract

Keep these endpoint names and JSON field names stable so backend and frontend can be developed independently.

## `GET /health`
Example:
```json
{"status":"ok"}
```

## `POST /actions/evaluate`
Request:
```json
{
  "agent_id": "agent-01",
  "requester_id": "user-01",
  "action_type": "update_record",
  "target": "customer-101",
  "arguments": {
    "field": "status",
    "value": "verified"
  }
}
```

Response:
```json
{
  "action_id": "generated-id",
  "decision": "ALLOW",
  "reason": "Action permitted by policy",
  "action_hash": "sha256-hash",
  "decision_path": "deterministic_rules"
}
```
`decision` must be exactly `ALLOW`, `BLOCK`, or `HOLD`. `decision_path` can be `deterministic_rules` or `ai_unavailable_fallback` if an optional AI assessor is attempted and unavailable.

## `GET /actions/pending`
Returns actions awaiting human approval. Do not include secrets.

## `POST /actions/{id}/approve`
Request:
```json
{"approver_id":"reviewer-02"}
```
Reject if the approver is the same identity as the requester. Approval must be recorded against the exact action hash.

## `POST /actions/{id}/reject`
Request:
```json
{"approver_id":"reviewer-02","reason":"Insufficient justification"}
```

## `POST /actions/{id}/execute`
Request:
```json
{"executor_id":"operator-01"}
```
Only execute a valid `ALLOW` action or a `HOLD` action with a valid approval. Recompute the canonical action hash and revalidate policy before execution. If the action changed since approval, refuse execution and require reauthorization.

## `GET /audit`
Returns audit events in chronological order.

## `GET /audit/verify`
Example response:
```json
{"valid":true,"checked_events":12,"message":"Audit chain verified"}
```
If tampering is detected, `valid` must be `false`.

## Error response convention
Use an HTTP error status and a concise JSON `detail` message. Every refusal or rejected approval/execution attempt should also create an audit event.
