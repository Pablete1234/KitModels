import threading

import pandas as pd
from items import *

from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import os


def read_file(file, convert_items=True):
    result = pd.read_parquet(file, engine="pyarrow")
    if convert_items:
        for i in range(0, 36):
            result["kit_" + str(i)] = result["kit_" + str(i)].apply(ItemStack.of)
            result["sorted_" + str(i)] = result["sorted_" + str(i)].apply(ItemStack.of)
    return result


def handle_player(_lock, _counter, _file):
    df = read_file("kit_data/all/" + _file, convert_items=False)

    start = df.columns.get_loc("kit_0")
    end = df.columns.get_loc("kit_35")

    _lock.acquire()
    for _idx, _row in df.iterrows():
        _counter[Inventory(_row[start:end].to_list())] += 1
    _lock.release()


files = os.listdir("kit_data/all")

serialized_kits = Counter()
with ThreadPoolExecutor(max_workers=8) as executor:
    lock = threading.Lock()
    for player_file in files:
        executor.submit(handle_player, lock, serialized_kits, player_file)





