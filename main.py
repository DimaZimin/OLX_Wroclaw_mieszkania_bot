import asyncio
from OlxParser import Parser
from loader import bot, db, dp, file_db, Form
from aiogram import executor
from keyboard import rooms_key, unsubscribe_key, start_keys, final_keys, start_subscription
import logging
from aiogram import types, filters
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext


@dp.message_handler(filters.Command('start'))
async def start(message: Message):
    logging.info(f'USER MESSAGE: {message.text}\tUSER ID: {message.chat.id}')
    await message.answer(text=f"Witaj, {message.from_user.full_name}!\n"
                              f"Aby zacząć proces śledzenia ogłoszeń naciśnij „Aktywuj wyszukiwanie”. "
                              f"W razie jakichkolwiek pytań lub sugestii, "
                              f"zachęcam do kontaktu z deweloperem poprzez kliknięcie przycisku poniżej.",
                              reply_markup=start_keys())


@dp.callback_query_handler(start_subscription.filter(action='next'))
async def process_subscription(call: CallbackQuery):
    await call.answer(cache_time=60)
    callback_data = (call.message.text, call.message.chat.id)
    logging.info(f'call = {callback_data[0]}\tchat id: {callback_data[1]}')
    await call.message.answer('Wybierz rodzaj mieszkania, jaki Cię interesuje',
                              reply_markup=rooms_key())
    await call.message.edit_reply_markup()


@dp.callback_query_handler(text_contains='back')
async def move_to_start(call: CallbackQuery):
    await call.answer(cache_time=60)
    callback_data = (call.message.text, call.message.chat.id)
    logging.info(f'call = {callback_data[0]}\tchat id: {callback_data[1]}')
    await call.message.answer(text=f"Witaj, {call.message.from_user.full_name}!\n"
                                   f"Aby zacząć proces śledzenia ogłoszeń naciśnij „Aktywuj wyszukiwanie”. "
                                   f"W razie jakichkolwiek pytań lub sugestii, "
                                   f"zachęcam do kontaktu z deweloperem poprzez kliknięcie przycisku poniżej.",
                              reply_markup=start_keys())
    await call.message.edit_reply_markup()


@dp.callback_query_handler(text_contains='one')
async def set_number_of_rooms(call: CallbackQuery):
    await call.answer(cache_time=60)
    callback_data = (call.message.text, call.message.chat.id)
    logging.info(f'call = {callback_data[0]}\tchat id: {callback_data[1]}')
    db.update_rooms(call.message.chat.id, 'one')
    await Form.price.set()
    await call.message.edit_reply_markup()
    await call.message.answer('Używając cyfr określ maksymalny czynsz miesięczny w zł.')


@dp.callback_query_handler(text_contains='two')
async def set_number_of_rooms(call: CallbackQuery):
    await call.answer(cache_time=60)
    callback_data = (call.message.text, call.message.chat.id)
    logging.info(f'call = {callback_data[0]}\tchat id: {callback_data[1]}')
    db.update_rooms(call.message.chat.id, 'two')
    await Form.price.set()
    await call.message.edit_reply_markup()
    await call.message.answer('Używając cyfr określ maksymalny czynsz miesięczny w zł.')


@dp.callback_query_handler(text_contains='three')
async def set_number_of_rooms(call: CallbackQuery):
    await call.answer(cache_time=60)
    callback_data = (call.message.text, call.message.chat.id)
    logging.info(f'call = {callback_data[0]}\tchat id: {callback_data[1]}')
    db.update_rooms(call.message.chat.id, 'three')
    await Form.price.set()
    await call.message.edit_reply_markup()
    await call.message.answer('Używając cyfr określ maksymalny czynsz miesięczny w zł.')


@dp.callback_query_handler(text_contains='four')
async def set_number_of_rooms(call: CallbackQuery):
    await call.answer(cache_time=60)
    callback_data = (call.message.text, call.message.chat.id)
    logging.info(f'call = {callback_data[0]}\tchat id: {callback_data[1]}')
    db.update_rooms(call.message.chat.id, 'four')
    await Form.price.set()
    await call.message.edit_reply_markup()
    await call.message.answer('Używając cyfr określ maksymalny czynsz miesięczny w zł.')


@dp.message_handler(lambda message: not message.text.isdigit() or int(message.text) > 99999, state=Form.price)
async def process_price_invalid(message: types.Message):
    logging.info(f'USER MESSAGE: {message.text}\tUSER ID: {message.chat.id}')
    return await message.reply("⛔️Uwaga! Kwota powinna być liczbą do 99999 (na przykład 1200). "
                               "Należy użyć cyfr bez spacji i innych znaków. "
                               "Proszę, wprowadź maksymalną kwotę jeszcze raz.")


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.price)
async def process_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    db.update_price(message.chat.id, price=int(message.text))
    logging.info(f'USER MESSAGE: {message.text}\tUSER ID: {message.chat.id}')
    await state.finish()
    await subscribe(message)


@dp.message_handler(commands=['subscribe'])
async def subscribe(message: Message):
    await message.answer('Proszę poczekać...')
    if not db.subscriber_exists(message.chat.id):
        db.add_subscriber(message.chat.id)
        logging.info(f'Subscribe user {message.from_user.id}')
    else:
        db.update_subscription(message.chat.id, True)
        logging.info(f'Subscribtion updated for user {message.from_user.id}')
    await message.answer(
         f"☑️Sukces! Subskrypcja została pomyślnie aktywowana!\nCzekam aż pojawią się nowe ogłoszenia "
         f"do {db.get_user_settings(message.chat.id)[0][-1]} zł.\n"
         "\nBędę informował Cię na bieżąco. ", reply_markup=unsubscribe_key)


@dp.message_handler(filters.Text(contains=['Zrezygnuj z otrzymywania']))
async def unsubscribe(message: types.Message):
    if not db.subscriber_exists(message.chat.id):
        db.add_subscriber(message.from_user.id, False)
        logging.info(f'TRIED TO UNSUBSCRIBE WHILE NOT SUBSCRIBED {message.from_user.id}')
        await message.answer("Subskrypcja nie jest aktywowana.")
    else:
        db.update_subscription(message.chat.id, False)
        logging.info(f'UNSUBSCRIBE {message.from_user.id}')
        await message.answer("⚠️Zrezygnowałeś z otrzymywania nowych powiadomień. ", reply_markup=ReplyKeyboardRemove())
        await message.answer("Dziękuję za skorzystanie z moich usług. Proszę, wesprzyj mnie i poleć znajomym. "
                             "W razie pytań lub sugestii, zachęcam do kontaktu z deweloperem: @dimazmn ",
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
            lastly_created_ads = [f'ID:{ad[2]}, PRICE:{ad[1]}' for ad in parser.make_ad_list()]
            logging.info(f'SCRAPED ADS FOR {self.nrooms.upper()} ROOMS: {lastly_created_ads}')
            new_ads = parser.get_last_ads(self.nrooms)
            logging.info(f"NEW ADS FOR {self.nrooms.upper()} ROOMS{new_ads}")
            parser.clear_oldest_ads(self.nrooms)
            if new_ads:
                for ad in parser.make_ad_list():
                    if ad[2] in new_ads:
                        subscriptions = db.get_subscriptions(self.nrooms)
                        for subscriber in subscriptions:
                            if int(ad[1]) <= int(subscriber[-1]):
                                logging.info(f'AD ID:{ad[2]} SENT TO:{subscriber}')
                                await bot.send_message(
                                    subscriber[1], text=f'💵Koszt wynajmu: {ad[1]}\n{ad[0]}')


if __name__ == '__main__':

    one_room = ScheduledTask(file_db, "one")
    two_rooms = ScheduledTask(file_db, "two")
    three_rooms = ScheduledTask(file_db, "three")
    four_rooms = ScheduledTask(file_db, "four")

    dp.loop.create_task(one_room.scheduled(60))
    dp.loop.create_task(two_rooms.scheduled(60))
    dp.loop.create_task(three_rooms.scheduled(60))
    dp.loop.create_task(four_rooms.scheduled(60))

    executor.start_polling(dp, skip_updates=True)
