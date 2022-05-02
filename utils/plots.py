import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from matplotlib.axes import Axes


def plot_sizes(val, x_label, y_label):
    plt.plot(sorted(val, reverse=True))
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    ax: Axes = plt.gca()
    ax.loglog()
    ax.get_xaxis().set_major_formatter(mticker.ScalarFormatter())
    ax.get_yaxis().set_major_formatter(mticker.ScalarFormatter())
    ax.grid(True, which='major')
    return plt


def plot_player_sizes(val):
    plot_sizes(val, "Players", "Matches")
    plt.xticks([1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000], rotation='vertical')
    plt.yticks([1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000])
    return plt


def plot_kit_sizes(val):
    plot_sizes(val, "Kit types", "Matches")
    plt.xticks([1, 2, 5, 10, 20, 50, 100, 200, 500])
    plt.yticks([1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000])
    return plt
