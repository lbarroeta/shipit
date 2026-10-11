import unittest
from app.download import download


class DownloadTests(unittest.TestCase):
    def test_owner_can_read(self):
        actor = {"id": 1, "role": "member", "tenant_id": "a"}
        document = {"owner_id": 1, "tenant_id": "a", "blob_key": "report"}
        self.assertEqual(download(actor, document, lambda key: key)["status"], 200)

    def test_other_member_denied_before_read(self):
        actor = {"id": 2, "role": "member", "tenant_id": "a"}
        document = {"owner_id": 1, "tenant_id": "a", "blob_key": "report"}
        reads = []
        self.assertEqual(download(actor, document, reads.append)["status"], 403)
        self.assertEqual(reads, [])
