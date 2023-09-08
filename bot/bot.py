import logging
import os
import asyncio
import shutil

from aiogram import Bot, Dispatcher, types
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
dp = Dispatcher(bot)

'''Логирование событий бота'''
logging_middleware = LoggingMiddleware()
dp.middleware.setup(logging_middleware)

'''Создание временных файлов'''
TEMP_FOLDER = "temp_files"
os.makedirs(TEMP_FOLDER, exist_ok=True)



async def send_buttons(message: types.Message):
    '''Создание кнопок для выбора действий.'''

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    video_sticker_button = types.KeyboardButton(text='Сделать видео-стикер')
    emoji_sticker_button = types.KeyboardButton(text='Сделать видео-эмоджи')
    keyboard.add(video_sticker_button, emoji_sticker_button)

    await message.answer(
        'Что бы вы хотели сделать?',
        reply_markup=keyboard
    )


@dp.message_handler(lambda message: message.text in ['Сделать видео-стикер', 'Сделать видео-эмоджи'])
async def create_video(message: types.Message):
    '''После нажатия кнопки бот приглашает отправить файл'''

    if message.text == 'Сделать видео-стикер':
        conversion_format = 'sticker'
    else:
        conversion_format = 'emoji'
    await message.answer('Отправьте файл')


@dp.message_handler(content_types=types.ContentType.VIDEO)
async def process_file(message: types.Message):
    '''Бот получает файл, использует метод конвертирования файла и возвращает файл в нужном формате'''

    conversion_format = 'sticker' if message.text == 'Сделать видео-стикер' else 'emoji'
    video_file = os.path.join(TEMP_FOLDER, f'video_{message.from_user.id}.mp4')
    await message.video.download(video_file)
    converted_video = await asyncio.to_thread(convert.convert_video, video_file, conversion_format)
    await message.answer('Ожидайте создания...')
    with open(converted_video, 'rb') as video:
        await message.reply_video(video)
    shutil.rmtree(TEMP_FOLDER)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    '''Запуск бота, после команды старт отправляет кнопки.'''

    await send_buttons(message)


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
