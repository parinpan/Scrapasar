import concurrent.futures
from api.bukalapak import Bukalapak
from api.tokopedia import Tokopedia
from api.helpers.normalizer_helper import Normalizer


class Integrator:
    REQUEST_LIMIT = 5
    EXECUTOR = None

    def __init__(self, config):
        self.config = config
        self.futures = []
        self.products = {config['data_type']: {}}

    def preload(self):
        data_type = self.config['data_type']

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10000) as executor:
                if Integrator.REQUEST_LIMIT:
                    for marketplace in self.config['marketplaces']:
                        if marketplace not in self.products[data_type]:
                            clazz = globals()[marketplace.title()]()
                            method = getattr(clazz, "stream_products_{}".format(data_type))

                            self.futures.append(executor.submit(
                                self.preload_assignment,
                                [marketplace, method, self.config['query']]
                            ))

        except Exception as e:
            print("Warning @Integrator.preload: " + str(e))
            Integrator.REQUEST_LIMIT -= 1

    def preload_assignment(self, params):
        data_type, marketplace, method, query = [self.config['data_type']] + params
        self.products[data_type][marketplace] = method(query)
        return marketplace

    def get_products(self):
        self.preload()

        # normalize all data
        concurrent.futures.wait(self.futures)

        self.products[self.config['data_type']] = Normalizer.source_transformer(
            self.products[self.config['data_type']]
        )

        return self.products[self.config['data_type']]
