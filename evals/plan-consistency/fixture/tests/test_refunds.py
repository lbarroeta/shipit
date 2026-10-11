import unittest
from app.refunds import refund_amount, refund_status


class RefundTests(unittest.TestCase):
    def test_paid_order_is_eligible(self):
        order = {"status": "paid", "paid_cents": 1000}
        self.assertEqual(refund_status(order), "eligible")
        self.assertEqual(refund_amount(order), 1000)
