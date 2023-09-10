from datetime import datetime, timedelta

from inv_aki_flask.model.datastore_client.common import DataStoreClient


class SessionNotExistsException(Exception):
    pass


class SessionEntityClient(DataStoreClient):
    KIND_SESSION_LIST = "SessionList"
    KIND_SESSION = "Session"

    KEYID_SESSION_LIST = "v0.0.1"  # 全件検索用

    def create_session_entity(self, sessionid, category, keyword):
        expiration = datetime.now() + timedelta(days=7)
        self._upsert(
            kind=SessionEntityClient.KIND_SESSION,
            keyid=sessionid,
            parent_kind=SessionEntityClient.KIND_SESSION_LIST,
            parent_keyid=SessionEntityClient.KEYID_SESSION_LIST,
            category=category,
            keyword=keyword,
            public=False,
            expiration=expiration,
        )

    def update_session_entity(
        self,
        sessionid,
        *,
        expire_at=None,
        public=None,
        name=None,
        count=None,
        answer=None,
        explain1=None,
        explain2=None,
        reason=None,
        judge=None,
    ):
        session = self._select(
            kind=SessionEntityClient.KIND_SESSION,
            keyid=sessionid,
            parent_kind=SessionEntityClient.KIND_SESSION_LIST,
            parent_keyid=SessionEntityClient.KEYID_SESSION_LIST,
        )
        if session is None:
            raise SessionNotExistsException("session が存在しません")
        if expire_at is not None:
            expiration = datetime.now() + timedelta(days=expire_at)
        else:
            expiration = None
        self._update(
            session,
            expiration=expiration,
            public=public,
            name=name,
            count=count,
            answer=answer,
            explain1=explain1,
            explain2=explain2,
            reason=reason,
            judge=judge,
        )

    def get_session(self, sessionid):
        return self._select(
            kind=SessionEntityClient.KIND_SESSION,
            keyid=sessionid,
            parent_kind=SessionEntityClient.KIND_SESSION_LIST,
            parent_keyid=SessionEntityClient.KEYID_SESSION_LIST,
        )

    def get_public_sessions(self):
        entities = self._get_from_parent(
            kind=SessionEntityClient.KIND_SESSION,
            parent_kind=SessionEntityClient.KIND_SESSION_LIST,
            parent_keyid=SessionEntityClient.KEYID_SESSION_LIST,
        )

        # TODO たぶんここ query を使ったほうがリソースが節約できる
        entities = [e for e in entities if e.get("public", False)]

        # TODO update 側修正してたぶんこれいらなくなる
        entities = [e for e in entities if e.get("keyword", "") != ""]

        # ランク順かつ，同ランクなら新しい順にソート
        entities = sorted(
            entities, key=lambda x: (-x["count"], x["expiration"]), reverse=True
        )

        return entities


client = SessionEntityClient()
