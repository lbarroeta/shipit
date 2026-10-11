# External contracts

## Order API

GET order returns integer `total_cents`. Clients can keep reading this field.

## Partner payload

The partner rejects unknown fields. Its payload contains exactly `id` and
`total_cents`. It must not inherit future public API fields.

## CSV

CSV rows have exactly two columns: ID and integer total cents.

## Downloads

Only the same-tenant owner or a same-tenant administrator may download a document.
Denied requests return 403 before blob access, even if identifiers are guessed.

## Refunds

Current behavior refunds the full paid amount for paid orders. No partial-refund
policy has been accepted. Eligibility and monetary rounding changes need a
product decision.
