# Tracker Writes — status by default, comments and creation opt-in

**Do not read this file unless `handoff.allow` in `.sdd/config.json` enables a
tracker write.** The default includes `tracker_status`: read the transition
rules and the configured adapter. Comments and issue creation remain opt-in.

Which capability unlocks which section:

| `handoff.allow` entry | What this file supplies |
| --- | --- |
| `tracker_comment` | the `Comment` lines, and the universal comment rules below |
| `tracker_status` | the `Transitions` and `Terminal` lines |
| `issue_create` | the `### Create` subsection, plus `task` mode in `SKILL.md` |

Branch naming and PR issue-linking are **not** here — they are always allowed and
live in `tracker-adapters.md`. Read only the section for `tracker.adapter`; the
other adapters are noise.

## Universal rules

For `plan` and `implementation` status writes, first verify the published PR is
ready for review. Resolve the linked issue to the configured repository/project;
no issue or adapter `none` → `n/a`. Enumerate its own workflow and match `In Review`
or an unambiguous review equivalent, then update and read back. Already at review
or later → no write. Missing/ambiguous target, unavailable access or failed
read-back → `partial`, preserving completed commit/push/PR effects for retry.
A missing or draft PR never advances the card.

- **Read the current status before writing a transition.** A blind "move to review"
  can drag a finished issue backwards.
- **Never move backwards.** Terminal and in-flight-past-this-point states are listed
  per adapter. When in doubt, leave the status alone and say so.
- **Enumerate, never hardcode.** States, transitions, issue types, teams, labels:
  ask the tracker what it has and match by name. An id copied from another
  workspace writes to the wrong place, silently.
- An unavailable tracker is `partial`, never a silent skip. Name the failing call.
- **Name the missing capability, not the tool.** "Linear MCP not connected" is
  actionable; "tracker unavailable" is not.
- **The draft's type maps to whatever this tracker calls it** — an issue type, a
  story type, or a label. No native concept → a label, and only one that already
  exists. Never introduce a `bug`/`feature` label scheme a repo does not have; say
  the type went unmapped instead.
- **Priority and size go to fields, not prose.** The draft's `Priority: P0–P3` and
  `Size: XS–XL` map to the tracker's own priority and size/estimate fields, matched
  by name per adapter below. `tracker.create.fields` decides which field: a string
  is the name to match, `null` means the tracker has none — skip it and report
  unmapped, without enumerating — and `"unknown"` or an absent block means use the
  adapter's default name from the tables below. Never create a field, an option, or a `priority:*` /
  `size:*` label. A tracker without a match → the value stays in the draft, the
  issue is still created, the body retains its complete typed contract, and the report says `priority unmapped` / `size unmapped`.
  A failure setting the field after the issue exists is `partial`, not a reason to
  delete the issue: the `## Created` line for that issue gets `— pending: <field or relation>`,
  and a re-run retries exactly those fields (see `task` mode in `SKILL.md`).
- **A comment carries the QA steps and the PR link. Nothing else.** No summary, no
  validation result, no file list, no diff narration, no restating the ticket back
  to the person who wrote it. The PR is where the change is described; the ticket is
  where someone learns how to verify it.
- QA steps are copied **verbatim**, into a tracker comment or into a created
  issue's body. They were written for someone who does not read code, so they are
  never shortened.
- **Nothing to say → no comment.** No QA steps in the report, or `review` mode where
  the thread replies are already the record → skip the write and report the line as
  `n/a`, not as `blocked`. An empty comment is worse than none.

## Publishing contract — all adapters

Create bodies from the complete standalone task/child contract, not an index row.
Always preserve explicit Problem, Goal, scope/boundaries, AC IDs, scenario details
and unblock conditions. Formatting conversions are allowed when required by the
provider; content loss is not. Exclude source/date/shape draft metadata and the
Created ledger; retain Type/Priority/Size in prose when native mapping is absent.

Inspect usable create/update, hierarchy and dependency read/write capabilities in
the current session. Provider support alone does not imply the connector exposes
it. Parent, blocking relation and advisory order have different meanings. Report
verified native relations separately from prose references. Unsupported concepts
stay in prose with IDs/URLs and exact manual steps; do not fake links or invent
labels/fields to emulate them. Failures after creation are partial, ledgered as
pending relations, read back/reconciled on retry without duplicate issues.
`dependency:<reference>` may name a local child or an existing external ID/URL;
resolve the latter live, never create the external prerequisite. Capability known
absent before an attempt is unsupported/manual, not pending. A supported operation
that fails (including permission denial) is partial/pending with its exact error;
retry after access is fixed. Never silently downgrade a failed write to success.

## `linear`

**Mechanism:** the Linear MCP server, in this session. The capabilities used are
list teams, list workflow states, get issue, create issue, create comment, and
update issue status. Not connected → stop and report which of those was needed.
There is no CLI fallback; do not construct API calls by hand.

Comment, `plan` mode:

```text
Plan: `<plan path>` — execute with /shipit:implement.
PR: <pr-url>
QA: UI verification required for <named flows>
```

No UI work → `QA: Backend only. UI verification not applicable.`

Comment, `implementation` mode: the QA steps verbatim, then the PR link. No
comment in `review` mode.

Transitions: `plan` and `implementation` modes → `In Review` (or the team's
unambiguous review equivalent), only after a ready PR is delivered. None in
review mode.

Already at review / do not downgrade: `In Review`, `Code Review`, `Ready for QA`,
`Accepted`, `Deployed`, `Canceled`, `Duplicate`, or that workspace's equivalents.

### Create

Target: `tracker.create.team` is required — Linear issues belong to a team, not to a
workspace. `tracker.create.project` is optional and attaches the issue to a project.

| Draft field | Goes to |
| --- | --- |
| Title | issue title |
| Type | the team's `Bug` / `Feature` / `Chore` label — Linear has no issue types. Absent → leave unmapped and say so |
| Problem + Goal + What to do + Acceptance criteria + QA / validation scenarios + Out of scope + Dependencies | issue description, markdown as written |
| `Labels` | labels, only ones the team already has |
| Priority | the numeric `priority`: `P0` → `1`, `P1` → `2`, `P2` → `3`, `P3` → `4`. Set the number, never match a name — the app shows `3` as `Medium` and the API calls it `Normal` |
| Size | estimate, only when the team's estimate scale is T-shirt (`XS`–`XL` by name). Another scale, or estimates off → size unmapped |

State: `tracker.create.initial_state`, matched by name against the team's workflow
states. No match → use the team's default `Backlog`-type state and say so.

Epic: a parent issue with sub-issues. Create the parent, then each child with
`parentId` set to it. Linear has no separate epic type — `tracker.create.epic_kind`
is `parent-issue`. Verify parent assignment is exposed by the connected tool; a
connected server may create issues without supporting relation writes. A configured
existing Project groups issues but is not itself a parent issue or blocking link;
do not create a new project implicitly. If configuration calls for a new project,
report the separate unsupported/unauthorized capability rather than substitute it.

Dependencies: use the provider's blocking/blocked-by relation only when the connected
capability supports it. Attach after endpoints exist, verify direction and read
back. Missing relation writes → keep explicit ID references and unblock conditions
in the body, report unsupported/manual native linking. Parenthood never becomes a blocking link.
See [Linear issue relations](https://linear.app/docs/issue-relations) and
[parent/sub-issues](https://linear.app/docs/parent-and-sub-issues).

## `github-issues`

**Mechanism:** the `gh` CLI. The only adapter that is not an MCP.
`gh auth status` failing is the same class of failure as a disconnected MCP: report
it, create nothing.

Link the issue from the PR body so GitHub closes it on merge — `Closes #<n>` when
the merge should close it, a bare `#<n>` reference when it should not. Getting this
wrong closes an issue that still has work left.

Comment: `gh issue comment <n> --body <...>`, same content as the Linear sections.
No comment in `review` mode.

Transitions: GitHub issues have open/closed and optionally a Project field.

- Never close an issue from `handoff`. Merging does that, or a human does.
- A Project status field exists → advance it the same way as Linear, via
  `gh project item-edit`.
- No Project → labels only if the repo already uses them for state. Do not
  introduce a label scheme.

Terminal: `closed`.

### Create

`gh issue create --title <...> --body <...>`, plus `--label` per label that already
exists in the repo (`gh label list` first — `gh` fails the whole call on an unknown
label). Never `--project`: the Project is attached afterwards, below, because that
is the only way to get the item id the fields need. The body carries
`Problem`, `Goal`, `What to do`, `Acceptance criteria`, `QA / validation
scenarios`, `Out of scope` and `Dependencies` as written.

Priority and size: GitHub issues have neither — they live on a Project as
single-select fields, by default named `Priority` (`P0`…) and `Size` (`XS`…), which
is GitHub's own project template; `tracker.create.fields` overrides the names.

`tracker.create.project` names the Project as `<owner>/<number>` — the owner is the
Project's, which need not be the repo's: a user Project can be linked to an
organization repo. With it set:

1. `gh project view <number> --owner <owner> --format json` → the node id.
2. `gh project field-list <number> --owner <owner> --format json` → the field ids
   for the names in `tracker.create.fields`, and the option id whose name matches
   the draft's value.
3. Create the issue, then
   `gh project item-add <number> --owner <owner> --url <issue-url> --format json` →
   the item id.
4. `gh project item-edit --id <item-id> --project-id <node-id> --field-id <field-id>
   --single-select-option-id <option-id>`, once per field.

A `create.project` that is a bare title — set by hand, or written before this format
— is resolved against the Projects linked to the repo (`detection-recipes.md § 7b`);
no match or more than one → report it and treat both fields as unmapped.

No project, no field by that name, or no matching option → that value is unmapped.
Never fall back to a label, whatever the repo has. A token without the `project`
scope fails step 1 — report `gh auth refresh -s project` as the fix, create the
issue anyway, and mark priority and size unmapped.

Type: a native issue type if the repo and usable capability expose one; enumerate
and match it first. Otherwise the repo's own label — `bug`, `enhancement`, `chore`, or whatever it uses.
`gh label list` decides; a repo without a matching label gets none, and the report
says the type went unmapped. No supported native/label match → keep Type in the body and report unmapped.

Epic: GitHub supports native sub-issues and blocking dependencies. Inspect the
available authenticated capabilities before publishing; basic `gh issue create`
does not itself attach these relations. Use verified GitHub REST/GraphQL operations
through `gh api` when available and authorized. Native hierarchy → parent first,
then attach each child. Native blocked-by relations → create endpoints first,
then link the dependent to its prerequisite, never reversing direction.
Enumerate/read back existing relations on retry.

Native relation capability absent or permission denied → preserve explicit parent
and dependency references in the issue bodies and report unsupported/manual or a
failed pending write. If the configured fallback is `task-list`, create children
first and include their actual links in the parent task list; report it as a text
index, not native hierarchy. Never claim the task list created a native link.

Official capability references (verify operation availability, IDs and permissions
rather than copying a request shape from another provider):
- [GitHub sub-issues REST API](https://docs.github.com/en/rest/issues/sub-issues)
- [GitHub issue dependencies REST API](https://docs.github.com/en/rest/issues/issue-dependencies)

State: issues open on creation. `tracker.create.initial_state` applies only when a
Project status field exists; otherwise it is `null` and nothing is set.

## `jira`

> **Written from the API contract, not verified against a live instance.** Treat the
> exact field and transition names as unconfirmed: list the available transitions
> before choosing one, and report if they do not match what is described here.

**Mechanism:** the Jira MCP server, in this session. Capabilities used: list issue
types, list transitions, get issue, create issue, add comment, transition issue.
Not connected → report which one was needed.

Comment: the same content, on the issue. No comment in `review` mode.

Transitions: Jira transitions are per-workflow and named per project. **Enumerate
first**, then pick by name, never by a hardcoded id:

1. List the available transitions for the issue.
2. Match on name (`In Progress`, `In Review`, `Done`).
3. No match → leave the status alone and report the available options.

Terminal: anything in a `Done` status category.

### Create

Target: `tracker.create.project` is required — the project key. Issue types are
per-project, so **enumerate them before choosing**: a project without a `Task` type,
or with a renamed one, is common and hardcoding the name fails the create call.

| Draft field | Goes to |
| --- | --- |
| Title | summary |
| Type | the issue type — `Bug`, `Story`/`Task`, `Task` for a chore. **Enumerate the project's types and match by name**; they are renamed often |
| Problem + Goal + What to do + Acceptance criteria + QA / validation scenarios + Out of scope + Dependencies | description |
| `Labels` | labels |
| Priority | the `priority` field. Enumerate the instance's priorities and match: `P0` → `Highest` (or `Blocker`), `P1` → `High`, `P2` → `Medium`, `P3` → `Low`. A scheme already named `P0`–`P3` matches directly |
| Size | a field named `Size` or `T-Shirt Size` when the create metadata offers one, matched by option name. None → size unmapped; never convert to story points |

Epic: the project's `Epic` issue type when it has one, with children linked by the
parent field (`parent` on modern instances, the epic-link custom field on older
ones — read what the create metadata offers rather than assuming). No `Epic` type
available → report it and preserve parent references in flat issue bodies;
never claim native hierarchy. If description expects rich document data instead
of markdown, convert formatting while preserving all content and scenario tables;
do not send unsupported markdown blindly.

Dependencies: enumerate available issue link types and their inward/outward
semantics. A native blocks/is-blocked-by link needs linking enabled, permission and
a usable connector operation; verify the dependent's blocked-by endpoint after
creation. Do not infer direction from a hardcoded name or replace it with parent.
Unsupported linking → body references/unblock conditions plus a manual report.
See [Jira link configuration](https://support.atlassian.com/jira-cloud-administration/docs/configure-issue-linking/).

State: a new issue lands in its workflow's first status. Setting a different
`initial_state` needs a transition immediately after creation — do it only when
`tracker.create.initial_state` is set and the transition is available by name.

## `shortcut`

**Mechanism:** the Shortcut MCP server, in this session. Capabilities used: list
workflows and workflow states, get story, create story, create epic, create comment,
update story state. Not connected → report which one was needed.

Comment: a comment on the story, same content as the Linear sections. No comment
in `review` mode.

Transitions: workflow states belong to a workflow, and a team may have its own.
Enumerate the states of the story's workflow and match by name — never by id, which
differs per workspace. Shortcut also types each state as `unstarted`, `started` or
`done`; use the type when the name does not match.

- `plan` and `implementation` modes → `In Review` or the unambiguous review
  state, e.g. `Ready for Review`, after a ready PR is delivered. The `started`
  type alone does not identify review; never select an arbitrary started state.
- `review` mode → none.

Terminal / do not downgrade: any state typed `done`, plus anything already `started`
past this point. Archived stories are terminal too — never write to one.

### Create

Target: `tracker.create.team` is the group or workflow the story belongs to.
`tracker.create.project` is optional.

| Draft field | Goes to |
| --- | --- |
| Title | story name |
| Type | story type, natively: `bug`, `feature`, `chore`. The one adapter where the mapping is exact |
| Problem + Goal + What to do + Acceptance criteria + QA / validation scenarios + Out of scope + Dependencies | description |
| `Labels` | labels |
| Priority | the workspace's `Priority` custom field when enabled: `P0` → `Highest`, `P1` → `High`, `P2` → `Medium`, `P3` → `Low`, or the same names when it already uses `P0`–`P3`. Not enabled → priority unmapped |
| Size | a custom field named `Size` when one exists, matched by option name. Estimates are points — never convert a T-shirt size into them; none → size unmapped |

Epic: Shortcut has a native Epic. Create the epic first, then each story with
`epic_id` set to it. `tracker.create.epic_kind` is `epic`.

State: `tracker.create.initial_state`, matched by name in the target workflow. No
match → the workflow's default unstarted state, and say so.

## `none`

**Mechanism:** none. Delivery is git and the PR host only.

- Branch from `.sdd/conventions.md`, else ask.
- No comment step. Everything the tracker comment would have carried goes in the PR
  body instead — including the QA steps.
- No status step.
- Report the tracker lines as `n/a (adapter: none)`, not as `blocked`. Absence of a
  tracker is a configuration, not a failure.

### Create

Nothing is created. The `task-create` draft on disk is the deliverable: report its path,
report the tracker line as `n/a (adapter: none)`, and leave `## Created` empty so a
later run — once an adapter is configured — still works.

This is the default when detection was ambiguous. A wrong adapter writes to the
wrong place, so `none` is the safe landing spot — and `/shipit:init` can be re-run
once the right one is known.
