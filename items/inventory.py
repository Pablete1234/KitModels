from typing import List
from collections import Counter


class Inventory:

    def __init__(self, items: List):
        self.items = items

    def __str__(self):
        return "[" + ",".join([str(e) for e in self.items]) + "]"

    def __eq__(self, other) -> bool:
        return self.items == other.items

    def __hash__(self) -> int:
        result: int = 1
        for item in self.items:
            result = 31 * result + hash(item)

        return result

    def apply(self, fn):
        return Inventory([fn(item) for item in self.items])

    def short_str(self):
        return "[" + ",".join([str(e) for e in self.items if e is not None]) + "]"

    def to_bag(self) -> Counter:
        result = Counter()
        for item in self.items:
            if item is not None:
                result[item] += 1
        return result

    @staticmethod
    def of(row, prefix):
        result = [None]*36
        for i in range(0, 36):
            result[i] = row[prefix + str(i)]

        return Inventory(result)



