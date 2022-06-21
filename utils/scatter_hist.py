# Compute the differences between kit and preference for a whole dataset
import os
from collections import defaultdict
from typing import Iterable, Dict, Tuple

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from items import Inventory
from utils import read_file


def compute_diff(_kit: Iterable, _sort: Iterable) -> (float, float):
    _item_count = 0
    _diff_count = 0

    _bar_diff = 0
    for i, ki, si in zip(range(0, 36), _kit, _sort):
        if ki is None:
            continue

        _item_count = _item_count + 1
        if si is None or ki != si:
            _diff_count = _diff_count + 1

        if i == 8:
            _bar_diff = _diff_count / _item_count
    _kit_diff = _diff_count / _item_count
    return _kit_diff, _bar_diff


def check_differences(ds: str = "kit_data/min_10"):
    pl_files = os.listdir(ds)
    results = np.zeros(shape=(len(pl_files), 4))

    for idx, user in enumerate(pl_files):
        df = read_file(ds + "/" + user, convert_items=True)

        for _idx, _row in df.iterrows():
            kit = _row["kit_0":"kit_35"]
            sort = _row["sorted_0":"sorted_35"]

            kit_diff, bar_diff = compute_diff(kit, sort)
            results[idx, 0:2] += kit_diff, bar_diff
            results[idx, 2:4] += kit_diff > 0, bar_diff > 0

        results[idx, :] = results[idx, :] / df.shape[0]

    return results


def scatter_hist(x, y, lab_x=None, lab_y=None, bins_x=None, bins_y=None):
    # start with a square Figure
    fig = plt.figure(figsize=(8, 8))

    # Add a gridspec with two rows and two columns and a ratio of 2 to 7 between
    # the size of the marginal axes and the main axes in both directions.
    # Also adjust the subplot parameters for a square plot.
    gs = fig.add_gridspec(2, 2, width_ratios=(7, 2), height_ratios=(2, 7),
                          left=0.1, right=0.9, bottom=0.1, top=0.9,
                          wspace=0.05, hspace=0.05)

    ax: Axes = fig.add_subplot(gs[1, 0])
    plt.xlabel(lab_x)
    plt.ylabel(lab_y)
    ax_histx = fig.add_subplot(gs[0, 0], sharex=ax)
    ax_histy = fig.add_subplot(gs[1, 1], sharey=ax)

    # no labels
    ax_histx.tick_params(axis="x", labelbottom=False)
    ax_histy.tick_params(axis="y", labelleft=False)

    # the scatter plot:
    ax.scatter(x, y, s=5)

    cnt, edg, bars = ax_histx.hist(x, bins=bins_x)
    ax_histx.bar_label(bars)
    ax_histx.spines['top'].set_visible(False)
    ax_histx.spines['right'].set_visible(False)

    cnt, edg, bars = ax_histy.hist(y, bins=bins_y, orientation='horizontal')
    ax_histy.bar_label(bars)
    ax_histy.spines['top'].set_visible(False)
    ax_histy.spines['right'].set_visible(False)


def show_scatter_hists(ds, whole=False, bar=True):
    edition_diffs = check_differences(ds)
    kit_edited_amount, kit_edited_times = edition_diffs[:, 0], edition_diffs[:, 2]
    bar_edited_amount, bar_edited_times = edition_diffs[:, 1], edition_diffs[:, 3]

    bins = np.arange(0, 1.0001, 0.1)
    # use the previously defined function
    if whole:
        scatter_hist(kit_edited_times, kit_edited_amount,
                     "Kit edition count (" + ds + ")",
                     "Kit edition amount (" + ds + ")", bins, bins)
        plt.show()

    if bar:
        scatter_hist(bar_edited_times, bar_edited_amount,
                     "Bar edition count (" + ds + ")",
                     "Bar edition amount (" + ds + ")", bins, bins)
        plt.show()


def compute_kit_modifications(ds) -> Dict[Inventory, Tuple[float, float, float, float, float]]:
    pl_files = os.listdir(ds)

    # total_cnt: total count, overall amount of times the kit was given
    # total_pl_cnt: total player count who received this kit
    # total_sum: total sum of edition % (for each time kit is given, 0 to 1)
    # total_pl_sum: total sum of edition %, per player (each player 0 to 1)
    # total_ed_cnt: total edition count, amount of times kit was edited (0 or 1 each time kit is given)
    results: Dict[Inventory, Tuple[float, float, float, float, float]] = defaultdict(lambda: (0, 0, 0, 0, 0))

    for idx, user in enumerate(pl_files):
        df = read_file(ds + "/" + user, convert_items=True, only_category=True)

        user_results: Dict[Inventory, Tuple[float, float, float]] = defaultdict(lambda: (0, 0, 0))

        for _idx, _row in df.iterrows():
            kit = Inventory.of(_row, "kit")
            sort = Inventory.of(_row, "sorted")

            kit_diff, bar_diff = compute_diff(kit, sort)
            pl_count, pl_sum, pl_edition_c = user_results[kit]
            user_results[kit] = (pl_count + 1, pl_sum + bar_diff, pl_edition_c + (1 if bar_diff > 0 else 0))

        for kit, val in user_results.items():
            total_cnt, total_pl_cnt, total_sum, total_pl_sum, total_ed_cnt = results[kit]
            pl_count, pl_sum, pl_edition_c = user_results[kit]
            results[kit] = (total_cnt + pl_count,
                            total_pl_cnt + 1,
                            total_sum + pl_sum,
                            total_pl_sum + (pl_sum / pl_count),
                            total_ed_cnt + pl_edition_c)

        if idx % 50 == 0:
            print("%d/%d" % (idx, len(pl_files)))

    # total count
    # player count
    # edition % overall average (average amount edited overall)
    # edition % per-player average (average amount edited aggregated first by player, then overall)
    # edition count % (times the kit was edited in any amount)
    return {k: (v[0], v[1], v[2] / v[0], v[3] / v[1], v[4] / v[0]) for (k, v) in results.items()}


def show_kit_scatter_hists(ds: str, x, y):
    if x is None or y is None:
        computed_kit_data = compute_kit_modifications(ds)

        if x is None:
            x = [v[2] for v in computed_kit_data.values()]
        if y is None:
            y = [v[0] for v in computed_kit_data.values()]

    bins = np.arange(-0.000001, 1.0001, 0.1)

    scatter_hist(x, y,
                 "Kit edition (" + ds + ")",
                 "Kit uses (" + ds + ")", bins, None)
    plt.show()
