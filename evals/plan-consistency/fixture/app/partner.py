from app.orders import order_summary


def partner_payload(order):
    return order_summary(order)
