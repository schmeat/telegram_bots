#!/usr/bin/env python3
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import InputMediaPhoto, ParseMode, ChatAction
import time
import logging
from telegram_token_key import m_token
from covid.lib.errors import CountryNotFound
import covid_stats_plotter
import vaccinations
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Help Menu:\n'
                             '/repeat <hours> to set a recurrence.\n'
                             '/unset to cancel the recurrence\n'
                             '/now to get the data at this moment\n'
                             '/country <country> to print stats for a given country\n'
                             '/country_list List all of the countries\n'
                             '/region <region> print stats for a given region\n'
                             '/region_list print a list of regions\n'
                             '/help to print this menu\n'
                             '/info to print the README')

def info(update: Update, _: CallbackContext) -> None:
    readme = open("README.md", "r")
    outString = readme.read()
    update.message.reply_text(outString)
    readme.close()

def getGraphs(country = "canada", state = "ontario"):
    images = []
    if country != None:
        images.append(covid_stats_plotter.outputCountryImage)
        covid_stats_plotter.plotCountryCases(country)
    if state != None:
        images.append(covid_stats_plotter.outputStateImage)
        covid_stats_plotter.plotStateCases(state)

    if country == "canada":
        images.append(vaccinations.ontarioVaccineImage)
        images.append(vaccinations.canadaVaccineImage)
        vaccinations.plotVaccinations()


    imageFiles = []
    for image in images:
        ImageFile = open(image, "rb")
        MediaImage = InputMediaPhoto(ImageFile)
        imageFiles.append(MediaImage)
        ImageFile.close()
        os.remove(image)

    return imageFiles

def getCanadaSummary(state = "ontario"):
    return vaccinations.getSummary()

def alarm(context: CallbackContext, state = "ontario", country = "canada") -> None:
    """Send the alarm message."""
    context.bot.send_chat_action(context.job.context, action=ChatAction.UPLOAD_PHOTO)
    context.bot.send_media_group(context.job.context, getGraphs(country, state))
    if country == "canada":
        context.bot.send_message(context.job.context, text=getCanadaSummary(state))

def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

def get_once(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    try:
        chat_id = update.message.chat_id
        context.job_queue.run_once(alarm, 0, context=chat_id, name=str(chat_id))
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /now')

def repeat_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in hours
        due = int(context.args[0]) * 3600
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(alarm, due, context=chat_id, name=str(chat_id))

        text = 'Timer successfully set!'
        if job_removed:
            text += ' Old one was removed.'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /repeat <hours>')

def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
    update.message.reply_text(text)

def country_data(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the country
        country = " ".join(context.args).title()

        update.message.reply_media_group(getGraphs(country=country, state=None))
        if country == "canada":
            update.message.reply_text(getCanadaSummary())
        else:
            update.message.reply_text(covid_stats_plotter.getCountrySummary(country))

    except (IndexError, ValueError, KeyError):
        update.message.reply_text('Usage: /country country'
                                  'Check the list of countries to see if your input is not valid')

def country_list(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    update.message.reply_text(covid_stats_plotter.getListOfCountries())


def region_data(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the region
        region = " ".join(context.args).title()

        chat_id = update.message.chat_id
        update.message.reply_media_group(getGraphs(state=region, country=None))
        update.message.reply_text(covid_stats_plotter.getRegionSummary(region = region))

    except (IndexError, ValueError, KeyError):
        update.message.reply_text('Usage: /region <region>\n'
                                  'Check the list of regions to see if your input is not valid')

def region_list(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    update.message.reply_text(covid_stats_plotter.getListOfRegions())

def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(m_token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", help))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("now", get_once))
    dispatcher.add_handler(CommandHandler("repeat", repeat_timer))
    dispatcher.add_handler(CommandHandler("unset", unset))
    dispatcher.add_handler(CommandHandler("country", country_data))
    dispatcher.add_handler(CommandHandler("country_list", country_list))
    dispatcher.add_handler(CommandHandler("region", region_data))
    dispatcher.add_handler(CommandHandler("region_list", region_list))
    dispatcher.add_handler(CommandHandler("info", info))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

