import asyncio
import logging
import os
import shutil
from aiogram import Bot, Dispatcher, types, F
from dotenv import load_dotenv
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup

import convert

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    filename='logging_bot_work.txt',
    filemode='w'
)

# Создание диспетчера
BOT_TOKEN = os.getenv('TOKEN_BOT')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Создание временных файлов
TEMP_FOLDER = "temp_files"
os.makedirs(TEMP_FOLDER, exist_ok=True)


class VideoState(StatesGroup):
    create_video = State()



@dp.message(Command('start'))
async def start(message: types.Message):
    # Запуск бота, после команды старт отправляет кнопки.
    global kb
    global keyboard
    kb = [
        [types.KeyboardButton(text='Сделать видео-стикер')],
        [types.KeyboardButton(text='Сделать видео-эмоджи')]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await message.answer('Что бы вы хотели сделать?', reply_markup=keyboard)


@dp.message(F.text == 'Сделать видео-стикер')
async def create_video_sticker(message: types.Message, state: FSMContext):
    global conversion_format
    conversion_format = 'sticker'
    await message.answer('Отправьте видео.')
    await state.set_state(VideoState.create_video)



@dp.message(F.text == 'Сделать видео-эмоджи')
async def create_video_emoji(message: types.Message, state: FSMContext):
    global conversion_format
    conversion_format = 'emoji'
    await message.answer('Отправьте видео.')
    await state.set_state(VideoState.create_video)


@dp.message(VideoState.create_video, F.video)
async def send_video_sticker(message: types.Message, bot: Bot, state: FSMContext):
    video_file = os.path.join(TEMP_FOLDER, f'video_{message.from_user.id}.mp4')
    await bot.download(message.video, destination=video_file)
    convert_video = await asyncio.to_thread(convert.convert_video, video_file, conversion_format)
    with open(convert_video, 'rb') as video:
        await message.answer_video(types.BufferedInputFile(video.read(), filename='convert_video.webm'))
        await state.clear()
    shutil.rmtree(TEMP_FOLDER)


@dp.message(VideoState.create_video)
async def unscripted_event_handler(message: types.Message):
    # Обработчик событий не по сценарию, отправляет кнопки
    await message.answer('Выберите, что нужно сделать?', reply_markup=keyboard)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
