#!/usr/bin/env python3
from covid.api import CovId19Data
from matplotlib import pyplot as plt
import numpy as np

outputImage = "current_plot.png"

def plottingfunction(*arguments, ax=None, show=False):
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    # do something with fig and ax here, e.g.
    line, = ax.plot(*arguments)

    if show:
        plt.show()

    return fig, ax, line

def plotStateCases(state = "ontario"):
    covid_api = CovId19Data(force=False)
    res = covid_api.get_history_by_province(state)
    # print(res)
    # res = covid_api.get_history_by_country("Canada")

    days = []
    y_data = []
    last = 0
    for day, data in res[state]['history'].items():
        print(day, data)
        days.append(day)
        diff = data['confirmed'] - last
        y_data.append(diff)
        last = data['confirmed']

    fig, _, _ = plottingfunction(y_data)
    fig.savefig(outputImage)

def main():
    plotStateCases()

if __name__ == '__main__':
    main()
