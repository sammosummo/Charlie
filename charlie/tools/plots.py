"""
Matplotlib is not the most intuitive plotting package. Thia script contains
a few convenience plotting functions.
"""
__author__ = 'smathias'


import numpy as np
import matplotlib.pyplot as plt

def bar_chart(labels, values, xlabel=None, ylabel=None, title=None):
    """
    Creates a simple bar chart given a list of string labels and associated
    values.
    :param labels: strings
    :param values: values, same length as labels
    :return: fig, ax
    """
    plt.cla()
    n_groups = len(labels)
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.5
    rects = plt.bar(index, values, bar_width)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(index, labels)
    xticknames = plt.setp(ax, xticklabels=labels)
    plt.setp(xticknames, rotation=80)
    plt.tight_layout()
    return fig, ax