from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import requests
import re

TOKEN = '1873304340:AAGpY3F5leYN_y3Ebz-mkvDf6o7Zh35Riic'

def get_url():
    contents = requests.get('https://random.dog/woof.json').json()    
    # print(contents)
    url = contents['url']
    return url

def bop(update, context):
    url = get_url()
    # print(url)
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id=chat_id, photo=url)

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('bop', bop))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
