from collections import defaultdict
from typing import Dict

from nptyping import *

from items import *
import numpy as np


class KitPredictor:
    def predict_kit(self, kit: Inventory) -> Inventory:
        if self.ignore_kit(kit):
            return kit

        vals: Dict[Category, NDArray[Shape["9"], Float]] = {}

        bag = kit.to_bag()
        for item, amt in bag.items():
            vals[item] = self.predict(kit, item)

        prediction: Inventory = Inventory([None] * 9)

        while len(bag) >= 1:
            k, v = max(vals.items(), key=lambda itm: np.max(itm[1]))
            slot = np.argmax(v)
            if v[slot] == -1:  # We ran out of preferences (even 0%'s). Means we filled all slots
                break

            # Default pick (no preferences), try to search for original position in kit.
            if v[slot] == 0:
                for idx, it in zip(range(0, 9), kit.items):
                    if it == k and v[idx] != -1:
                        slot = idx
                        break

            if prediction.items[slot] is not None:
                raise Exception("Attempted to put 2 items in same slot")

            prediction.items[slot] = k

            bag[k] -= 1
            if bag[k] <= 0:
                del bag[k]
                del vals[k]

            for v in vals.values():
                v[slot] = -1

        return prediction

    def ignore_kit(self, kit: Inventory):
        pass

    def predict(self, kit: Inventory, item: object) -> NDArray[Shape["9"], Float]:
        pass

    def learn(self, kit: Inventory, pref: Inventory) -> None:
        pass

    @staticmethod
    def calculate_diff(predicted: Inventory, actual: Inventory):
        item_count = 0
        diff_count = 0
        for i, p_it, a_it in zip(range(0, 9), predicted.items, actual.items):
            if a_it is None:
                continue

            item_count = item_count + 1

            if p_it != a_it:
                diff_count = diff_count + 1
        return diff_count / item_count if item_count > 0 else 0


class NoOpPredictor(KitPredictor):
    def ignore_kit(self, kit: Inventory):
        return True


class NaiveBayesPredictor1(KitPredictor):

    def __init__(self) -> None:
        super().__init__()
        self.chances: Dict[Category, NDArray[Shape["9"], Float]] = defaultdict(lambda: np.zeros(shape=9, dtype=float))

    def ignore_kit(self, kit: Inventory):
        return not (Weapon in kit or Tool in kit)

    def predict(self, kit: Inventory, item: Category) -> NDArray[Shape["9"], Float]:
        arr = self.chances[item]
        total = np.sum(arr)
        # We have preferences matching for this case, return those
        if total != 0:
            return arr / total
        # No preferences for this use-case, create dummy. Assume you WANT the default position(s).
        return np.array([1 if ki == item else 0 for i, ki in zip(range(0, 9), kit.items)], dtype=float)

    def learn(self, kit: Inventory, pref: Inventory) -> None:
        for i, ki, pi in zip(range(0, 9), kit.items, pref.items):
            if pi is not None:
                self.chances[pi][i] += 1


class NaiveBayesPredictor2(KitPredictor):

    def __init__(self) -> None:
        super().__init__()
        self.chances: Dict[Category, NDArray[Shape["2,9"], Float]] = defaultdict(lambda: np.zeros(shape=(2, 9), dtype=float))

    def ignore_kit(self, kit: Inventory):
        return not (Weapon in kit or Tool in kit)

    def predict(self, kit: Inventory, item: Category) -> NDArray[Shape["9"], Float]:
        mat = self.chances[item]
        arr = np.array([mat[0 if ki == item else 1][i] for i, ki in zip(range(0, 9), kit.items)])
        total = np.sum(arr)
        # We have preferences matching for this case, return those
        if total != 0:
            return arr / total
        # No preferences for this use-case, create dummy. Assume you WANT the default position(s).
        return np.array([1 if ki == item else 0 for i, ki in zip(range(0, 9), kit.items)], dtype=float)

    def learn(self, kit: Inventory, pref: Inventory) -> None:
        for i, ki, pi in zip(range(0, 9), kit.items, pref.items):
            if pi is not None:
                self.chances[pi][0 if ki == pi else 1][i] += 1


class NaiveBayesPredictor3(KitPredictor):

    def __init__(self) -> None:
        super().__init__()
        self.chances: Dict[Category, NDArray[Shape["10,9"], Float]] = defaultdict(lambda: np.zeros(shape=(10, 9), dtype=float))

    def ignore_kit(self, kit: Inventory):
        return not (Weapon in kit or Tool in kit)

    def predict(self, kit: Inventory, item: Category) -> NDArray[Shape["9"], Float]:
        mat = self.chances[item]
        arr = np.zeros(shape=9, dtype=float)
        for i, ki in enumerate(kit.items):
            if ki == item:
                row = min(i, 9)  # Max row to check is 10th row (idx = 9)
                total = np.sum(mat[row, :])
                if total != 0:
                    arr += (mat[row, :] / total)
                if i >= 9:  # If 10th row is included we're done
                    break

        if np.any(arr):
            return arr
        # No preferences for this use-case, create dummy. Assume you WANT the default position(s).
        return np.array([1 if ki == item else 0 for i, ki in zip(range(0, 9), kit.items)], dtype=float)

    def learn(self, kit: Inventory, pref: Inventory) -> None:
        for i, ki, pi in zip(range(0, 9), kit.items, pref.items):
            if pi is not None:
                if ki == pi:
                    self.chances[pi][i, i] += 1
                else:
                    indexes = [min(idx, 9) for idx, it in enumerate(kit.items) if it == pi and it != pref.items[idx]]
                    for idx in indexes:
                        self.chances[pi][idx, i] += 1 / len(indexes)

