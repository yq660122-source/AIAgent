import requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def create_session():

    session = requests.Session()

    retry = Retry(

        total=3,

        backoff_factor=1,

        status_forcelist=[
            429,
            500,
            502,
            503,
            504
        ],

        allowed_methods=["GET"]

    )

    adapter = HTTPAdapter(max_retries=retry)

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


session = create_session()


def safe_get(

    url,

    params=None,

    headers=None,

    timeout=20,

    verify=True

):

    try:

        final_headers = HEADERS.copy()

        if headers:
            final_headers.update(headers)

        response = session.get(

            url,

            params=params,

            headers=final_headers,

            timeout=timeout,

            verify=verify

        )

        response.raise_for_status()

        return response

    except Exception as e:

        print(f"SAFE REQUEST ERROR: {url}")
        print(e)

        return None