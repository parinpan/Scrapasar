import time
import pickle
import json
import uuid
import sys
import os
from multiprocessing import Pool
from algo.attribute_normalizer import AttributeNormalizer
from api.integrator import Integrator


class Scrapasar:
    CONFIG = {}

    @staticmethod
    def create_process(marketplace):
        integrator = Integrator({
            "data_type": "json",
            "marketplaces": [marketplace],
            "query": Scrapasar.CONFIG['query']
        })

        return integrator.get_products()

    @staticmethod
    def find(priority):
        p = Pool()
        products = {}
        out = p.map(Scrapasar.create_process, Scrapasar.CONFIG['marketplaces'])

        for product in out:
            products.update(product)

        # normalize
        AttributeNormalizer.apply(products)

        # calculate
        from algo.topsis import Topsis
        Topsis.calculate(priority, products)

        return products


if __name__ == '__main__':
    priority = sys.argv[3].split(',')
    keywords = ' '.join(sys.argv[1].strip().split('_'))

    Scrapasar.CONFIG = {
        'query': {
            'keywords': keywords,
            'category_id': sys.argv[2] if sys.argv[2] != 'null' else None,
            'page': int(sys.argv[4])
        },
        'marketplaces': ['bukalapak', 'tokopedia']
    }

    out = json.dumps(Scrapasar.find(priority))
    print(out)
