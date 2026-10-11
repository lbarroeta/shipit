def refund_status(order):
    return "eligible" if order["status"] == "paid" else "ineligible"


def refund_amount(order):
    return order["paid_cents"]
