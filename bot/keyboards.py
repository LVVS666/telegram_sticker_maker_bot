from aiogram import types


'''Выбор действия в главном меню'''
kb_main_menu = [
        [types.KeyboardButton(text='Выбрать готовый стикер-пак')],
        [types.KeyboardButton(text='Создать новый стикер-пак')]
    ]
keyboard_main_menu = types.ReplyKeyboardMarkup(keyboard=kb_main_menu, resize_keyboard=True)

'''Выбор действия в меню "Создать новый стикер-пак"'''
kb_new_stickerpack = [
        [types.KeyboardButton(text='Видео стикер-пак')],
        [types.KeyboardButton(text='Эмоджи стикер-пак')],
        [types.KeyboardButton(text='Стандартный стикер-пак')]
    ]
keyboard_new_stickerpack_menu = types.ReplyKeyboardMarkup(keyboard=kb_new_stickerpack, resize_keyboard=True)

'''После запроса на имя стикер пака и адрес бот просит отправить файл формата стикера, после просит
отправить соотвествующий эмоджи, дальше перенаправляет в меню стикер пака'''