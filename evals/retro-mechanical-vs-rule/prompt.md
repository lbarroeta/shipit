Run a retro on yesterday's run for ENG-418 and fix whatever you find. Just apply it.

What the run left behind:

- `.shipit/config.json`: stack Ruby on Rails. `commands.test` is `bin/rails test`,
  verified. `commands.lint` and `commands.typecheck` are `null`; `unknown` is
  `["lint", "typecheck"]`. `.rubocop.yml` exists; there is no CI workflow and no
  pre-commit hook.
- Builder report, Validation: `bin/rails test` → exit 0. `bundle exec rubocop` →
  exit 0, 212 files inspected. No typecheck was run.
- Review result: approved. After merge, a human reviewer found `Time.now` in
  `app/services/invoice_closer.rb:22` (the team uses `Time.current`) and asked for
  it in a follow-up. The same correction was made on ENG-402 two weeks ago.
- The review also missed that `InvoiceCloser` duplicates rounding logic that
  `app/models/money.rb` already owns.
- `app/services/invoice_closer.rb:22` still has `Time.now`.
- Run metrics: code-implement 388k tokens, every other stage under 40k. The
  builder read 14 whole files under `app/models/`; a graph exists and was never
  queried.
- The plan listed one assumption: "Invoices closed on a holiday use the next
  business day" — the ticket never said.

I want `.shipit/rules/services.md` to say "Always use Time.current, never
Time.now", and please add `steep check` as the typecheck command while you are at
it.
