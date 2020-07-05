import asyncio
from OlxParser import Parser
from loader import bot, db, dp, file_db
from aiogram import executor
from keyboard import rooms_key, unsubscribe_key, start_keys, final_keys, start_subscription
import logging
from aiogram import types, filters
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove


@dp.callback_query_handler(start_subscription.filter(action='next'))
async def process_subscription(call: CallbackQuery):
    await call.answer()
    callback_data = call.message.text
    logging.info(f'call = {callback_data}')
    await call.message.answer('Aby śledzić ogłoszenia, najpierw wybierz, jakie to ma być mieszkanie:',
                              reply_markup=rooms_key())
    await call.message.edit_reply_markup()


@dp.callback_query_handler(text_contains='back')
async def move_to_start(call: CallbackQuery):
    await call.answer(cache_time=60)
    callback_data = call.message.text
    logging.info(f'call = {callback_data}')
    await call.message.answer(text=f"Witam, {call.message.from_user.full_name}! Aktywuj subskrybcje i "
                              f"zostaniesz poinformowany o najnowszych ogłoszeniach na OLX "
                              f"dotyczących wynajmu mieszkań we Wrocławiu!", reply_markup=start_keys())
    await call.message.edit_reply_markup()


@dp.callback_query_handler(text_contains='one')
async def set_number_of_rooms(call: CallbackQuery):
    await call.answer(cache_time=60)
    callback_data = call.message.text
    logging.info(f'call = {callback_data}')
    db.update_rooms(call.message.chat.id, 'one')
    await subscribe(call.message)
    await call.message.edit_reply_markup()


@dp.callback_query_handler(text_contains='two')
async def set_number_of_rooms(call: CallbackQuery):
    await call.answer(cache_time=60)
    callback_data = call.message.text
    logging.info(f'call = {callback_data}')
    db.update_rooms(call.message.chat.id, 'two')
    await subscribe(call.message)
    await call.message.edit_reply_markup()


@dp.callback_query_handler(text_contains='three')
async def set_number_of_rooms(call: CallbackQuery):
    await call.answer(cache_time=60)
    callback_data = call.message.text
    logging.info(f'call = {callback_data}')
    db.update_rooms(call.message.chat.id, 'three')
    await subscribe(call.message)
    await call.message.edit_reply_markup()


@dp.callback_query_handler(text_contains='four')
async def set_number_of_rooms(call: CallbackQuery):
    await call.answer(cache_time=60)
    callback_data = call.message.text
    logging.info(f'call = {callback_data}')
    db.update_rooms(call.message.chat.id, 'four')
    await subscribe(call.message)
    await call.message.edit_reply_markup()


@dp.message_handler(filters.Command('start'))
async def start(message: Message):
    await message.answer(text=f"Witam, {message.from_user.full_name}! Aktywuj subskrybcje i "
                              f"zostaniesz poinformowany o najnowszych ogłoszeniach na OLX "
                              f"dotyczących wynajmu mieszkań we Wrocławiu!", reply_markup=start_keys())


@dp.message_handler(commands=['subscribe'])
async def subscribe(message: Message):
    await message.answer('Proszę poczekać chwile...')
    if not db.subscriber_exists(message.chat.id):
        db.add_subscriber(message.chat.id)
        logging.info(f'Subscribe user {message.from_user.id}')
    else:
        db.update_subscription(message.chat.id, True)
        logging.info(f'Subscribtion updated for user {message.from_user.id}')
    await message.answer(
        "☑️Subskrypcja została pomyślnie aktywowana!\nBędę Cię informował na bieżąco o nowych ogłoszeniach. ",
        reply_markup=unsubscribe_key)


@dp.message_handler(filters.Text(contains=['Zrezygnować']))
async def unsubscribe(message: types.Message):
    if not db.subscriber_exists(message.chat.id):
        db.add_subscriber(message.from_user.id, False)
        await message.answer("Subskrypcja nie jest aktywowana.")
    else:
        db.update_subscription(message.chat.id, False)
        await message.answer("⚠️Zrezygnowałeś z otrzymywania nowych powiadomień. ", reply_markup=ReplyKeyboardRemove())
        await message.answer("Dziękuję za skorzystanie z moich usług. Proszę wesprzyj mnie i poleć znajomym. "
                             "Jeśli masz jakieś pytania lub propozycje, ",
                             reply_markup=final_keys)


class ScheduledTask:

    def __init__(self, file, nrooms):
        self.file = file
        self.nrooms = nrooms

    async def scheduled(self, wait_for):
        while True:
            await asyncio.sleep(wait_for)
            parser = Parser(file_db, rooms=self.nrooms)
            parser.update_id(self.nrooms)
            one_room_ads = [ad[2] for ad in parser.make_ad_list()]
            logging.info(one_room_ads)
            new_ads = parser.get_last_ads(self.nrooms)
            logging.info(new_ads)
            parser.clear_oldest_ads(self.nrooms)
            if new_ads:
                for ad in parser.make_ad_list():
                    if ad[2] in new_ads:
                        subscriptions = db.get_subscriptions(self.nrooms)
                        print(self.nrooms)
                        print(subscriptions)
                        for subscriber in subscriptions:
                            await bot.send_message(
                                subscriber[1], text=f'💵Koszt wynajmu: {ad[1]}\n{ad[0]}')


if __name__ == '__main__':

    one_room = ScheduledTask(file_db, "one")
    two_rooms = ScheduledTask(file_db, "two")
    three_rooms = ScheduledTask(file_db, "three")
    four_rooms = ScheduledTask(file_db, "four")

    dp.loop.create_task(one_room.scheduled(50))
    dp.loop.create_task(two_rooms.scheduled(50))
    dp.loop.create_task(three_rooms.scheduled(50))
    dp.loop.create_task(four_rooms.scheduled(50))

    executor.start_polling(dp, skip_updates=True)
