from app.policy import can_download


def download(actor, document, read_blob):
    if not can_download(actor, document):
        return {"status": 403}
    return {"status": 200, "body": read_blob(document["blob_key"])}
