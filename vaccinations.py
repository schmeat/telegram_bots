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

    for day_data in jsonData['data']:
        date = pd.to_datetime(day_data['date'])
        if date > pd.Timestamp(2020, 12, 15):
            dates.append(date)
            total_vaccinations.append(day_data['total_vaccinations'])
            total_vaccines_distributed.append(day_data['total_vaccines_distributed'])

    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.plot(dates, total_vaccinations, label="Total Vaccinations")
    ax.plot(dates, total_vaccines_distributed, 'r', label="Vaccines Distributed")
    ax.set_xlabel('Date')
    ax.set_ylabel('Vaccinations')
    ax.legend()
    plt.xticks(rotation=45)
    fig.savefig(outputImage, format='png', dpi=100, bbox_inches='tight')
    plt.close()

def plotVaccinations():
    plotVaccinationsForURL(urlOntario, "Vaccinations for Ontario", ontarioVaccineImage)
    plotVaccinationsForURL(urlCanada, "Vaccinations for Canada", canadaVaccineImage)

def getSummaryData(url, title):
    summary = {}
    outputString = title + ":\n"
    jsonData = json.loads(urllib.request.urlopen(url).read().decode())
    summary['Cases'] = jsonData['data'][-1]['change_cases']
    summary['Deaths'] = jsonData['data'][-1]['change_fatalities']
    summary['Vaccinated'] = jsonData['data'][-1]['change_vaccinations']
    summary['Hospitalizations'] = jsonData['data'][-1]['change_hospitalizations']

    for key, value in summary.items():
        outputString += "- " + str(key) + ": ";
        outputString += format(value,',d') + "\n"
    outputString += "\n"

    return outputString

def getSummary():
    outputString = getSummaryData(urlCanada, "Canada Summary")
    outputString += getSummaryData(urlCanada, "Ontario Summary")
    return outputString

def main() -> None:
    plotVaccinations()
    print(getSummary())

if __name__ == '__main__':
    main()
