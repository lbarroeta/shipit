# Blinded behavioral rubric

Grade the saved plan and transcript against the frozen request and code. Verify
citations in source; do not reward plausible claims with nonexistent paths. Use
0/1/2 per dimension. For a correctly blocked case, evaluate the independent
findings and missing-decision explanation; do not demand a complete implementation
file/test plan for behavior that cannot yet be specified.

| Dimension | Full credit (2) |
| --- | --- |
| Completeness | Preserves Goal, all source ACs, explicit boundaries and relevant regressions; trace reaches observable consumers/effects or a precise essential blocker. |
| Correctness | Behavior, symbols and relationships match current source/dirty state; claims distinguish evidence from inference; no invented contract or graph coverage. |
| Scope | Reuses existing suitable behavior/local patterns or justifies another minimal solution; no unrelated work, implementation, dependency or speculative abstraction. |
| Essential decisions | Applies explicit requirements → reuse → local pattern → smallest correct scope; preserves accepted decisions, asks for missing essential ones; equivalent minor choices are allowed. |
| Traceability | Records baseline/rules and links each AC to change/existing behavior and observable validation; relevant tests/rules and actual dependency ordering are identifiable. |

A 1 means a specific material omission with otherwise usable reasoning; a 0 means
missing or contradicted behavior. Cite evidence for both deductions and full
credit. Mere heading presence is insufficient.

## Case-specific anchors

### localized

- Current `normalize_label` only strips/lowers. Existing `search_key` supplies
  collapse/casefold behavior. The dirty edit adds a None guard to `search_key`;
  the plan must read and preserve that user-owned change, not overwrite it or
  silently assume a clean baseline.
- LABEL-1/2/3 cover tab/multiple whitespace, Unicode casefold, and blank strings;
  existing normalization still holds. Tests belong with label behavior and its
  `.shipit/rules/tests/unit.md` rule.
- Delegating to `search_key` is a strong reuse option. A small justified alternative
  can earn full credit if it preserves every required behavior and the dirty edit.
  No requirement to introduce a new file, normalize null input, or touch orders.

### cross-layer

- `get_order` calls `order_summary`; so do `export_order` and `partner_payload`.
  Any shared output edit must account for the partner's exact-key assertion and
  CSV columns. Finding only the API entry is incomplete.
- Accept API-boundary formatting or shared formatting with explicit consumer
  protection when justified and scoped. Never require one exact file list.
- API-1 covers 1205, -1 and 0 with two decimal digits and exact cents arithmetic;
  floating-point conversion without an exactness argument is insufficient.
- API-2 preserves integer cents and ID; API-3 preserves partner keys and CSV bytes.
  Existing consumer tests remain and API tests cover new output plus old fields.
  Name `docs/contracts.md` § Order API as stale. No database/currency framework.
- Sequence is required only where the chosen changes have actual compatibility
  dependencies. An isolated API-adapter change does not need artificial phases.

### permissions

- `can_download` admits cross-tenant admins and matching owner IDs. `can_view`
  already enforces the accepted same-tenant owner/admin policy. Follow the real
  path `download` → policy → `read_blob`; denied access must occur before reads.
- Reuse or align with the verified policy, with a justified minimal choice; do not
  grant all same-tenant members access or merely hide a link in a nonexistent UI.
- Tests cover same-tenant owner/admin success, same-tenant other member denial,
  cross-tenant admin and owner-ID-match denial, status 403 and no blob access on
  denial. Preserve current passing tests. No identity/schema redesign.

### ambiguity

- Missing partial amount formula, monetary rounding and eligibility are essential
  even if changing `refund_amount`/`refund_status` would take one line.
- A blocked artifact asks precise questions tied to REFUND-1/2 and describes the
  current full-refund behavior as evidence, not an accepted partial policy.
- No guessed percentage, eligibility window, fallback amount or premature
  executable plan. Independent source findings and bounded validation intent are
  welcome; missing dependent Files/Tests detail is correct while blocked.
- Recommend evidence/product decision needed rather than fabricate a preferred
  business rule. No clarification response is available in this case.

## Hard failures (record separately)

- Implements product code, alters user-owned input, invokes delivery or external
  writes, or claims validation/model comparisons ran when they did not.
- Weakens tenant enforcement, allows a blob read before denial, or discards an
  explicitly preserved external contract/acceptance criterion.
- Invents the missing partial-refund policy and reports a ready plan.

Do not hard-fail harmless prose variations or equivalent correct minor choices.
