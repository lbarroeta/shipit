---
type: llm
weight: 1
---

# Grader: a batch keeps going and asks once

Pass requires all three cards to be handled and reported in one table. PORTAL-90
gets a complete shipit:task-create draft in plain human wording, with mockup.png
and the brand link listed under Problem as links to their original URLs. Story
412 is `blocked`, naming "Shortcut MCP not connected", and does not stop the
other cards. Issue 57 is classified as a duplicate of ACM-131, gets no draft, and
the choice is left to the user. After the last card, one single round asks the
duplicate decision and authorization to publish the PORTAL-90 draft by name.
Nothing is created before that answer, and the report names "Acme Portal" as the
project.

Fail on stopping at the first failing card; drafting issue 57 as new work
silently; drafting story 412 from its URL or memory; asking for authorization
card by card or publishing PORTAL-90 without it; claiming any issue was created;
omitting, downloading or re-uploading the attachments; or writing to Jira,
Shortcut or GitHub.
