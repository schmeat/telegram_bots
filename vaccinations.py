#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 17:47:25 2021

This program connects to the covid19tracker.ca API to pull in information on COVID cases and vaccines 
And sends an automated response to a Telegram group via the Telegram Bot wheresmyfuckingvaccine

@author: Anirudh
"""

import urllib
import json
import telebot

url = "https://api.covid19tracker.ca/summary"
data = urllib.request.urlopen(url).read().decode()
obj = json.loads(data)

url_on = "https://api.covid19tracker.ca/reports/province/ON"
data_on = urllib.request.urlopen(url_on).read().decode()
obj_on = json.loads(data_on)


percent_nat = (int(obj['data'][-1]['total_vaccinations'])-int(obj['data'][-1]['total_vaccinated']))*100/38048738
str_nat = ("National\nNew COVID Cases: " + str("{:,}".format(int(obj['data'][0]['change_cases']))) +"\nDaily Doses given: " + str("{:,}".format(int(obj['data'][0]['change_vaccinations']))) + "\nPercent Vaccinated : " + str('{:.2f}%'.format(percent_nat)) + "\nLast updated at : " + obj['last_updated'])
#print(str_nat)

percent_on = (obj_on['data'][-1]['total_vaccinations']-obj_on['data'][-1]['total_vaccinated'])*100/14755211
str_on = ("\n\nOntario:\nNew COVID Cases: " + str("{:,}".format(obj_on['data'][-1]['change_cases'])) + "\nDaily Doses given: " + str("{:,}".format(obj_on['data'][-1]['change_vaccinations'])) + "\nPercent Vaccinated : " + str('{:.2f}%'.format(percent_on)) + "\nLast updated at : " + obj_on['last_updated'])
#print(str_on)

total_string = str_nat + str_on
#print(total_string)

# chat ID: -redacted

#connect to Telegram

bot = telebot.TeleBot("redacted", parse_mode=None)
bot.send_message(-redacted,total_string)
