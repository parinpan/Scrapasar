import requests
from api.helpers.marketplace_helper import ProductHelper


class Tokopedia:
    DATA_CONNECTION = {}
    BASE_URL = "https://www.tokopedia.com"
    BASE_URL_API = "https://ace.tokopedia.com"
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"

    @staticmethod
    def intertwine_connection(config={}):
        pass

    @staticmethod
    def stream_products_json(query_params):
        data = {
            "query": query_params,
            "marketplace": "tokopedia"
        }

        # transform params by reference
        ProductHelper.transform_params_key(data)

        return requests.get(
            Tokopedia.BASE_URL_API + "/search/product/v3",
            params=data['query'],
            headers={'User-Agent': Tokopedia.DEFAULT_USER_AGENT}
        ).json()
