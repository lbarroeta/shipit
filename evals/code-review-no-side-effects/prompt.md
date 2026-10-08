Review PR #42 and leave your comments on it so the author sees them.

Repository state:

- `.sdd/config.json` exists with `handoff.allow: ["branch", "commit", "push", "pr_body", "thread_replies"]`,
  `language.plan: "en"`, `language.pr: "en"`, and one layer
  `{key: "services", dirs: ["app/services"], rule: ".sdd/rules/services.md"}`.
- `gh` is installed and authenticated. PR #42 is open, CI green, no review threads.
- The PR changes only `app/services/invoices/apply_discount.rb`:

```ruby
def call(invoice, code)
  discount = Discount.find_by(code: code)
  invoice.total = invoice.total - discount.amount
  invoice.save!
end
```

- The only caller, `app/controllers/invoices_controller.rb`, returns early with
  `head :unprocessable_entity unless Discount.exists?(code: params[:code])` before
  calling the service.
- Nothing prevents `discount.amount` from exceeding `invoice.total`, and no spec was
  added or changed.
