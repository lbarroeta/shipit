---
max_turns: 20
---

Use shipit:pr-fix on PR #87.

Repository state: Rails 7.1 app, `.shipit/config.json` has `stack.frameworks:
["rails"]`, `tests.framework: "rspec"`, `ci.required_jobs: ["rspec"]`. The
current branch is the PR's head `feat/invoice-export`, clean. `gh` returns:

- `gh pr view`: open, base `main`, `mergeable: CONFLICTING`,
  `mergeStateStatus: DIRTY`. `git merge-tree` against `origin/main` lists
  `config/routes.rb`.
- Thread A on `app/models/invoice.rb:42` (`total_cents = line_items.sum(&:amount_cents)`):
  "This loads every line item into memory; use `line_items.sum(:amount_cents)`."
  The method is called from `InvoicesController#index` once per invoice.
- Thread B on `app/services/invoice_exporter.rb:18`
  (`invoice.customer.email`): "`customer` can be nil here, add a guard."
  `Invoice` has `belongs_to :customer` (required by default in Rails 5+), the
  `customer_id` column is `null: false`, and the exporter is only called with
  persisted invoices.
- Thread C: "Can we make the exporter pluggable so it also supports XML later?"
- `gh pr checks`: `rspec` failed, `danger` (optional) failed, `brakeman` pending.
  `rspec` log: `spec/services/invoice_exporter_spec.rb:31` —
  `expected "2024-01-05" got "2024-01-04"`. The exporter formats
  `invoice.issued_at.to_date` while the spec freezes time at
  `2024-01-05 01:00 +0100`. `danger` log: `Missing CHANGELOG entry`.
