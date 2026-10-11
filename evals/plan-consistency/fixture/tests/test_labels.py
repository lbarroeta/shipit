import unittest
from app.labels import normalize_label


class LabelTests(unittest.TestCase):
    def test_normalizes_case_and_edges(self):
        self.assertEqual(normalize_label("  Cat  "), "cat")
