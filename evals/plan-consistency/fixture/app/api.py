from app.orders import order_summary


def get_order(order):
    return {"status": 200, "body": order_summary(order)}
