from typing import Callable

from google.cloud import datastore


def validate_key(f: Callable) -> Callable:
    def _f(self, kind="", keyid="", parent_kind="", parent_keyid="", **properties):
        if (parent_kind == "") != (parent_keyid == ""):
            raise InvalidKeyException(
                "\n".join(
                    [
                        "parent_kind, parent_keyid の一方が指定されていません: ",
                        f"parent_kind={parent_kind}, parent_keyid={parent_keyid}",
                    ]
                )
            )

        if parent_kind != "" and parent_keyid != "":
            key = self.client.key(parent_kind, parent_keyid, kind, keyid)
        else:
            key = self.client.key(kind, keyid)

        return f(self, key=key, **properties)

    return _f


class InvalidKeyException(Exception):
    pass


class DataStoreClient:
    def __init__(self):
        self.client = datastore.Client()

    @validate_key
    def _upsert(self, key, **properties):
        entity = datastore.Entity(key)
        entity.update(properties)
        self.client.put(entity)

    @validate_key
    def _select(self, key):
        return self.client.get(key)

    @validate_key
    def _delete(self, key):
        return self.client.delete(key)

    def _update(self, entity, **properties):
        for k, v in properties.items():
            if v is not None:
                entity[k] = v
        self.client.put(entity)

    def _get_from_parent(self, kind, parent_kind, parent_keyid):
        ancestor_key = self.client.key(parent_kind, parent_keyid)
        query = self.client.query(kind=kind, ancestor=ancestor_key)
        return list(query.fetch())
