from datetime import datetime, timedelta

from inv_aki_flask.model.datastore_client.common import DataStoreClient
from inv_aki_flask.model.datastore_client.session import SessionEntityClient


class MessageEntityClient(DataStoreClient):
    KIND_MESSAGE = "Message"

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
        expiration = datetime.now() + timedelta(days=7)

        self._upsert(
            kind=MessageEntityClient.KIND_MESSAGE,
            keyid=messageid,
            parent_kind=SessionEntityClient.KIND_SESSION,
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

    def get_messages(self, sessionid):
        return self._get_from_parent(
            kind=MessageEntityClient.KIND_MESSAGE,
            parent_kind=SessionEntityClient.KIND_SESSION,
            parent_keyid=sessionid,
        )


client = MessageEntityClient()
