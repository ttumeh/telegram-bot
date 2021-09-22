from datetime import date
from datetime import datetime
import logging
from os import name

from telegram import Update, update, user
from telegram.ext import Job, Updater, CommandHandler, CallbackContext, dispatcher
from telegram.utils.helpers import effective_message_type

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""

    job = context.job
    
    if (len(str(job.next_t.hour)) == 1):
        hour = "0"+str(job.next_t.hour+3)
    else:
        hour = str(job.next_t.hour+3)
    if (len(str(job.next_t.minute)) == 1):
        minute = "0"+str(job.next_t.minute)
    else:
        minute = str(job.next_t.minute)
    if (len(str(job.next_t.second)) == 1):
        second = "0"+str(job.next_t.second)
    else:
        second = str(job.next_t.minute)
    
    
    time = str(job.next_t.day) + "/" + str(job.next_t.month) + "/" + str(job.next_t.year) + " " + str(hour) + ":" + str(minute) + ":" + str(second)
    context.bot.send_message(job.context, text='This is a reminder to @{}.\nAt {} you said: '.format(job.name, time))


def remindme(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        unit = str(context.args[1])

        user = update.effective_user.username

        if due < 0:
            update.message.reply_text('Ootko vähän tyhmä ei aika voi alkaa miinuksella :DDDDD')
            return

        if unit != "seconds":
            update.message.reply_text('En y,,ärrä (vielä)')
            return

        context.job_queue.run_once(alarm, due, context=chat_id, name=str(user))

        text = '@{} will be reminded in {} {}'.format(user, due, unit)
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /remindme <value> <unit>')


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("2009677583:AAHAAmmUaZ8XSp9B0bESyq_9d5gUEr05rRc")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("remindme", remindme))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()