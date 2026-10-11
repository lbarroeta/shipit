def can_download(actor, document):
    return actor["role"] == "admin" or actor["id"] == document["owner_id"]


def can_view(actor, document):
    return actor["tenant_id"] == document["tenant_id"] and (
        actor["role"] == "admin" or actor["id"] == document["owner_id"]
    )
