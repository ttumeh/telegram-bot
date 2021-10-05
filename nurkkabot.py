#-*- coding: utf-8 -*-
#!/usr/bin/ python3

import logging
from os import name
from telegram import Update, update, user
from telegram.constants import CHATACTION_FIND_LOCATION
from telegram.ext import Job, Updater, CommandHandler, CallbackContext, dispatcher
from telegram.ext.utils.types import CD
from telegram.files.photosize import PhotoSize
from telegram.utils.helpers import effective_message_type
from telegram.utils.types import JSONDict
import random
from urllib.request import urlopen
from bs4 import BeautifulSoup
import urllib.request
import re


msg = []
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

def haeSivu(update: Update, context: CallbackContext) -> None:

    headers={'User-Agent':user_agent,} 

    if len(context.args) > 1: 
        url = "https://www.iltalehti.fi/saa/" + context.args[1] + "/" + context.args[0]
        url = url.strip(",")
    else:
        kaupunki = urllib.parse.quote(context.args[0])
        url = ("https://www.iltalehti.fi/saa/Suomi/" + kaupunki)

    request=urllib.request.Request(url,None,headers) #The assembled request
    response = urllib.request.urlopen(request)
    data = response.read()

    soup = BeautifulSoup(data, 'html.parser')

    discussion_div = soup.get_text()

    alku = discussion_div.find('Tällä hetkellä')

    loppu = discussion_div.find('Muista')

    subs = discussion_div[alku:loppu]
    update.message.reply_text(subs)


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("weather", haeSivu))

    # TODO Announcements

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
