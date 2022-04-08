from typing import List

from .categories import Categories, Category
from .materials import Material, find_material
from .enchantment import Enchantment


class ItemStack:

    def __init__(self, serialized: int):
        self.serialized: int = serialized
        self.material: Material = find_material((serialized >> 16) & 0xffff)

        if self.material is None:
            print("Invalid item stack loaded: " + str(serialized) + " mat id:" + str((serialized >> 16) & 0xffff))
            self.serialized = 0

        self.amount: int = (self.serialized >> 8) & 0xff
        self.data: int = self.serialized & 0xff
        self.enchants: List[Enchantment] = []

        self.category: Category = Categories.of(self.material)

        if self.category is not None:
            self.data, self.enchants = self.category.read_data(self.data)

    def __str__(self):
        result = str(self.material)

        if self.data != 0:
            result += "[" + str(self.data) + "]"

        if len(self.enchants) > 0:
            result += "(" + ",".join([str(e) for e in self.enchants]) + ")"

        if self.amount != 1:
            result += " x " + str(self.amount)

        return result

    def __eq__(self, other) -> bool:
        return self.serialized == other.serialized

    def __hash__(self) -> int:
        return self.serialized

    @staticmethod
    def of(serialized: int):
        return None if serialized == 0 else ItemStack(serialized)
