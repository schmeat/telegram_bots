#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 17:47:25 2021

This program connects to the covid19tracker.ca API to pull in information on COVID cases and vaccines
And sends an automated response to a Telegram group via the Telegram Bot wheresmyfuckingvaccine

@author: Anirudh & Ajay
"""
import urllib.request
import json
from matplotlib import pyplot as plt
import pandas as pd

ontarioVaccineImage = "ontario_vaccines.png"
canadaVaccineImage = "canada_vaccines.png"
urlOntario = "https://api.covid19tracker.ca/reports/province/ON"
urlCanada = "https://api.covid19tracker.ca/reports"

def plotVaccinationsForURL(url, title = "Vaccinations", outputImage = "vaccinations.png"):
    jsonData = json.loads(urllib.request.urlopen(url).read().decode())
    dates = []
    total_vaccinations = []
    total_vaccines_distributed = []
    new_vaccinations = []
    windowSize = 7
    movingWindow = 7 * [0]
    index = 0
    last = 0

    for day_data in jsonData['data']:
        date = pd.to_datetime(day_data['date'])
        if date > pd.Timestamp(2020, 12, 15):
            dates.append(date)
            total_vaccinations.append(day_data['total_vaccinations'])
            total_vaccines_distributed.append(day_data['total_vaccines_distributed'])
            movingWindow[index] = day_data['change_vaccinations']
            new_vaccinations.append(sum(movingWindow)/len(movingWindow))
            last = index
            index = 0 if (index == (windowSize-1)) else (index+1)

    fig, ax = plt.subplots()
    ax.set_title(title)
    ln1 = ax.plot(dates, total_vaccinations, label="Total Vaccinations")
    ln2 = ax.plot(dates, total_vaccines_distributed, 'r', label="Vaccines Distributed")
    ax.set_ylabel('Total Vaccinations')
    plt.xticks(rotation=45)
    ax2=ax.twinx()
    ln3 = ax2.plot(dates, new_vaccinations, 'b', label="New Vaccintations (7-day avg)")
    ax2.set_ylabel("New Vaccinations")
    lns = ln1 + ln2 + ln3
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=0)
    fig.savefig(outputImage, format='png', dpi=100, bbox_inches='tight')
    plt.close()

def plotVaccinations():
    plotVaccinationsForURL(urlCanada, "Vaccinations for Canada", canadaVaccineImage)
    plotVaccinationsForURL(urlOntario, "Vaccinations for Ontario", ontarioVaccineImage)

def getSummaryData(url, title):
    summary = {}
    jsonData = json.loads(urllib.request.urlopen(url).read().decode())
    outputString = title + " (As of " + jsonData['data'][-1]['date'] + "):\n"
    summary['New Vaccinated'] = jsonData['data'][-1]['change_vaccinations']
    summary['Total Vaccinated'] = jsonData['data'][-1]['total_vaccinations']

    for key, value in summary.items():
        outputString += "- " + str(key) + ": ";
        outputString += format(value,',d') + "\n"
    outputString += "\n"

    return outputString

def getSummary():
    countryString = getSummaryData(urlCanada, "Canada Vaccinations")
    provinceString = getSummaryData(urlOntario, "Ontario Vaccinations")
    return (countryString.title(), provinceString.title())

def main() -> None:
    plotVaccinations()
    print(getSummary())

if __name__ == '__main__':
    main()
