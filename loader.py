import json
from aiogram import Bot, Dispatcher
from sqlight_api import SQLighter
import logging
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()

with open('token.json') as json_file:
    token = json.load(json_file)

logging.basicConfig(filename='logs.log',
                    filemode='a',
                    format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )
bot = Bot(token=token['TOKEN'])
dp = Dispatcher(bot, storage=storage)
db = SQLighter('db.db')
file_db = 'data.json'


class Form(StatesGroup):
    price = State()
