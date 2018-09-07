from api.helpers.session_helper import SessionHelper
from api.helpers.tokopedia_helper import TokopediaHelper, TokopediaParser
from api.helpers.bukalapak_helper import BukalapakHelper, BukalapakParser
from api.tokopedia import Tokopedia
from functools import reduce
import concurrent.futures
import datetime

class Normalizer:
    DOCS_COLLECTION = {}
    FUTURES = {"tokopedia": {}, "bukalapak": {}}
    REQ_SESSION = SessionHelper.retry_session(retries=50)

    @staticmethod
    def source_transformer(sources):
        for marketplace in sources:
            method = getattr(Normalizer, "{}_transformer".format(marketplace))
            sources[marketplace] = method(sources[marketplace])

        return sources

    @staticmethod
    def lookup(key, url):
        return {
            "key": key,
            "value": Normalizer.REQ_SESSION.get(
                url,
                timeout=None,
                headers={'User-Agent': Tokopedia.DEFAULT_USER_AGENT}
            )
        }

    @staticmethod
    def add_trace_url(config):
        base = config["source"][config["product"]]

        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = (first - datetime.timedelta(days=1)).strftime("%Y%m%d")

        dictz = {
            "bukalapak": {
                # "profile_page": base['merchant']['url']
            },
            "tokopedia": {
                "product_page": base['url'],
                "product_stats": "https://js.tokopedia.com/productstats/check?pid={}".format(config["product"]),
                "shop_reputation": "https://www.tokopedia.com/reputationapp/statistic/api/v1/shop/{}/rating".format(base['merchant']['id']),
                "product_rating": "https://www.tokopedia.com/reputationapp/review/api/v1/rating?product_id={}".format(config["product"]),
                "shipment_speed": "https://slicer.tokopedia.com/shop-speed/cube/shop_speed_daily/aggregate?cut=shop_id:{}|finish_date:{}-".format(base['merchant']['id'], last_month)
            }
        }

        return dictz[config["marketplace"]]

    @staticmethod
    def trace_deeper(config):
        with concurrent.futures.ThreadPoolExecutor(max_workers=10000) as executor:
            marketplace = config["marketplace"]
            clazz = globals()["{}Helper".format(marketplace.title())]()
            tracer = getattr(clazz, "{}_tracer".format(marketplace))

            for product in config['source']:
                config["product"] = product
                config["trace_urls"] = Normalizer.add_trace_url(config)

                for key, url in config['trace_urls'].items():
                    Normalizer.FUTURES[marketplace][product] = Normalizer.FUTURES[marketplace].get(product, [])
                    Normalizer.FUTURES[marketplace][product].append(
                        executor.submit(
                            Normalizer.lookup,
                            key,
                            url
                        )
                    )

            for product in Normalizer.FUTURES[marketplace]:
                for future in concurrent.futures.as_completed(Normalizer.FUTURES[marketplace][product]):
                    data = future.result()

                    tracer({
                        "key": data['key'],
                        "data": data['value'],
                        "source": config['source'][product],
                        "execute": executor
                    })

    @staticmethod
    def bukalapak_transformer(sources):
        new_sources, futures, out = [{}, [], []]

        for source in sources['data']:
            review = source['store']['reviews']

            total_review = (review['positive'] + review['negative'])
            source['store']['reviews']['percentage'] = 0

            if total_review > 0:
                source['store']['reviews']['percentage'] = review['positive'] / total_review
                source['store']['reviews']['percentage'] *= 100

            new_sources[source['id']] = {
                "id": source['id'],
                "name": source['name'].strip(),
                "url": source['url'],
                "price": source['price'],
                "stock": source['stock'],
                "condition": source['condition'],
                "discount": reduce(dict.get, ["deal", "percentage"], source),
                "rating": {
                    "average": reduce(dict.get, ["rating", "average_rate"], source),
                    "total": reduce(dict.get, ["rating", "user_count"], source)
                },
                "merchant": {
                    "id": source['store']['id'],
                    "name": source['store']['name'],
                    "url": source['store']['url'],
                    "delivery_time": BukalapakHelper.delivery_time_converter(
                        reduce(dict.get, ["store", "delivery_time"], source)
                    ),
                    "transaction": BukalapakParser.build_shop_transaction(source),
                    "reviews": source['store']['reviews']
                },
                "category": {
                    "id": source['category']['id'],
                    "name": source['category']['name']
                },
                "courier": {
                    "total": len(source['store']['carriers']),
                    "list": source['store']['carriers']
                },
                "image": {
                    "small": source['images']['small_urls'],
                    "large": source['images']['large_urls']
                },
                "stats": {
                    "total_view": source['stats']['view_count'],
                    "total_sold": source['stats']['sold_count'],
                    "sucess": None,
                    "rejected": None
                }
            }

        Normalizer.trace_deeper({
            "marketplace": "bukalapak",
            "source": new_sources
        })

        return new_sources

    @staticmethod
    def tokopedia_transformer(sources):
        new_sources = {}

        for source in sources['data']['products']:
            new_sources[source['id']] = {
                "id": source['id'],
                "name": source['name'],
                "url": source['url'],
                "price": source['price_int'],
                "stock": source['stock'],
                "condition": source['condition'],
                "discount": source['discount_percentage'],
                "rating": {
                    "average": source['rating'],
                    "total": None
                },
                "merchant": {
                    "id": source['shop']['id'],
                    "name": source['shop']['name'],
                    "url": source['shop']['url'],
                    "delivery_time": {},
                    "transaction": {
                        "made": None,
                        "rejected": None,
                        "percentage": None
                    },
                    "reviews": {}
                },
                "category": {
                    "id": source['category_id'],
                    "name": source['category_name']
                },
                "courier": {
                    "total": source['courier_count'],
                    "list": []
                },
                "image": {
                    "small": [source['image_url_300']],
                    "large": [source['image_url_700']]
                },
                "stats": {
                    "total_view": None,
                    "total_sold": None,
                    "sucess": None,
                    "rejected": None
                }
            }

        Normalizer.trace_deeper({
            "marketplace": "tokopedia",
            "source": new_sources
        })

        return new_sources
