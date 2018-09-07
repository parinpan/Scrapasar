import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


class SessionHelper:
    @staticmethod
    def retry_session(retries, session=None):
        session = session or requests.Session()

        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=0.001,
            status_forcelist=(443, 403, 500, 429)
        )

        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session
