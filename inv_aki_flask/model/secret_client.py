from google.cloud import secretmanager


class SecretClient:
    def __init__(self, project_id):
        self.project_id = project_id
        self.client = secretmanager.SecretManagerServiceClient()

    def get_secret(self, secret_id, version_id="latest"):
        try:
            name = "/".join(
                [
                    "projects",
                    self.project_id,
                    "secrets",
                    secret_id,
                    "versions",
                    version_id,
                ]
            )
            response = self.client.access_secret_version(request={"name": name})
            payload = response.payload.data.decode("utf-8").strip()
            return payload

        except Exception as e:
            return None
