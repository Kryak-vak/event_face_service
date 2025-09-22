from django.conf import settings
from httpx import Client


class EventApiClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.headers.update({
            "Authorization": f"Bearer {settings.API_JWT}",
        })
    
    def request(self, method, url, *args, **kwargs):
        json_payload = dict(kwargs.pop("json", {}) or {})
        json_payload.setdefault("owner_id", settings.OWNER_ID)
        kwargs["json"] = json_payload

        return super().request(method, url, *args, **kwargs)
