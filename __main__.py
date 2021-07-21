import logging
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
import requests
import re
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# OS port to listen to
PORT = int(os.environ.get('PORT', 5000))

# Heroku config keys
TOKEN = os.getenv('TOKEN')
API_KEY = os.getenv('API_KEY')
WEBAPP_URL = os.getenv('WEBAPP_URL')

# API call URL
REQUEST_URL = 'https://api.spoonacular.com/recipes/random?number=1&tags=dessert&apiKey={}'

# To limit caption length
MAX_SUMMARY_CHAR_LENGTH = 1200


def start(update, context):
    """Sends a message when the command /start is issued."""
    chat_id = update.message.chat_id
    context.bot.send_message(
        chat_id=chat_id, text='Hi! Enter /pls to obtain a random dessert recipe.')


def get_recipe():
    """Makes an API call to Spoonacular to retrieve exactly one random recipe."""
    contents = requests.get(REQUEST_URL.format(API_KEY)).json()
    return contents['recipes'][0]


def get_recipe_details():
    """
    Obtains the details of a random recipe selected.
    Returns its name, image URL, source (recipe) URL, and summary description.
    """
    allowed_extension = ['jpg', 'jpeg', 'png']
    file_extension = ''
    summary_char_length = 2000
    while file_extension not in allowed_extension or summary_char_length > MAX_SUMMARY_CHAR_LENGTH:
        recipe = get_recipe()
        print('Getting recipe...')
        try:
            name = recipe['title']
            image_url = recipe['image']
            source_url = recipe['sourceUrl']
            summary = recipe['summary']
            summary_char_length = len(summary)
            print('Summary character length:', summary_char_length)
        except KeyError:
            continue
        file_extension = re.search("([^.]*)$", image_url).group(1).lower()
    return (name, image_url, source_url, summary)


def construct_caption(name, src_url, summary):
    """Creates a caption based on a selected recipe into HTML format."""
    return '<b>{}</b> \
            \n<a href=\"{}\"><b>Recipe here</b></a> \
            \n<b>Description</b>: {}'.format(name, src_url, summary)


def error(update, context):
    """Logs errors and sends error messages caused by updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    chat_id = update.message.chat_id
    context.bot.send_message(
        chat_id=chat_id, text='There seems to be an error somewhere. Sorry :(')


def pls(update, context):
    """Sends a randomly-selected recipe of a dessert with relevant details when the command /pls is issued."""
    (name, image_url, source_url, summary) = get_recipe_details()
    caption = construct_caption(name, source_url, summary)
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id=chat_id, photo=image_url,
                           caption=caption, parse_mode=ParseMode.HTML)


def main():
    # Create the Updater and pass it to the bot's token
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # On different commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler('pls', pls))

    # Log all errors
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

    # Start the Bot 
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook(WEBAPP_URL + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
