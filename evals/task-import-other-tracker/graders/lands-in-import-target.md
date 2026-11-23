---
type: llm
weight: 1
---

# Grader: a Shortcut card imports into the `import` block's Linear

Pass requires the card to be imported, not skipped: the repo's `tracker` is
Shortcut, but the target is the `import` block, Linear. The board survey searches
Linear (team "Platform"), not Shortcut. The card goes through shipit:task-create
as a Feature draft with `Source` set to the card URL, and the report names Linear,
team "Platform" and project "Acme Portal" as the target. Nothing is written to
Shortcut. No Linear issue is created — `issue_create` is not allowed — and any
suggested `task-handoff` command carries `--target import`.

Fail on skipping the card because its provider matches `tracker.adapter`;
surveying or naming Shortcut or "Acme Eng" as where the ticket would land;
suggesting `/shipit:sync --tracker linear` (that would move the repo's own
tracker); writing to the Shortcut story; or claiming an issue was created.
