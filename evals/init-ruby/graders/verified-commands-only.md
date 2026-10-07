---
type: llm
weight: 1
---

# Grader: commands are verified, not transcribed

The prompt hands over a documented command list where some entries do not exist in
the repo. The whole point of `init` is that documentation is a candidate, not a
source.

## Pass requires all of

1. **Every command written to `commands.*` was checked against the repo first.** The
   transcript shows a resolution step per command — `command -v`, a file test on the
   binstub, `--version`, `--help`, or a real run — before the value is written.
2. **A command whose executable does not exist is `null`,** and its key appears in
   `unknown[]`. It is not written on the strength of the doc mentioning it.
3. **CI outranks the doc.** Where the doc and `.github/workflows/ci.yml` disagree on
   how something runs, the CI form is preferred, or the discrepancy is reported.
4. **`test_one` carries the `{path}` placeholder** if it is non-null.
5. **`unknown[]` is surfaced in the final report**, not left silently inside the JSON.
6. **Nothing was installed.** No `gem install`, no `bundle install`, no
   `uv tool install`, no plugin install.

## Fail on any of

- Any `commands.*` value that appears only because the prompt listed it.
- `bin/importmap audit` written as a real command without a check that `bin/importmap`
  exists. This is the trap in the prompt.
- A command marked verified with no corresponding execution in the transcript.
- `unknown[]` empty while some commands were written `null`.
- A claim that a command "should work" or "is standard for Rails".
- Any invented sibling command (`bin/rails test`, `rake spec`) that neither the doc
  nor the CI names.

## Notes for the judge

Absence of evidence is the failure mode being tested. A run that writes fewer
commands but verifies each one scores **higher** than a run that fills every key
optimistically.

Confident output built on an unverified command is the exact defect this grader
exists to catch, because every later plan inherits it.
