import logging
import os

from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    filename='logging_bot_work.txt',
    filemode='w'
)

BOT_TOKEN = os.getenv('TOKEN_BOT')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


async def send_buttons(message: types.Message):

    '''Создание кнопок для выбора действий.'''

    keyboard = types.InlineKeyboardMarkup()
    button_video_sticker = types.InlineKeyboardButton(''
                                                      'Создать видео-стикер',
                                                      callback_data='video_sticker'
                                                      )
    button_sticker = types.InlineKeyboardButton(''
                                                'Создать стикер',
                                                callback_data='sticker'
                                                )
    keyboard.add(button_video_sticker, button_sticker)

    await message.answer(
        'Что бы вы хотели сделать?',
        reply_markup=keyboard
    )


@dp.callback_query_handler(lambda callback_query: True)
async def process_buttons(callback_query: types.CallbackQuery):

    '''Обработка запроса от кнопок'''

    data = callback_query.data
    if data == 'video_sticker':
        await callback_query.answer('Тут функция конвертер видео')
    elif data == 'sticker':
        await callback_query.answer('Тут функция обработчик фото')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):

    '''Запуск бота, после команды старт отправляет кнопки.'''

    await send_buttons(message)


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
