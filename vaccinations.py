#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 17:47:25 2021

This program connects to the covid19tracker.ca API to pull in information on COVID cases and vaccines
And sends an automated response to a Telegram group via the Telegram Bot wheresmyfuckingvaccine

@author: Anirudh
"""
import urllib.request
import json
from matplotlib import pyplot as plt
import pandas as pd

ontarioVaccineImage = "ontario_vaccines.png"

def plotVaccinationsForOntario():
    url= "https://api.covid19tracker.ca/reports/province/ON"
    jsonData = json.loads(urllib.request.urlopen(url).read().decode())
    dates = []
    total_vaccinations = []
    total_vaccines_distributed = []

    print(jsonData['data'][0])
    for day_data in jsonData['data']:
        date = day_data['date']
        dates.append(date)
        total_vaccinations.append(day_data['total_vaccinations'])
        total_vaccines_distributed.append(day_data['total_vaccines_distributed'])

    dates = pd.to_datetime(dates)
    fig, ax = plt.subplots()
    ax.set_title("Vaccinations for Ontario")
    ax.plot(dates, total_vaccinations, label="Total Vaccinations")
    ax.plot(dates, total_vaccines_distributed, 'r', label="Vaccines Distributed")
    ax.set_xlabel('Date')
    ax.set_ylabel('Vaccinations')
    ax.legend()
    plt.xticks(rotation=45)
    fig.savefig(ontarioVaccineImage, format='png', dpi=100, bbox_inches='tight')

def plotVaccinations():
    urlCanada = "https://api.covid19tracker.ca/summary"
    urlOntario = "https://api.covid19tracker.ca/reports/province/ON"
    plotVaccinationsForOntario()


def main() -> None:
    plotVaccinations()

if __name__ == '__main__':
    main()
