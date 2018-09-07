from functools import reduce


class Data:
    MAX_INDICATOR = {
        'rating': 0,
        'rating_total': 0,
        'delivery_level': 0,
        'shipment_courier': 0,
        'price': 0,
        'product_selling': 0,
        'merchant_success_transaction': 0,
        'merchant_positive_feedback': 0,
        'merchant_positive_feedback_percentage': 0
    }

    TRANSLATION = {
        'pr': 'rating',
        'prt': 'rating_total',
        'dl': 'delivery_level',
        'sc': 'shipment_courier',
        'prc': 'price',
        'ps': 'product_selling',
        'mst': 'merchant_success_transaction',
        'mpf': 'merchant_positive_feedback',
        'mpfp': 'merchant_positive_feedback_percentage'
    }

    @staticmethod
    def get_var(product):
        return {
            'pr': reduce(dict.get, ['rating', 'average'], product),
            'prt': reduce(dict.get, ['rating', 'total'], product),
            'dl': reduce(dict.get, ['merchant', 'delivery_time', 'level'], product),
            'sc': reduce(dict.get, ['courier', 'total'], product),
            'prc': product['price'],
            'mst': reduce(dict.get, ['merchant', 'transaction', 'percentage'], product),
            'ps': reduce(dict.get, ['stats', 'total_sold'], product),
            'mpf': reduce(dict.get, ['merchant', 'reviews', 'positive'], product),
            'mpfp': reduce(dict.get, ['merchant', 'reviews', 'percentage'], product)
        }

class AttributeNormalizer:
    @staticmethod
    def apply(product_list):
        scores = {}
        scoring_indicator = MaxFinder.leverage(product_list)

        for marketplace, products in product_list.items():
            for product_id, product in products.items():
                var = Data.get_var(product)

                for key, score in var.items():
                    key_translate = Data.TRANSLATION[key]
                    indicator = scoring_indicator[key_translate]

                    score = score if score is not None else 0
                    scores[product_id] = scores.get(product_id, {})
                    scores[product_id][key_translate] = score / indicator

                # flip
                to_flip = ['price']
                AttributeNormalizer.flip(to_flip, scores[product_id])

                # join
                AttributeNormalizer.join('rating_total', 'rating', scores[product_id])
                AttributeNormalizer.join('merchant_positive_feedback_percentage', 'merchant_positive_feedback', scores[product_id])


        product_list['scores'] = scores

    @staticmethod
    def flip(keys, scores):
        for key in keys:
            score = scores[key]
            scores[key] = 1 - score if score < 1 else 1

    def join(fromz, to, scores):
        scores[to] += scores[fromz]
        scores[to] /= 2
        del scores[fromz]


class MaxFinder:
    @staticmethod
    def leverage(product_list):
        for marketplace, products in product_list.items():
            for product_id, product in products.items():
                var = Data.get_var(product)

                for k, v in Data.TRANSLATION.items():
                    if var[k] is not None and var[k] > Data.MAX_INDICATOR[v]:
                        Data.MAX_INDICATOR[v] = var[k]

        return Data.MAX_INDICATOR
