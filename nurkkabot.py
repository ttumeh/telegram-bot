from datetime import date
from datetime import timedelta
from datetime import datetime
import logging
from os import name
from telegram import Update, update, user
from telegram.constants import CHATACTION_FIND_LOCATION
from telegram.ext import Job, Updater, CommandHandler, CallbackContext, dispatcher
from telegram.ext.utils.types import CD
from telegram.utils.helpers import effective_message_type
from telegram.utils.types import JSONDict

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

msg = []
i = 0


def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    global i
    job = context.job

    context.bot.send_message(
        job.context,
        text="This is a reminder for @{}.\n\n On {} {} sent this:".format(
            user, time, msgsender
        ),
    )
    context.bot.send_message(job.context, text="{}".format(msg[i]))
    i += 1


def remindme(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    global msgsender
    global user
    global time

    chat_id = update.message.chat_id
    time = datetime.now().replace(microsecond=0)
    time = time.strftime("%d/%m/%Y %H:%M")

    msg.append(update.message.reply_to_message.text)

    print(len(msg))

    user = update.effective_user.username
    msgsender = update.message.reply_to_message.from_user.name

    try:

        due = int(context.args[0])
        unit = str(context.args[1])

        if due < 0:
            update.message.reply_text("Reminder cannot be set to negative value.")
            return

        if (
            unit != "seconds"
            and unit != "minutes"
            and unit != "hours"
            and unit != "days"
            and unit != "weeks"
            and unit != "months"
            and unit != "years"
        ):
            update.message.reply_text("I don't understand that. Please use plural (e.g. 'seconds')")
            return

        text = "@{} will be reminded in {} {}".format(user, due, unit)
        update.message.reply_text(text)

        if unit == "minutes":
            due = due * 60

        if unit == "hours":
            due = due * 3600

        if unit == "days":
            due = due * 86400

        if unit == "weeks":
            due = due * 604800

        if unit == "months":
            due = due * 2629743

        if unit == "years":
            due = due * 31556926

        context.job_queue.run_once(alarm, due, context=(chat_id), name=str(chat_id))

    except (IndexError, ValueError):
        update.message.reply_text("Usage: /remindme <value> <unit>. See /help for more")


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("remindme", remindme))

    # TODO Announcements

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
