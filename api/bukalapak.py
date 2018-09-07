import requests
from bs4 import BeautifulSoup
from api.helpers.marketplace_helper import ProductHelper


class Bukalapak:
    DATA_CONNECTION = {}
    BASE_URL = "https://www.bukalapak.com"
    BASE_URL_API = "https://api.bukalapak.com"
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"

    @staticmethod
    def intertwine_connection():
        html_doc = requests.get(Bukalapak.BASE_URL).text
        soup = BeautifulSoup(html_doc, 'lxml')

        meta_token = soup.find('meta', {"name": "oauth-access-token"})
        Bukalapak.DATA_CONNECTION['access_token'] = meta_token['content']

    @staticmethod
    def stream_products_json(query_params):
        Bukalapak.intertwine_connection()
        query_params['access_token'] = Bukalapak.DATA_CONNECTION['access_token']

        data = {
            "query": query_params,
            "marketplace": "bukalapak"
        }

        # transform params by reference
        ProductHelper.transform_params_key(data)

        return requests.get(
            Bukalapak.BASE_URL_API + "/products",
            params=data['query'],
            headers={'User-Agent': Bukalapak.DEFAULT_USER_AGENT}
        ).json()
