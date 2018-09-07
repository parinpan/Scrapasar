from skcriteria import Data, MIN, MAX
from skcriteria.madm import closeness
import matplotlib.pyplot as plt


class Topsis:
    @staticmethod
    def create_matrix(scores):
        matrix = []

        for product_id, score in scores.items():
            score_values = list(score.values())
            matrix.append(score_values)

        return matrix

    @staticmethod
    def reshape_priority(priority):
        new_priority = []
        priority_len = len(priority)

        for p in priority:
            p = (priority_len - int(p)) + 1
            new_priority.append(p)

        return new_priority

    @staticmethod
    def calculate(priority, products):
        new_scores = {}
        scores = products['scores']
        product_ids = list(scores.keys())

        if len(product_ids) == 0:
            return

        first_product_id = product_ids[0]
        entity = list(scores[first_product_id].keys())

        criteria = [MAX] * len(entity)
        matrix = Topsis.create_matrix(scores)
        priority = Topsis.reshape_priority(priority)

        data = Data(
            matrix,
            criteria,
            weights=priority,
            anames=product_ids,
            cnames=entity
        )

        dm = closeness.TOPSIS(mnorm="sum")
        decision = dm.decide(data)
        ranks = decision.rank_.tolist()

        for idx in range(len(ranks)):
            pid = product_ids[idx]

            new_scores[pid] = {
                'pid': pid,
                'rank': ranks[idx],
                'attrs': scores[pid]
            }

        products['scores'] = new_scores

        return decision
