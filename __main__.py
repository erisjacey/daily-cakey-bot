from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
import requests
import re

TOKEN = '1873304340:AAGpY3F5leYN_y3Ebz-mkvDf6o7Zh35Riic'
API_KEY = '0664cb0dac0948c5a70e52eb532f45fe'
REQUEST_URL = 'https://api.spoonacular.com/recipes/random?number=1&tags=dessert&apiKey={}'


def get_recipe():
    contents = requests.get(REQUEST_URL.format(API_KEY)).json()
    return contents['recipes'][0]


def get_image_url_summary():
    allowed_extension = ['jpg', 'jpeg', 'png']
    file_extension = ''
    while file_extension not in allowed_extension:
        recipe = get_recipe()
        url = recipe['image']
        summary = recipe['summary']
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    return (url, summary)


def pls(update, context):
    (url, summary) = get_image_url_summary()
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id=chat_id, photo=url,
                           caption=summary, parse_mode=ParseMode.HTML)


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('pls', pls))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
