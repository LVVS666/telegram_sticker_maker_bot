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
    global conversion_format
    conversion_format = 'sticker'
    await message.answer('Отправьте видео.')

@dp.message(F.text == 'Сделать видео-эмоджи')
async def create_video_sticker(message: types.Message):
    global conversion_format
    conversion_format = 'emoji'
    await message.answer('Отправьте видео.')

@dp.message(F.video)
async def send_video_sticker(message: types.Message, bot: Bot):
    video_file = os.path.join(TEMP_FOLDER, f'video_{message.from_user.id}.mp4')
    await bot.download(message.video, destination=video_file)
    convert_video = await asyncio.to_thread(convert.convert_video, video_file, conversion_format)
    with open(convert_video, 'rb') as video:
        await message.answer_video(types.BufferedInputFile(video.read(), filename='convert_video.webm'))
    shutil.rmtree(TEMP_FOLDER)



async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
