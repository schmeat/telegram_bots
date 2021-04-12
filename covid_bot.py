#!/usr/bin/env python3
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import time
import logging
from telegram_token_key import m_token
from covid.lib.errors import CountryNotFound
import covid_stats_plotter

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Help Menu:\n/repeat <seconds> to set a recurrence.\n/unset to cancel the recurrence\n/now to get the date at this moment\n/help to print this menu')

def echo(update, context):
    if not hasattr(echo,"count"):
        echo.count=0
    if echo.count <= 0:
        # context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
        help(update, context)
        echo.count = 5
    else:
        echo.count = echo.count - 1

def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    state = "ontario"
    country = "canada"
    covid_stats_plotter.plotStateCases(state)
    graph = open(covid_stats_plotter.outputImage, "rb")
    context.bot.send_photo(job.context, graph)
    graph.close()
    covid_stats_plotter.plotCountryCases(country)
    graph = open(covid_stats_plotter.outputImage, "rb")
    context.bot.send_photo(job.context, graph)
    graph.close()

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
        update.message.repeat_timer('Usage: /now <country> <state>')

def repeat_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
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
        update.message.reply_text('Usage: /repeat <seconds>')

def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
    update.message.reply_text(text)

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
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

