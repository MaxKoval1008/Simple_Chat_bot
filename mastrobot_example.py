import datetime
import math

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

STATE = None
BIRTH_YEAR = 1
BIRTH_MONTH = 2
BIRTH_DAY = 3


def start_getting_birthday_info(update, context):
    global STATE
    STATE = BIRTH_YEAR
    update.message.reply_text(f"I would need to know your birthday, so tell me what year did you born in...")


# function to handle the /start command
def start(update, context):
    first_name = update.message.chat.first_name
    update.message.reply_text(f"Hi {first_name}, nice to meet you!")
    start_getting_birthday_info(update, context)


# function to handle the /help command
def help(update, context):
    update.message.reply_text(f'Available commands:\r'
                              '\r/start\r '
                              '\r/help\r '
                              '\r/biorhythm ')


# function to handle errors occured in the dispatcher
def error(update, context):
    update.message.reply_text('An error occured')


def received_birth_year(update, context):
    global STATE
    try:
        today = datetime.date.today()
        year = int(update.message.text)

        if year > today.year:
            raise ValueError("invalid value")
        context.user_data['birth_year'] = year
        update.message.reply_text(f"Ok, now I need to know the month (in numerical form)...")
        STATE = BIRTH_MONTH
    except:
        update.message.reply_text("It's funny but it doesn't seem to be correct...")


def received_birth_month(update, context):
    global STATE
    try:
        today = datetime.date.today()
        month = int(update.message.text)
        if month > 12 or month < 1:
            raise ValueError("invalid value")
        context.user_data['birth_month'] = month
        update.message.reply_text(f"Great! And now, the day...")
        STATE = BIRTH_DAY
    except:
        update.message.reply_text("It's funny but it doesn't seem to be correct...")


def received_birth_day(update, context):
    global STATE
    try:
        today = datetime.date.today()
        dd = int(update.message.text)
        yyyy = context.user_data['birth_year']
        mm = context.user_data['birth_month']
        birthday = datetime.date(year=yyyy, month=mm, day=dd)
        if today - birthday < datetime.timedelta(days=0):
            raise ValueError("invalid value")
        context.user_data['birthday'] = birthday
        STATE = None
        update.message.reply_text(f'Ok, you born on {birthday}')
    except:
        update.message.reply_text("It's funny but it doesn't seem to be correct...")


def text(update, context):
    global STATE
    if STATE == BIRTH_YEAR:
        return received_birth_year(update, context)
    if STATE == BIRTH_MONTH:
        return received_birth_month(update, context)
    if STATE == BIRTH_DAY:
        return received_birth_day(update, context)


# This function is called when the /biorhythm command is issued
def biorhythm(update, context):
    user_biorhythm = calculate_biorhythm(
        context.user_data['birthday'])
    update.message.reply_text(f"Phisical: {user_biorhythm['phisical']}")
    update.message.reply_text(f"Emotional: {user_biorhythm['emotional']}")
    update.message.reply_text(f"Intellectual: {user_biorhythm['intellectual']}")


def calculate_biorhythm(birthdate):
    today = datetime.date.today()
    delta = today - birthdate
    days = delta.days
    phisical = math.sin(2 * math.pi * (days / 23))
    emotional = math.sin(2 * math.pi * (days / 28))
    intellectual = math.sin(2 * math.pi * (days / 33))
    biorhythm = {'phisical': int(phisical * 10000) / 100, 'emotional': int(emotional * 10000) / 100,
                 'intellectual': int(intellectual * 10000) / 100, 'phisical_critical_day': (phisical == 0),
                 'emotional_critical_day': (emotional == 0), 'intellectual_critical_day': (intellectual == 0)}
    return biorhythm


def main():
    TOKEN = '5096697363:AAGTw2tATi1wD5b34KVktQSjwop0eS05ApI'
    # create the updater, that will automatically create also a dispatcher and a queue to
    # make them dialoge
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    # add handlers for start and help commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    # add an handler for our biorhythm command
    dispatcher.add_handler(CommandHandler("biorhythm", biorhythm))
    # add an handler for normal text (not commands)
    dispatcher.add_handler(MessageHandler(Filters.text, text))
    # add an handler for errors
    dispatcher.add_error_handler(error)
    # start your shiny new bot
    updater.start_polling()
    # run the bot until Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
