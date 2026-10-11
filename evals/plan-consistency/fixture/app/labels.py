def normalize_label(value):
    return value.strip().lower()


def search_key(value):
    return " ".join(value.split()).casefold()
