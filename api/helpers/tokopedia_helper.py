import json, sys
from bs4 import BeautifulSoup, SoupStrainer


class TokopediaHelper:
    FUTURES = []

    @staticmethod
    def tokopedia_tracer(config):
        text = config['data'].text\
            .strip('show_product_stats(')\
            .strip('show_product_view(')\
            .strip('last_online(')\
            .strip(')')

        try:
            if config['key'] == "product_stats":
                data = json.loads(text)
                config['source']['stats']['success'] = data['success']
                config['source']['stats']['rejected'] = data['reject']
                config['source']['stats']['total_sold'] = data['item_sold']

            elif config['key'] == "product_views":
                data = json.loads(text)
                config['source']['stats']['total_view'] = data['view']

            elif config['key'] == "product_rating":
                data = json.loads(text)

                config['source']['rating'] = {
                    'average': float(data['data']['rating_score']),
                    'total': data['data']['total_review']
                }

            elif config['key'] == "shop_reputation":
                data = json.loads(text)
                TokopediaParser.build_review(data, config['source'])

            elif config['key'] == "shipment_speed":
                data = json.loads(text)
                TokopediaParser.build_speed(data, config['source'])

            elif config['key'] == "product_page":
                TokopediaHelper.FUTURES.append(
                    config['execute'].submit(
                        TokopediaParser.product_page,
                        text,
                        config['source']
                    )
                )

        except Exception as e:
            print("Warning @TokopediaHelper.tokopedia_tracer: " + str(e))


class TokopediaParser:
    @staticmethod
    def product_page(doc, source=None):
        try:
            stats_part = SoupStrainer('div', {"class": 'rvm-right-column'})
            soup = BeautifulSoup(doc, 'lxml', parse_only=stats_part)

            data = {"courier": []}
            courier_cont = soup.find_all('div', {'class': 'rvm-shipping-support'})

            shop_trans_cont = soup.find_all('div', {'class': 'rvm-merchant-transaction'})
            shop_trans = shop_trans_cont[0].text\
            .replace('Transaksi Sukses', '')\
            .replace('%', '')\
            .strip()\
            .split(' ')[0]

            for el in courier_cont:
                courier = el.find('img')['title']
                types = el.find_all('span', {'class': 'va-middle'})

                for type in types:
                    data['courier'].append("{} {}".format(courier, type.text))

            source['courier']['total'] = len(data['courier'])
            source['courier']['list'] = data['courier']
            source['merchant']['transaction']['percentage'] = float(shop_trans)

        except Exception as e:
            print(str(e))

        return data

    @staticmethod
    def build_review(data, source):
        rating = data['data']['rating']

        count = {
            'positive': 0,
            'negative': 0,
            'percentage': 0
        }

        for detail in rating['detail']:
            if detail['rate'] < 3:
                count['negative'] += detail['total_review']

            else:
                count['positive'] += detail['total_review']

        total_reviews = count['positive'] + count['negative']

        if total_reviews > 0:
            count['percentage'] = count['positive'] / total_reviews

        count['percentage'] *= 100
        source['merchant']['reviews'] = count

    @staticmethod
    def build_speed(data, source):
        speed = 0
        summary = data['summary']

        if summary['order_count']  > 0:
            speed = summary['sum_speed'] / summary['order_count']

        speed = 5 if speed > 5 else speed
        speed_type = ''

        if speed < 1:
            speed = 0

        elif speed <= 1.5:
            speed = 5
            speed_type = 'Sangat Cepat'

        elif speed <= 2.5:
            speed = 4
            speed_type = 'Cepat'

        elif speed <= 3.5:
            speed = 3
            speed_type = 'Sedang'

        elif speed <= 4.5:
            speed = 2
            speed_type = 'Lambat'

        elif speed <= 5:
            speed = 1
            speed_type = 'Sangat Lambat'

        else:
            speed = 0

        source['merchant']['delivery_time'] = {
            'min': None,
            'max': None,
            'level': speed,
            'type': speed_type
        }
