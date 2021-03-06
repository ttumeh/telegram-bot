# -*- coding: utf-8 -*-
# @Author: Tuomas Aaltonen <ttumeh>
# @Date: 15.10.2021
# @Telegram: tzkal
#!/usr/bin/ python3
import json
import requests
import logging
import math
import time
from datetime import datetime
from telegram import Update
from telegram.constants import CHATACTION_FIND_LOCATION
from telegram.ext import Updater, CommandHandler, CallbackContext, RegexHandler, PrefixHandler
from telegram.ext.utils.types import CD
from telegram.ext import MessageHandler
from telegram.ext.messagehandler import Filters

API_TOKEN = ""
BOT_TOKEN = ""
# Enable logging
logging.basicConfig(
    filename='logs.log', format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def anna_taa(update: Update, context: CallbackContext) -> None:
    #Get the user that is given points, and the person that gives the points
    gets_points = update.message.reply_to_message.from_user.username
    gives_points = update.message.from_user.username
    #Check if user is trying to give points to him/herself
    if gives_points == gets_points:
        update.message.reply_text("Cheating not allowed!")
        return
    #Check if user given points is a bot
    if update.message.reply_to_message.from_user.is_bot == True:
        update.message.reply_text("No thanks, I can print million of those if I wanted.")
        return
    #Open json file
    with open('taa.json', 'r') as j:
        data = json.load(j)
    #Search for the user given points in the data
    for s in range(len(data)):
        if data[s]["username"] == gives_points:
            #Remove 1 point from the user that gives away the point
            data[s]["points"] -= 1
            with open("taa.json", "w") as j:
                #Dump the changes into the JSON
                json.dump(data, j)  
        if data[s]["username"] == gets_points:
            #Give 1 points to the user that is given the point
            data[s]["points"] += 1
            with open("taa.json", "w") as j:
                #Dump the changes into the JSON
                json.dump(data, j)            
            points = str(data[s]["points"])
            #Bot replies with:
            update.message.reply_text(str("t???? :D given to {0}!\n{0} now has {1} t???? :D").format(gets_points,points))
            break
    #If user that is given points not in data, create new user and append into data file    
    else:
        with open('taa.json', 'r') as j:
            data = json.load(j)
            data.append({"username":update.message.reply_to_message.from_user.username, "points": 1})
            with open('taa.json', "w") as j:
                json.dump(data, j)
                #Bot replies with:
                update.message.reply_text(str("t???? :D given to {0}!\n{0} now has 1 t???? :D").format(gets_points))

def taa_stats(update: Update, context: CallbackContext):
    supply = 0
    holder_arr = []
    with open('taa.json', 'r') as j:
        data = json.load(j)
        for s in range(len(data)):
            supply += data[s]["points"]
            holder_arr.append([data[s]["username"], (data[s]["points"])])
        holder_arr.sort(key=lambda x:x[1], reverse=True)
        print(holder_arr[0][0])
        update.message.reply_text(str("Circulating supply: {0}\nTop 5 whales:\n" + get_holders(holder_arr)).format(supply))

def my_taa(update: Update, context: CallbackContext):
    get_points_user = update.message.from_user.username
    with open('taa.json', 'r') as j:
        data = json.load(j)
    #Search for the user looking for the data
    for s in range(len(data)):
        if data[s]["username"] == get_points_user:
            points = data[s]["points"]
            #Bot replies with the amount of points the user has
            update.message.reply_text(str("You have {0} t????!").format(points))

def get_holders(taulukko):
    holders = ""
    for x in range(0,5):
        holders += (taulukko[x][0] + ": " + str(taulukko[x][1]) + "\n")
    return holders

def add_group(update: Update, context: CallbackContext):
    #Greets new group member
    for member in update.message.new_chat_members:
        update.message.reply_text(f"Hello {member.full_name} and welcome!")

def get_weather(update: Update, context: CallbackContext) -> None:
    logging.info(update.message.from_user)
    #If no argument provided, reply with the following and return
    if (len(context.args) == 0):
        update.message.reply_text("No city provided!")
        return
    #Requests current weather JSON from the API for the city provided as an argument
    response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + context.args[0] + 
    "&appid=" + API_TOKEN)
    #Load the JSON text into a variable
    weather = json.loads(response.text)
    #Set the wanted values into variables
    temp = str(toCelsius(int(weather['main']['temp'])))
    sky = "{0}".format(str(check_the_sky(weather['weather'][0]['icon'])))
    feelslike = str(toCelsius(int(weather['main']['feels_like'])))
    wind = str(weather['wind']['speed'])
    sunrise = str(to_datetime(int(weather['sys']['sunrise'])))
    sunset = str(to_datetime(int(weather['sys']['sunset'])))
    #Bot sends the current weather as a reply
    update.message.reply_text("Temperature: " + temp + "\N{DEGREE SIGN}C" + sky + "\n" + "Feels like: " + feelslike + "\N{DEGREE SIGN}C"
    + "\n" + "Wind speed: " + wind + "m/s" + "\n" + "Sunrise: " + sunrise + " UTC" + "\n" + "Sunset: " + sunset + " UTC")

def get_forecast(update: Update, context: CallbackContext) -> None:
    logging.info(update.message.from_user)
    #If no argument provided, reply with the following and return
    if (len(context.args) == 0):
        update.message.reply_text("No city provided!")
        return
    #Requests a forecast JSON from the API for the city provided as an argument
    response = requests.get("http://api.openweathermap.org/data/2.5/forecast?q=" + context.args[0] + "&appid=" + API_TOKEN)
    #Load the JSON text into a variable
    weather = json.loads(response.text)
    #Set the wanted data into variables
    forecast_time = [str(string_to_datetime(weather['list'][0]['dt_txt'])),
                    str(string_to_datetime(weather['list'][1]['dt_txt'])),
                    str(string_to_datetime(weather['list'][2]['dt_txt'])),
                    str(string_to_datetime(weather['list'][3]['dt_txt']))]
    temperature =  [str(toCelsius(int(weather['list'][0]['main']['temp']))),
                    str(toCelsius(int(weather['list'][1]['main']['temp']))),
                    str(toCelsius(int(weather['list'][2]['main']['temp']))),
                    str(toCelsius(int(weather['list'][3]['main']['temp'])))]
    sky = [ "{0}".format(str(check_the_sky(weather['list'][0]['weather'][0]['icon']))),
            "{0}".format(str(check_the_sky(weather['list'][1]['weather'][0]['icon']))),
            "{0}".format(str(check_the_sky(weather['list'][2]['weather'][0]['icon']))),
            "{0}".format(str(check_the_sky(weather['list'][3]['weather'][0]['icon'])))]
    #Bot replies with a forecast spanning 9 hours
    update.message.reply_text(
    forecast_time[0] + "\n" + temperature[0] + "\N{DEGREE SIGN}C"  + 
    sky[0] + "\n" + forecast_time[1] + "\n" + temperature[1] + "\N{DEGREE SIGN}C"  + 
    sky[1] + "\n" + forecast_time[2] + "\n" + temperature[2] + "\N{DEGREE SIGN}C"  + 
    sky[2] + "\n" + forecast_time[3] + "\n" + temperature[3] + "\N{DEGREE SIGN}C"  + 
    sky[3])

def get_price(update: Update, context: CallbackContext) -> None:
    logging.info(update.message.from_user)
    #If no argument provided, reply with the following and return
    if (len(context.args) == 0):
        update.message.reply_text("No ticker provided!")
        return
    #Requests JSON from the API for the token provided as an argument
    token = find_name(context.args[0].lower(), update, context)
    response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids={0}&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true'.format(token))
    #Load the JSON text into a variable
    data = json.loads(response.text)
    response = requests.get('https://api.coingecko.com/api/v3/coins/{0}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false'.format(token))
    #Load the JSON text into a variable
    data2 = json.loads(response.text)
    #Set the wanted data into variables and format them into user-friendly format
    ath = data2["market_data"]["ath"]["usd"]
    ath = str("{:,}".format(ath))
    tokenprice = data[token]['usd']
    tokenprice = str("{:,}".format(tokenprice))
    tokenmc = math.trunc(data[token]['usd_market_cap'])
    tokenmc = str("{:,}".format(tokenmc))
    pricechange = str(round(data[token]['usd_24h_change'],1))
    volume = math.trunc(data[token]['usd_24h_vol'])
    volume = str("{:,}".format(volume))
    #Bot replies with following
    context.bot.send_message(chat_id=update.message.chat_id, text=token.capitalize() + 
    "\n" + "Price: " + "$" + tokenprice + "\n" + "Marketcap: " + "$" + tokenmc + 
    "\n" + "All-time-high: " + "$" + ath + "\n" + "24h Change: " + pricechange + "%" + 
    "\n" + "24h Volume: " + "$" + volume)
 
def find_name(ticker, update, context):
    #Looks for the given ticker from .txt file and saves its index
    with open('tickers.txt', encoding="utf8") as f:
        data = f.read().split('\n')
        if ticker in data:
            index = data.index(ticker)
            #If given ticker is not found in the data, reply with following
        else: context.bot.send_message(chat_id=update.message.chat_id, text="Ticker not found!")
    #Looks for the corresponding token name for the ticker given and returns it
    with open('names.txt', encoding="utf-8") as f:
        data = f.read().split('\n')
        token = data[index]
        return str(token)

def string_to_datetime(date):
    #Formats the given UNIX timestamp into user-friendly form (forecast)
    datetime_object = datetime.fromisoformat(date)
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday = weekdays[datetime_object.weekday()]
    time = datetime.strftime(datetime_object, '%d.%m %H:%M')
    return str(weekday + " " + time)

def to_datetime(weather):
    #Formats the given UNIX timestamp into user-friendly form (sunrise-sunset)
    date = (datetime.utcfromtimestamp(weather))
    date = date.strftime('%H:%M:%S')
    return date

def check_the_sky(icon):
    #Returns corresponding weather emoji to the icon in the JSON file
    if icon == "01d":
        return ("\U00002600")
    if icon == "01n":
        return ("\U0001F319")
    if icon == "02n" or icon == "03n" or icon == "04n":
        return ("\U00002601")
    if icon == "04d":
        return ("\U0001F324")
    if icon == "09d" or "09n":
        return ("\U0001F327")
    if icon == "10d" or icon == "10n":
        return ("\U0001F326")
    if icon == "11d" or icon == "11n":
        return ("\U0001F329")
    if icon == "13d" or icon == "13n":
        return ("\U0001F328")
    if icon == "50d" or icon == "50n":
        return ("\U0001F32B")
    else: return ("")

def toCelsius(kv):
    #Convers kelvin into celsius
    return round((kv-273.15), 1)

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher
    add_group_handle = MessageHandler(Filters.status_update.new_chat_members, add_group)
    dispatcher.add_handler(add_group_handle)
    dispatcher.add_handler(CommandHandler("weather", get_weather))
    dispatcher.add_handler(CommandHandler("forecast", get_forecast))
    dispatcher.add_handler(CommandHandler("price", get_price))
    dispatcher.add_handler(PrefixHandler("/", "t????", anna_taa))
    dispatcher.add_handler(PrefixHandler("/", "t????t", my_taa))
    dispatcher.add_handler(CommandHandler("stats", taa_stats))
    # Start the Bot
    updater.start_polling()
    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
