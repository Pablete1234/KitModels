import os
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Counter, Callable, TypeVar, Hashable

import numpy as np
import pandas
import pandas as pd
import pyarrow.parquet as pq
from pandas import Series

from items import *


def read_file(file: str, convert_items: bool = True, only_category: bool = False) -> pandas.DataFrame:
    """
    Read a parquet file with kit data into a dataframe
    :param file: path for the file to read
    :param convert_items: if item cells should be converted from ints to item stacks or categories
    :param only_category: True to convert to categories, false to convert to item stacks
    :return: a pandas dataframe with the data
    """
    result = pd.read_parquet(file, engine="pyarrow")
    if convert_items:
        for i in range(0, 36):
            result["kit_" + str(i)] = result["kit_" + str(i)] \
                .apply(Categories.ofSerialized if only_category else ItemStack.of)
            result["sorted_" + str(i)] = result["sorted_" + str(i)] \
                .apply(Categories.ofSerialized if only_category else ItemStack.of)
    return result


def row_count(file: str) -> int:
    """
    Read the row count in a parquet file
    """
    return pq.read_table(file, columns=[]).num_rows


def split_datasets(sizes: List[int] = None, source: str = "kit_data/all", dest: str = "kit_data/min_", dry_run: bool = None) -> List[int]:
    """
    Split dataset into folders for players with at least n kit preferences saved
    :param sizes: list of sizes
    :param source: source dataset
    :param dest: dataset prefix to use
    :param dry_run: True to ignore copying files, useful to just get a count of kit sizes
    :return: a list with the sizes for all the kits
    """
    if sizes is None:
        sizes = [10, 50, 100]
    if dry_run is None:
        dry_run = all([os.path.isdir(dest + str(s) + "/") for s in sizes])

    result = []

    if not dry_run:
        for s in sizes:
            path = dest + str(s) + "/"
            if os.path.isdir(path):
                shutil.rmtree(path)
            os.mkdir(path)

    for user in os.listdir(source):
        rows = row_count(source + "/" + user)
        result.append(rows)
        if dry_run:
            continue
        for s in sizes:
            if rows >= s:
                shutil.copy(source + "/" + user, dest + str(s) + "/" + user)

    return result


def as_kit_type(_row: Series) -> Inventory:
    return Inventory(sorted(filter(None, _row["kit_0":"kit_35"].apply(Categories.ofSerialized).unique())))


T = TypeVar("T")


# Count-up all separate "kit types" in the dataset
def count_kits(ds: str = "kit_data/min_10", to_kit: Callable[[Series], T] = as_kit_type) -> Counter[T]:
    lock = threading.Lock()
    result = Counter[T]()

    def handle_player(file):
        df = read_file(file, convert_items=False)
        for _idx, _row in df.iterrows():
            inv = to_kit(_row)
            lock.acquire()
            result[inv] += 1
            lock.release()

    files = os.listdir(ds)
    with ThreadPoolExecutor(max_workers=32) as executor:
        lock = threading.Lock()
        for player_file in files:
            executor.submit(handle_player, ds + "/" + player_file)

    return result


def print_kit_counter(kit_counter: Counter[object]):
    for kit, count in sorted(kit_counter.items(), key=lambda kv: kv[1], reverse=False):
        print(str(count) + "\t" + str(kit))


# Display visually original kit and preference kit in a table
def display_changes(pl_file, ds: str = "kit_data/all"):
    df = read_file(ds + "/" + pl_file, only_category=True)
    arr = np.empty(shape=(df.shape[0] * 2, 37), dtype=object)

    kit_start = df.columns.get_loc("kit_0")
    kit_end = df.columns.get_loc("kit_35")+1
    sort_start = df.columns.get_loc("sorted_0")
    sort_end = df.columns.get_loc("sorted_35")+1

    _idx: int
    for _idx, _row in df.iterrows():
        arr[(_idx * 2), 1:] = _row[kit_start:kit_end]
        arr[(_idx * 2) + 1, 1:] = _row[sort_start:sort_end]
        arr[(_idx * 2), 0] = _row[0]

    return arr
