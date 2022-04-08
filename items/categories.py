from collections import defaultdict
from enum import Enum
from typing import List, Dict, Iterable, Optional

from .enchantment import Enchantment
from .materials import Material, find_material


def find_materials(query):
    return [x for x in list(Material) if x.name.endswith(query)]


class Category:
    def __init__(self):
        self.materials = []

    def __lt__(self, other):
        return self.materials[0].value < other.materials[0].value

    def get_all(self) -> List[Material]:
        return self.materials

    def read_data(self, data: int) -> (int, List[Enchantment]):
        return data, []


class EnchantmentCategory(Category):
    def __init__(self):
        super().__init__()
        self.enchants = []

    def read_data(self, data: int) -> (int, List[Enchantment]):
        result = []
        for i, enchant in enumerate(self.enchants):
            if (data & (1 << i)) != 0:
                result.append(enchant)
        return 0, result


class Tool(EnchantmentCategory, Enum):
    PICKAXE = find_materials("_PICKAXE")
    AXE = find_materials("_AXE")
    SPADE = find_materials("_SPADE")
    HOE = find_materials("_HOE")
    SHEARS = [Material.SHEARS]

    def __init__(self, materials):
        super().__init__()
        self.materials = materials
        self.enchants = [Enchantment.DIG_SPEED, Enchantment.SILK_TOUCH, Enchantment.DURABILITY]


class Weapon(EnchantmentCategory, Enum):
    SWORD = find_materials("_SWORD"), [Enchantment.DAMAGE_ALL, Enchantment.KNOCKBACK, Enchantment.FIRE_ASPECT]
    BOW = [Material.BOW], [Enchantment.ARROW_DAMAGE, Enchantment.ARROW_KNOCKBACK, Enchantment.ARROW_FIRE, Enchantment.ARROW_INFINITE]

    def __init__(self, materials, enchants):
        super().__init__()
        self.materials = materials
        self.enchants = enchants


class Bucket(Category, Enum):
    BUCKET = [Material.BUCKET, Material.WATER_BUCKET, Material.LAVA_BUCKET]

    def __init__(self, materials):
        super().__init__()
        self.materials = materials


class Item(Category):
    def __init__(self, material):
        super().__init__()
        self.material = material
        self.materials = [material]

    def __str__(self):
        return "Item." + str(self.material)

    def __eq__(self, other):
        return self.material == other.material

    def __hash__(self):
        return hash(self.material)


class Categories:
    CATEGORY_MAP: Dict[Material, Category] = {}

    @classmethod
    def setup(cls):
        cls.__add_categories(Weapon)
        cls.__add_categories(Tool)
        cls.__add_category(Bucket.BUCKET)

    @classmethod
    def __add_category(cls, category: Category):
        for mat in category.get_all():
            cls.CATEGORY_MAP[mat] = category

    @classmethod
    def __add_categories(cls, categories: Iterable[Category]):
        for cat in categories:
            cls.__add_category(cat)

    @classmethod
    def of(cls, mat: Material) -> Optional[Category]:
        if mat is None:
            return None
        cat: Optional[Category] = cls.CATEGORY_MAP.get(mat)
        if cat is None:
            cls.CATEGORY_MAP[mat] = cat = Item(mat)
        return cat

    @classmethod
    def ofSerialized(cls, serialized: int) -> Optional[Category]:
        if serialized == 0:
            return None
        return Categories.of(find_material((serialized >> 16) & 0xffff))


Categories.setup()
