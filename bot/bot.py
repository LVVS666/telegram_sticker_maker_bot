import logging
import os
import asyncio
import shutil

from aiogram import Bot, Dispatcher, types, F
from dotenv import load_dotenv
from aiogram.contrib.middlewares.logging import LoggingMiddleware

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

'''Логирование событий бота'''
logging_middleware = LoggingMiddleware()
dp.middleware.setup(logging_middleware)

'''Создание временных файлов'''
TEMP_FOLDER = "temp_files"
os.makedirs(TEMP_FOLDER, exist_ok=True)


@dp.message(Commands=('start'))
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
    conversion_format = 'sticker'
    video_file = os.path.join(TEMP_FOLDER, f'video_{message.from_user.id}.mp4')
    await message.video.download(video_file)
    converted_video = await asyncio.to_thread(convert.convert_video, video_file, conversion_format)
    await message.answer('Ожидайте создания...')
    with open(converted_video, 'rb') as video:
        await message.reply_video(video)
    shutil.rmtree(TEMP_FOLDER)

@dp.message(F.text == 'Сделать видео-эмоджи')
async def create_video_sticker(message: types.Message):
    conversion_format = 'emoji'
    video_file = os.path.join(TEMP_FOLDER, f'video_{message.from_user.id}.mp4')
    await message.video.download(video_file)
    converted_video = await asyncio.to_thread(convert.convert_video, video_file, conversion_format)
    await message.answer('Ожидайте создания...')
    with open(converted_video, 'rb') as video:
        await message.reply_video(video)
    shutil.rmtree(TEMP_FOLDER)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
