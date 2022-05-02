# Compute the differences between kit and preference for a whole dataset
import os
from typing import Iterable

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from utils import read_file


def check_differences(ds: str = "min_10"):
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

    pl_files = os.listdir("kit_data/" + ds)
    results = np.zeros(shape=(len(pl_files), 4))

    for idx, user in enumerate(pl_files):
        df = read_file("kit_data/all/" + user, convert_items=True)
        kit_start = df.columns.get_loc("kit_0")
        kit_end = df.columns.get_loc("kit_35") + 1
        sort_start = df.columns.get_loc("sorted_0")
        sort_end = df.columns.get_loc("sorted_35") + 1

        for _idx, _row in df.iterrows():
            kit = _row[kit_start:kit_end]
            sort = _row[sort_start:sort_end]

            kit_diff, bar_diff = compute_diff(kit, sort)
            results[idx, 0:2] += kit_diff, bar_diff
            results[idx, 2:4] += kit_diff > 0, bar_diff > 0

        results[idx, :] = results[idx, :] / df.shape[0]

    return results


def scatter_hist(x, y, labx=None, laby=None):
    # start with a square Figure
    fig = plt.figure(figsize=(8, 8))

    # Add a gridspec with two rows and two columns and a ratio of 2 to 7 between
    # the size of the marginal axes and the main axes in both directions.
    # Also adjust the subplot parameters for a square plot.
    gs = fig.add_gridspec(2, 2, width_ratios=(7, 2), height_ratios=(2, 7),
                          left=0.1, right=0.9, bottom=0.1, top=0.9,
                          wspace=0.05, hspace=0.05)

    ax: Axes = fig.add_subplot(gs[1, 0])
    plt.xlabel(labx)
    plt.ylabel(laby)
    ax_histx = fig.add_subplot(gs[0, 0], sharex=ax)
    ax_histy = fig.add_subplot(gs[1, 1], sharey=ax)

    # no labels
    ax_histx.tick_params(axis="x", labelbottom=False)
    ax_histy.tick_params(axis="y", labelleft=False)

    # the scatter plot:
    ax.scatter(x, y, s=5)

    bins = np.arange(0, 1.0001, 0.1)

    cnt, edg, bars = ax_histx.hist(x, bins=bins)
    ax_histx.bar_label(bars)
    ax_histx.spines['top'].set_visible(False)
    ax_histx.spines['right'].set_visible(False)

    cnt, edg, bars = ax_histy.hist(y, bins=bins, orientation='horizontal')
    ax_histy.bar_label(bars)
    ax_histy.spines['top'].set_visible(False)
    ax_histy.spines['right'].set_visible(False)


def show_scatter_hists(ds, whole=False, bar=True):
    edition_diffs = check_differences(ds)
    kit_edited_amount, kit_edited_times = edition_diffs[:, 0], edition_diffs[:, 2]
    bar_edited_amount, bar_edited_times = edition_diffs[:, 1], edition_diffs[:, 3]

    # use the previously defined function
    if whole:
        scatter_hist(kit_edited_times, kit_edited_amount,
                     "Kit edition count (" + ds + ")",
                     "Kit edition amount (" + ds + ")")
        plt.show()

    if bar:
        scatter_hist(bar_edited_times, bar_edited_amount,
                     "Bar edition count (" + ds + ")",
                     "Bar edition amount (" + ds + ")")
        plt.show()
