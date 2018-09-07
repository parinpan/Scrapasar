import sys
from bs4 import BeautifulSoup, SoupStrainer
from functools import reduce

class BukalapakHelper:
    FUTURES = []

    @staticmethod
    def bukalapak_tracer(config):
        data = config["data"].text

        try:
            if config["key"] == "profile_page":
                pass
                # BukalapakParser.profile_page(data, config["source"])

        except Exception as e:
            print(str(e))

    @staticmethod
    def delivery_time_converter(delivery_time):
        delivery_time = delivery_time.lstrip('< ')
        range, unit = delivery_time.split(' ')

        speed = 5
        speed_type = 'Sangat Cepat'

        unit_multplier = {
            "hari": 3600 * 24,
            "jam": 3600,
        }

        range = range.split('-')
        max_range_key = 0 if len(range) == 1 else 1

        range[0] = int(range[0])
        range[max_range_key] = int(range[max_range_key])

        if unit == "hari":
            if range[max_range_key] == 2:
                speed = 4
                speed_type = 'Cepat'

            elif range[max_range_key] == 3:
                speed = 3
                speed_type = 'Sedang'

            elif range[max_range_key] == 4:
                speed = 2
                speed_type = 'Lambat'

            else:
                speed = 1
                speed_type = 'Sangat Lambat'

        return {
            "min": range[0] * unit_multplier[unit],
            "max": range[max_range_key] * unit_multplier[unit],
            "level": speed,
            "type": speed_type
        }


class BukalapakParser:
    @staticmethod
    def build_shop_transaction(source):
        shop_transaction = {
            'made': reduce(dict.get, ["store", "rejection", "recent_transactions"], source),
            'rejected': reduce(dict.get, ["store", "rejection", "rejected"], source),
            'percentage': 0
        }

        if shop_transaction['made'] > 0:
            shop_transaction['percentage'] = (shop_transaction['made'] - shop_transaction['rejected']) / shop_transaction['made']
            shop_transaction['percentage'] *= 100

        return shop_transaction

    """@staticmethod
    def profile_page(doc, source):
        profile_part = SoupStrainer('article')
        soup = BeautifulSoup(doc, 'lxml', parse_only=profile_part)
        pass"""
