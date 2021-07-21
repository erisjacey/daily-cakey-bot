import logging
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
import requests
import re

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = '1873304340:AAGpY3F5leYN_y3Ebz-mkvDf6o7Zh35Riic'
API_KEY = '0664cb0dac0948c5a70e52eb532f45fe'
REQUEST_URL = 'https://api.spoonacular.com/recipes/random?number=1&tags=dessert&apiKey={}'
MAX_SUMMARY_CHAR_LENGTH = 1200


def get_recipe():
    contents = requests.get(REQUEST_URL.format(API_KEY)).json()
    return contents['recipes'][0]


def get_image_url_summary():
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
    return '<b>{}</b> \
            \n<a href=\"{}\"><b>Recipe here</b></a> \
            \n<b>Description</b>: {}'.format(name, src_url, summary)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def pls(update, context):
    (name, image_url, source_url, summary) = get_image_url_summary()
    caption = construct_caption(name, source_url, summary)
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id=chat_id, photo=image_url,
                           caption=caption, parse_mode=ParseMode.HTML)


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('pls', pls))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
