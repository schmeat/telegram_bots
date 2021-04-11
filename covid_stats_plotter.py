#!/usr/bin/env python3
from covid.api import CovId19Data
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

outputImage = "current_plot.png"

def plottingfunction(date, cases, deaths, title) -> None:
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.plot(date, cases)
    ax.set_xlabel("Date")
    ax.set_ylabel("Cases")
    # plt.xticks(rotation=45)
    ax2=ax.twinx();
    ax2.plot(date, deaths, 'r')
    ax2.set_ylabel("Deaths")
    fig.subplots_adjust(bottom=0.2)
    # plt.xticks(rotation=45)
    fig.savefig(outputImage, format='png', dpi=100, bbox_inches='tight')

def plotCountryCases(country = "canada"):
    covid_api = CovId19Data(force=False)
    res = covid_api.get_history_by_country(country)
    title = "COVID Cases for " + country
    plotData(res, country, title)

def plotStateCases(state = "ontario"):
    covid_api = CovId19Data(force=False)
    res = covid_api.get_history_by_province(state)
    title = "COVID Cases for " + state
    plotData(res, state, title)

def plotData(res, key, title = "COVID Cases"):
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
    plottingfunction(days, y_data, y2_data, title)

def main():
    plotStateCases()

if __name__ == '__main__':
    main()
