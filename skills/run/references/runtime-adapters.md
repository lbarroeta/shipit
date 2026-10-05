# Native subagent adapters

Choose by the hosting runtime, not the tracker. Claude Code uses the `anthropic`
routes; local Codex uses `openai`. Do not invoke another provider's CLI or use
user-owned chat creation as a substitute. Load only the relevant section.

The default route pairs are in `../assets/models.json`. The helper's `routes`
command applies `.sdd/config.json` overrides at
`run.models.<anthropic|openai>.<plan|implement|handoff>`, each a complete
`{"model": "...", "effort": "..."}` pair. Do not modify global session settings.
Check availability and restrictions through the runtime's exposed capabilities;
if access cannot be proven until spawn, the spawn failure is a blocker, not
permission to switch model. Recheck returned routes after Git preparation because
pulling `main` may update the repo contract.

## Claude Code

The plugin ships native definitions under its root `agents/`:

| Stage | Scoped agent | Default model | Effort |
| --- | --- | --- | --- |
| plan | `shipit:run-planner` | `claude-opus-5-5` | `high` |
| implement | `shipit:run-builder` | `claude-sonnet-5-5` | `high` |
| handoff | `shipit:run-delivery` | `claude-sonnet-5-5` | `high` |

Use the native Agent tool with the corresponding scoped subagent type. Give it
the absolute checkout, skill path and message contract; each definition instructs
the child to read that skill. Read the selected definition before dispatch and
check its model/effort against the resolved route. Explicit local overrides need
a matching native agent definition with the requested model and `effort`; if the
runtime cannot apply that pair, stop rather than use the packaged default.

Wait for each native result before starting the dependent stage. Resume/send a
follow-up through the native agent controls, keeping the same configured pair.
If those controls are unavailable, wait for termination and dispatch a fresh child
with its saved artifacts. Confirm model/effort from runtime task metadata when
exposed (Claude Code `/tasks` displays it); environment/organization overrides may
substitute or cap values. Do not ask the model to certify its own identity.

## Local Codex (app, CLI, IDE)

Use the exposed native spawn, message/follow-up and wait controls. Depending on
the host these are `spawn_agent` / `send_message` / `wait` or the collaboration
tools. Pass the route's `model` and `reasoning_effort` explicitly on spawn. With
`collaboration.spawn_agent`, use `fork_turns: "none"`: a full-history fork inherits
the parent model and cannot take overrides. Supply the complete message contract
instead. This skill explicitly requests delegation and its route overrides.

Wait for final completion, not merely commentary, before checkpointing. If a host
uses named TOML agents instead of per-spawn overrides, select an existing custom
agent whose `model` and `model_reasoning_effort` exactly match the route. Do not
silently install or rewrite `.codex/agents/`; report the missing adapter capability.
No inherited parent-model fallback, no new sidebar chats. Capture effective
settings from returned runtime metadata when available.

Other runtimes, including OpenCode, are unsupported for this pipeline; existing
individual shipit skills remain usable there.

Official references: [Claude Code subagents](https://code.claude.com/docs/en/sub-agents),
[Claude Code effort](https://code.claude.com/docs/en/model-config#adjust-effort-level),
[Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).
