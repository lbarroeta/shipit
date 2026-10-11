import unittest
from app.api import get_order
from app.export import export_order
from app.partner import partner_payload


class OrderTests(unittest.TestCase):
    def setUp(self):
        self.order = {"id": 7, "total_cents": 1200}

    def test_api_amount(self):
        self.assertEqual(get_order(self.order)["body"]["total_cents"], 1200)

    def test_csv_contract(self):
        self.assertEqual(export_order(self.order), "7,1200")

    def test_partner_keys(self):
        self.assertEqual(set(partner_payload(self.order)), {"id", "total_cents"})
