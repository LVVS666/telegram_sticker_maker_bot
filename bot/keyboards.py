from aiogram import types


'''Выбор действия в главном меню'''
kb_main_menu = [
        #[types.KeyboardButton(text='Выбрать готовый стикер-пак')],
        [types.KeyboardButton(text='Создать новый стикер-пак')]
    ]
keyboard_main_menu = types.ReplyKeyboardMarkup(keyboard=kb_main_menu, resize_keyboard=True)

'''Выбор действия в меню "Создать новый стикер-пак"'''
kb_new_stickerpack = [
        [types.KeyboardButton(text='Видео стикер-пак')],
        [types.KeyboardButton(text='Стандартный стикер-пак')],
        [types.KeyboardButton(text='Назад')]
    ]
keyboard_new_stickerpack_menu = types.ReplyKeyboardMarkup(keyboard=kb_new_stickerpack, resize_keyboard=True)

'''После запроса на имя стикер пака и адрес бот просит отправить файл формата стикера, после просит
отправить соотвествующий эмоджи, дальше перенаправляет в меню стикер пака'''

'''Меню стикер-пака'''
kb_stickerpack = [
    [types.KeyboardButton(text='Добавить стикер')],
    [types.KeyboardButton(text='Удалить стикер')],
    [types.KeyboardButton(text='Удалить стикер-пак')],
    [types.KeyboardButton(text='Назад')]
]


keyboard_stickerpack_menu = types.ReplyKeyboardMarkup(keyboard=kb_stickerpack, resize_keyboard=True)

'''Меню помощи'''
kb_help = [
    [types.KeyboardButton(text='Выбрaть готовый стикер-пак')],
    [types.KeyboardButton(text='Создaть новый стикер-пак')],
    [types.KeyboardButton(text='Видео стикер-пaк')],
    [types.KeyboardButton(text='Стaндартный стикер-пак')],
    [types.KeyboardButton(text='Добaвить стикер')],
    [types.KeyboardButton(text='Удaлить стикер')],
    [types.KeyboardButton(text='Удaлить стикер-пак')],
    [types.KeyboardButton(text='Нaзад')]
]
keyboard_help_menu = types.ReplyKeyboardMarkup(keyboard=kb_help, resize_keyboard=True)
