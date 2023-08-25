from datetime import datetime, timedelta

from inv_aki_flask.model.datastore_client.common import DataStoreClient


class ReportEntityClient(DataStoreClient):
    KIND_REPORT_LIST = "ReportList"
    KIND_REPORT = "Report"

    KEYID_REPORT_LIST = "v0.0.1"  # 全件検索用

    def create_report_entity(
        self, sessionid, messageid, keyword, question, answer, correct
    ):
        expiration = datetime.now() + timedelta(days=30)
        self._upsert(
            kind=ReportEntityClient.KIND_REPORT,
            keyid=f"{sessionid}_{messageid}",
            parent_kind=ReportEntityClient.KIND_REPORT_LIST,
            parent_keyid=ReportEntityClient.KEYID_REPORT_LIST,
            keyword=keyword,
            question=question,
            answer=answer,
            correct=correct,
            expiration=expiration,
        )


client = ReportEntityClient()
