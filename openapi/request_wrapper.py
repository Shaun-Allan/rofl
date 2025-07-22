from asyncio import SubprocessProtocol
import requests
from langchain_community.utilities.requests import RequestsWrapper

class UnsafeRequestsWrapper(RequestsWrapper):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        session = requests.Session()
        session.headers.update(self.headers)
        # session.verify = False
        # session.verify = "C:\\dev\\SREMA\\ssl-certs.pem"  # Disable SSL verification
        object.__setattr__(self, "session", session)  # Bypass Pydantic restricti
        
        
        
# class UnsafeRequestsWrapper(RequestsWrapper):
#     def __init__(self, **kwargs):
#         # Force verify to False before Pydantic validation
#         kwargs["verify"] = False
#         super().__init__(**kwargs)

#         session = requests.Session()
#         if self.headers:
#             session.headers.update(self.headers)
#         session.verify = False

#         object.__setattr__(self, "session", session)


# class UnsafeRequestsWrapper(RequestsWrapper):
#     def __init__(self, **kwargs):
#         # Force verify to False before Pydantic validation
#         kwargs["verify"] = False
#         # kwargs["headers"] = self.
#         super().__init__(**kwargs)

#         # Print headers from the superclass
#         print("Superclass headers:", self.headers)

#         # session = requests.Session()
#         # if self.headers:
#         #     session.headers.update(self.headers)
#         # session.verify = False

#         # object.__setattr__(self, "session", session)


