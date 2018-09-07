import os
import json
from pathlib import Path


class ParamsHelper:
    PARAMS = {}
    PARAMS_JSON = ""

    @staticmethod
    def load_params(key):
        if key not in ParamsHelper.PARAMS:
            if ParamsHelper.PARAMS_JSON:
                json_text = ParamsHelper.PARAMS_JSON

            else:
                json_file = os.path.dirname(__file__) + '/../misc/params.json'
                json_text = Path(json_file).read_text()

            ParamsHelper.PARAMS[key] = json.loads(json_text)[key]

        return ParamsHelper.PARAMS[key]


class ProductHelper:
    @staticmethod
    def transform_params_key(config):
        new_data = {}
        product_query_params = ParamsHelper.load_params("product_query_params")
        product_query_values = ParamsHelper.load_params("product_query_values")
        category_translation = ParamsHelper.load_params("category_translation")
        marketplace_params = product_query_params[config['marketplace']]
        marketplace_values = product_query_values[config['marketplace']]
        config['query']['category_id'] = config['query']['category_id']

        # category translation
        preq = config['query']['category_id'] in category_translation
        preq = preq and config['marketplace'] in category_translation[config['query']['category_id']]

        if preq:
            config['query']['category_id'] = category_translation[config['query']['category_id']][config['marketplace']]

        else:
            config['query']['category_id'] = ""


        for key in marketplace_params:
            new_key = marketplace_params[key]
            new_data[new_key] = config['query'][key] if key in config['query'] else ""

            if key == "page":
                new_data[new_key] = 0

                if config['query']['page'] > 1:
                    key_translate = {'bukalapak': 'limit', 'tokopedia': 'rows'}
                    new_data[new_key] = config['query']['page'] * marketplace_values[key_translate[config['marketplace']]]

            if not new_data[new_key] and new_key in marketplace_values:
                new_data[new_key] = marketplace_values[new_key]

        config['query'] = new_data
