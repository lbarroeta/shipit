Plan this ticket.

> **KOD-311 — Add a discount code field to checkout**
> A shopper can enter a discount code during checkout. Valid codes reduce the order
> total. Invalid codes show an inline error and leave the total unchanged.

Repository state:

- `.sdd/config.json` exists, with `worktree.enabled: true` and
  `worktree.root: "../worktrees/shop"`, and `tracker.adapter: "none"`.
- `git worktree list` reports two worktrees besides the main checkout:
  - `../worktrees/shop/kod-298` on branch `lb/kod-298-order-totals`
  - `../worktrees/shop/kod-305` on branch `lb/kod-305-checkout-copy`
- `../worktrees/shop/kod-298/.sdd/plans/kod-298-order-totals.md` has a `Files` table
  listing `app/models/order.rb` and `app/services/orders/calculate_total.rb`.
- `../worktrees/shop/kod-305/.sdd/plans/kod-305-checkout-copy.md` has a `Files` table
  listing `app/views/checkout/show.html.erb`.

Your change will need to touch the order total calculation and the checkout view.
