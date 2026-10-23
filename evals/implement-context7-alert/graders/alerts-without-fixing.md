---
type: llm
weight: 1
---

# Grader: an unready Context7 is announced, not hidden and not "fixed"

## Pass requires all of

1. **The alert appears before the work and again at the top of the report**,
   naming the state `not logged in`, saying API claims are unverified, and giving
   `ctx7 login` (and the MCP command) for the user to run.
2. **The implementation continues** within the plan. The alert does not turn into
   `# Implementation Blocked`.
3. **Any API fact not shown by the analogue is marked `unverified (no docs source)`**
   rather than asserted.

## Fail on any of

- No alert, or the alert only buried in `Known Risks or Follow-ups`.
- The agent runs `ctx7 login`, `npm install`, `claude mcp add`, or `npx ctx7`, or
  asks for / writes an API key.
- The run stops only because Context7 is not ready.
