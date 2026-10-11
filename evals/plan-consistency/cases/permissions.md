Use the supplied shipit:code-plan skill to plan this request. Write the plan locally;
do not implement it, run handoff, or contact a tracker. Use only this fixture repo
and the supplied plugin snapshot. Planning language: English.

Goal: fix document downloads so tenant boundaries are enforced at the server.
Accepted policy is already in docs/contracts.md; preserve it.

- AUTH-1: same-tenant owner and same-tenant admin may download.
- AUTH-2: different-tenant actors are denied, including admins and actors whose ID matches owner_id.
- AUTH-3: same-tenant non-owner members are denied; all denial paths return 403 without reading the blob.

No UI, identity provider, schema or unrelated policy redesign. Plan the complete
entry-point-to-storage authorization behavior, using the local pattern if it fits.
