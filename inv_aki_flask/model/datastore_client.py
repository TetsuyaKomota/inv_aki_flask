from datetime import datetime, timedelta

from google.cloud import datastore


class InvalidKeyException(Exception):
    pass


class SessionNotExistsException(Exception):
    pass


class DataStoreClient:
    KIND_SESSION_LIST = "SessionList"
    KIND_SESSION = "Session"
    KIND_MESSAGE = "Message"

    KEYID_SESSION_LIST = "v0.0.1"  # 全件検索用

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

    def create_session_entity(self, sessionid, work, keyword):
        expiration = datetime.now() + timedelta(days=1)
        self._upsert(
            kind=DataStoreClient.KIND_SESSION,
            keyid=sessionid,
            parent_kind=DataStoreClient.KIND_SESSION_LIST,
            parent_keyid=DataStoreClient.KEYID_SESSION_LIST,
            work=work,
            keyword=keyword,
            public=False,
            expiration=expiration,
        )

    def update_session_entity(
        self, sessionid, *, expire_at=None, public=None, rank=None, judge=None
    ):
        session = self._select(
            kind=DataStoreClient.KIND_SESSION,
            keyid=sessionid,
            parent_kind=DataStoreClient.KIND_SESSION_LIST,
            parent_keyid=DataStoreClient.KEYID_SESSION_LIST,
        )
        if session is None:
            raise SessionNotExistsException("session が存在しません")
        if expire_at is not None:
            expiration = datetime.now() + timedelta(days=expire_at)
        else:
            expiration = None
        self._update(
            session, expiration=expiration, public=public, rank=rank, judge=judge
        )

    def create_message_entity(
        self,
        sessionid,
        messageid,
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
            question=question,
            answer=answer,
            reason1=reason1,
            reason2=reason2,
            reason3=reason3,
            expiration=expiration,
        )

    def update_message_expiration(self, message, expire_at):
        expiration = datetime.now() + timedelta(days=expire_at)
        self._update(message, expiration=expiration)

    def get_session(self, sessionid):
        return self._select(
            kind=DataStoreClient.KIND_SESSION,
            keyid=sessionid,
            parent_kind=DataStoreClient.KIND_SESSION_LIST,
            parent_keyid=DataStoreClient.KEYID_SESSION_LIST,
        )

    def get_messages(self, sessionid):
        return self._get_from_parent(
            kind=DataStoreClient.KIND_MESSAGE,
            parent_kind=DataStoreClient.KIND_SESSION,
            parent_keyid=sessionid,
        )

    def get_public_sessions(self):
        entities = self._get_from_parent(
            kind=DataStoreClient.KIND_SESSION,
            parent_kind=DataStoreClient.KIND_SESSION_LIST,
            parent_keyid=DataStoreClient.KEYID_SESSION_LIST,
        )

        # TODO たぶんここ query を使ったほうがリソースが節約できる
        entities = [e for e in entities if e.get("public", False)]

        # TODO update 側修正してたぶんこれいらなくなる
        entities = [e for e in entities if e.get("keyword", "") != ""]

        # ランク順かつ，同ランクなら新しい順にソート
        entities = sorted(
            entities, key=lambda x: (-x["rank"], x["expiration"]), reverse=True
        )

        return entities


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
