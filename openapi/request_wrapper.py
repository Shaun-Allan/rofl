import requests
from langchain_community.utilities.requests import RequestsWrapper

class UnsafeRequestsWrapper(RequestsWrapper):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        session = requests.Session()
        session.headers.update(self.headers)
        session.verify = False  # Disable SSL verification
        object.__setattr__(self, "session", session)  # Bypass Pydantic restriction