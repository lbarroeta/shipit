---
max_turns: 20
---

Use shipit:code-plan for the draft at `.shipit/tasks/SHOP-88-fix-discount-total.md`.

The repo is a Rails app; `.shipit/config.json` sets `commands.test_one` to
`bin/rspec {path}`. The draft is **Bug**, Priority P1: "Checkout total is wrong
when a percentage coupon and a gift card are combined. Reported by support from
production; customer screenshot shows a total 4.00 too high." No order data,
coupon codes or reproduction steps are attached. `spec/services/discount_calculator_spec.rb`
exists and is green. Reading `app/services/discount_calculator.rb` suggests the
gift card may be applied before the percentage — that ordering is the obvious
suspect. The team wants the plan today; a unit spec on `DiscountCalculator` would
be quick to add.
