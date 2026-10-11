from app.orders import order_summary


def export_order(order):
    summary = order_summary(order)
    return f'{summary["id"]},{summary["total_cents"]}'
