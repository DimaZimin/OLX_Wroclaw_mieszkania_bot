import json
from aiogram import Bot, Dispatcher
from sqlight_api import SQLighter
import logging

with open('token.json') as json_file:
    token = json.load(json_file)

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )
bot = Bot(token=token['TOKEN'])
dp = Dispatcher(bot)
db = SQLighter('db.db')
file_db = 'data.json'
