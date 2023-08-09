from datetime import datetime, timedelta

from google.cloud import datastore


class InvalidKeyException(Exception):
    pass


class DataStoreClient:
    KIND_SESSION = "Session"
    KIND_MESSAGE = "Message"

    def __init__(self):
        self.client = datastore.Client()

    def validate_key(f):
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

    @validate_key
    def _upsert(self, key, **properties):
        task = datastore.Entity(key)
        task.update(properties)
        self.client.put(task)

    @validate_key
    def _select(self, key):
        return self.client.get(key)

    @validate_key
    def _delete(self, key):
        return self.client.delete(key)

    def _get_from_parent(self, kind, parent_kind, parent_keyid):
        ancestor_key = self.client.key(parent_kind, parent_keyid)
        query = self.client.query(kind=kind, ancestor=ancestor_key)
        return list(query.fetch())

    def create_session_entity(self, sessionid):
        expiration = datetime.now() + timedelta(days=1)
        self._upsert(
            kind=DataStoreClient.KIND_SESSION, keyid=sessionid, expiration=expiration
        )

    def create_message_entity(
        self,
        sessionid,
        messageid,
        work,
        keyword,
        question,
        answer,
        reason1,
        reason2,
        reason3,
    ):
        expiration = datetime.now() + timedelta(days=1)

        self._upsert(
            kind=DataStoreClient.KIND_MESSAGE,
            keyid=messageid,
            parent_kind=DataStoreClient.KIND_SESSION,
            parent_keyid=sessionid,
            work=work,
            keyword=keyword,
            question=question,
            answer=answer,
            reason1=reason1,
            reason2=reason2,
            reason3=reason3,
            expiration=expiration,
        )

    def get_messages(self, sessionid):
        return self._get_from_parent(
            kind=DataStoreClient.KIND_MESSAGE,
            parent_kind=DataStoreClient.KIND_SESSION,
            parent_keyid=sessionid,
        )


client = DataStoreClient()

if __name__ == "__main__":
    client.create_session_entity("session_1")
    client.create_message_entity(
        "session_1",
        "message_1",
        "ワンピース",
        "ルフィ",
        "主人公ですか？",
        "当てはまる",
        "主人公だから",
        "格好いいから",
        "なんとなく",
    )
    client.create_message_entity(
        "session_1",
        "message_2",
        "ワンピース",
        "ルフィ",
        "男性キャラクターですか？",
        "当てはまる",
        "一人称が俺だから",
        "強いから",
        "なんとなく",
    )

    print(client.get_messages("session_1"))
