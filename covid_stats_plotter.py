#!/usr/bin/env python3
from covid.api import CovId19Data
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

outputStateImage = "state_cases.png"
outputCountryImage = "country_cases.png"

def getSummary(res, title):
    summaryMapToday = {"New Cases Today" : "confirmed",
                       "New Recovered Today" : "recovered",
                       "New Deaths Today" : "deaths"};
    summaryMapTotal = {"Total Cases" : "confirmed",
                       "Total Recovered" : "recovered",
                       "Total Deaths" : "deaths"};
    current_index = -1
    currentData = res[list(res)[current_index]]
    while float(currentData['change_confirmed']) == 0.0 and float(currentData['change_deaths']) == 0.0 and float(currentData['change_recovered']) == 0.0:
        current_index -= 1
        try:
            currentData = res[list(res)[current_index]]
        except:
            return "Couldn't find valid data."

    secondLastData = res[list(res)[current_index - 1]]
    date = pd.to_datetime(list(res)[current_index]).date()
    summaryTitle = "<h3>" + "Summary for: " + title + "</h3>"
    asOfTitle = "<i>" + "As of: " + str(date) + </i>"
    outputString = summaryTitle + "\n" + asOfTitle + "\n"
    for key, value in summaryMapToday.items():
        if value in currentData:
            outputString += "- " + key + ": "
            outputString += format(currentData[value] - secondLastData[value], ',d') + "\n"
    for key, value in summaryMapTotal.items():
        if value in currentData:
            outputString += "- " + key + ": "
            outputString += format(currentData[value], ',d') + "\n"

    return outputString.title()

def getCountrySummary(country = "canada"):
    covid_api = CovId19Data(force=False)
    country_key = country.lower().replace(" ", "_")
    res = covid_api.get_history_by_country(country)[country_key]['history']
    return getSummary(res, country)

def getRegionSummary(region = "Ontario"):
    covid_api = CovId19Data(force=False)
    region_key = region.lower().replace(" ", "_")
    res = covid_api.get_history_by_province(region)[region_key]['history']
    return getSummary(res, region)

def getListOfCountries():
    covid_api = CovId19Data(force=False)
    outputString = ""
    for country in covid_api.show_available_countries():
        outputString += country + "\n"
    return outputString

def getListOfRegions():
    covid_api = CovId19Data(force=False)
    outputString = ""
    for country in covid_api.show_available_regions():
        outputString += country + "\n"
    return outputString

def plotCountryCases(country = "canada"):
    covid_api = CovId19Data(force=False)
    res = covid_api.get_history_by_country(country)
    title = "COVID Cases for " + country
    plotData(res, country, title.title(), outputCountryImage)

def plotStateCases(state = "ontario"):
    covid_api = CovId19Data(force=False)
    res = covid_api.get_history_by_province(state)
    title = "COVID Cases for " + state
    plotData(res, state, title.title(), outputStateImage)

def plottingfunction(date, cases, deaths, title, outputImage) -> None:
    fig, ax = plt.subplots()
    ax.set_title(title + " (7-day Average)")
    lns1 = ax.plot(date, cases, label="Cases")
    ax.set_ylabel("Cases")
    ax.legend()
    plt.xticks(rotation=45)
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
    dbKey = key.lower().replace(" ", "_")
    print(dbKey)
    for day, data in res[dbKey]['history'].items():
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
    print(getCountrySummary("India"))
    print(getRegionSummary("Ontario"))

if __name__ == '__main__':
    main()
