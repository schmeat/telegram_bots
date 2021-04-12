#!/usr/bin/env python3
from covid.api import CovId19Data
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

outputStateImage = "state_cases.png"
outputCountryImage = "country_cases.png"

def plotCountryCases(country = "canada"):
    covid_api = CovId19Data(force=False)
    res = covid_api.get_history_by_country(country)
    title = "COVID Cases for " + country
    plotData(res, country, title, outputCountryImage)

def plotStateCases(state = "ontario"):
    covid_api = CovId19Data(force=False)
    res = covid_api.get_history_by_province(state)
    title = "COVID Cases for " + state
    plotData(res, state, title, outputStateImage)

def plottingfunction(date, cases, deaths, title, outputImage) -> None:
    fig, ax = plt.subplots()
    ax.set_title(title)
    lns1 = ax.plot(date, cases, label="Cases")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cases")
    ax.legend()
    # plt.xticks(rotation=45)
    ax2=ax.twinx();
    lns2 = ax2.plot(date, deaths, 'r', label="Deaths")
    ax2.set_ylabel("Deaths")
    lns = lns1 + lns2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=0)
    fig.subplots_adjust(bottom=0.2)
    # plt.xticks(rotation=45)
    fig.savefig(outputImage, format='png', dpi=100, bbox_inches='tight')
    plt.close()

def plotData(res, key, title = "COVID Cases", outputImage = "current_plot.png"):
    days = []
    y_data = []
    y2_data = []
    movingWindow_index = 0
    index = 0
    windowSize = 7
    movingWindow = windowSize * [0]
    movingWindow2 = windowSize * [0]
    last = 0
    last2 = 0
    for day, data in res[key]['history'].items():
        days.append(day)
        confirmed = data['confirmed']
        deaths = data['deaths']
        movingWindow[index] = confirmed - last
        movingWindow2[index] = deaths - last2
        last = confirmed
        last2 = deaths
        y_data.append(sum(movingWindow) / len(movingWindow))
        y2_data.append(sum(movingWindow2) / len(movingWindow2))

        movingWindow_index = index
        index = 0 if (index == (windowSize-1)) else (index + 1)

    days = pd.to_datetime(days)
    plottingfunction(days, y_data, y2_data, title, outputImage)

def main():
    plotStateCases()

if __name__ == '__main__':
    main()
