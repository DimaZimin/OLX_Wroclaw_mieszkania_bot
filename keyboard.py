from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

rooms_callback = CallbackData('chose_rooms', 'number_of_rooms')
start_subscription = CallbackData('subscription', 'action')


def start_keys():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅Aktywuj wyszukiwanie", callback_data=start_subscription.new(action='next'))],
            [InlineKeyboardButton(text="✉️Skontaktować sie z autorem", url='telegram.me/dimazmn')]])


final_keys = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅Aktywuj wyszukiwanie", callback_data=start_subscription.new(action='next'))],
        [InlineKeyboardButton(text="📤️Poleć znajomym", switch_inline_query='Cześć! Szukasz mieszkanie we Wrocławiu?'
                                                                           'Mogę Ci w tym pomoc.')],
        [InlineKeyboardButton(text="✉️Skontaktować się z autorem", url='telegram.me/dimazmn')]
    ])


def rooms_key():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Kawalerka', callback_data='number_of_rooms:one')],
        [InlineKeyboardButton(text='2 pokoje', callback_data='number_of_rooms:two')],
        [InlineKeyboardButton(text='3 pokoje', callback_data='number_of_rooms:three')],
        [InlineKeyboardButton(text='4 pokoje i więcej', callback_data='number_of_rooms:four')],
        [InlineKeyboardButton(text='⬅️Wstecz', callback_data='back')]
    ])


# unsubscribe_key = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🚫Zrezygnować z nowych powiadomień')]])
unsubscribe_key = ReplyKeyboardMarkup().row(KeyboardButton(text='🚫Zrezygnować z nowych powiadomień'))