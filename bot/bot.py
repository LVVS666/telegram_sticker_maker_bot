import logging
import os
import asyncio
import shutil
import logging
from aiogram import Bot, Dispatcher, types, F
from dotenv import load_dotenv
from aiogram.filters.command import Command


import convert

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    filename='logging_bot_work.txt',
    filemode='w'
)

'''Создание диспетчера'''
BOT_TOKEN = os.getenv('TOKEN_BOT')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


'''Создание временных файлов'''
TEMP_FOLDER = "temp_files"
os.makedirs(TEMP_FOLDER, exist_ok=True)


@dp.message(Command('start'))
async def start(message: types.Message):
    '''Запуск бота, после команды старт отправляет кнопки.'''
    kb = [
        [types.KeyboardButton(text='Сделать видео-стикер')],
        [types.KeyboardButton(text='Сделать видео-эмоджи')]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await message.answer('Что бы вы хотели сделать?', reply_markup=keyboard)


@dp.message(F.text == 'Сделать видео-стикер')
async def create_video_sticker(message: types.Message):
    await message.answer('Отправьте видео.')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
