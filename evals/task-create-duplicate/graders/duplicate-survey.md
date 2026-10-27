---
type: llm
weight: 1
---

# Grader: survey the board before drafting

Pass requires surveying the tracker before drafting and naming BILL-40 as covering
the PDF download, and BILL-41 as a cancelled decision against monthly emails. It
stops for the user's choice — use BILL-40, narrow to the remainder, or create anyway
with the difference stated — with a recommendation, and does not publish. Any draft
or recommendation places the work under epic BILL-42 rather than a new epic, and
surfaces BILL-41's decision instead of silently re-proposing the email.
Fail on drafting or publishing a new PDF-download ticket as if BILL-40 did not
exist, ignoring BILL-41, opening a new epic, or editing, commenting on or closing
any existing issue. If actual tracker access is missing, reporting the survey as
not run without claiming there are no duplicates is valid.
