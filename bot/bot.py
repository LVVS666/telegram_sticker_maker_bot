import asyncio
import logging
import os
import shutil
import subprocess
from io import BytesIO

from aiogram import Bot, Dispatcher, types, F
from dotenv import load_dotenv
from aiogram.types import FSInputFile
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram.methods.create_new_sticker_set import CreateNewStickerSet

import convert
import keyboards

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
    emoji_in_sticker = State()
    name_sticker_pack = State()
    title_sticker_pack = State()
    video_pack = State()
    static_pack = State()
    video = State()
    image = State()
    delete_sticker_state = State()
    add_sticker_state = State()


@dp.message(Command('start'))
async def start(message: types.Message):
    '''
    Запуск бота, после команды старт отправляет кнопки.
    '''

    await message.answer('Что бы вы хотели сделать?', reply_markup=keyboards.keyboard_main_menu)


@dp.message(F.text == 'Создать новый стикер-пак')
async def create_new_sticker_pack(message: types.Message, state: FSMContext):
    '''Выбор создаваемого стикерпака'''

    await message.answer('Какой стикерпак вы бы хотели создать?', reply_markup=keyboards.keyboard_new_stickerpack_menu)
    await state.set_state(VideoState.video_pack)
    await state.set_state(VideoState.static_pack)


@dp.message((F.text == 'Видео стикер-пак') | (F.text == 'Стандартный стикер-пак'))
async def type_sticker_pack(message: types.Message, state: FSMContext):
    '''Название для стикер-пака'''
    if message.text == 'Видео стикер-пак':
        await state.update_data(video_pack=message.text)
    else:
        await state.update_data(static_pack=message.text)
    await state.set_state(VideoState.name_sticker_pack)
    await message.answer('Придумайте название для стикер-пака.')


@dp.message(VideoState.name_sticker_pack)
async def create_name_sticker_pack(message: types.Message, state: FSMContext):
    '''Адрес ссылки на стикер-пак'''
    await state.update_data(name_sticker_pack=message.text + '_by_TSickMBot')
    await message.answer('Придумайте короткий адрес для стикер-пака.')
    await state.set_state(VideoState.title_sticker_pack)


@dp.message(VideoState.title_sticker_pack)
async def title_sticker_pack(message: types.Message, state: FSMContext):
    """Эмоджи для стикер-пака"""
    await state.update_data(title_sticker_pack=message.text)
    await message.answer('Отправьте эмоджи подходящий стикеру')
    await state.set_state(VideoState.emoji_in_sticker)


'''Работа с меню стикерпака'''


@dp.message(F.text == 'Выбрать готовый стикер-пак')
async def all_sticker_pack(message: types.Message):
    '''Отправляется список всех созданных стикер-паков'''
    await message.answer('Выбрать действие', reply_markup=keyboards.keyboard_stickerpack_menu)
    pass


@dp.message(F.text == 'Удалить стикер')
async def delete_sticker(message: types.Message, state: FSMContext):
    '''Удаление стикера из стикер пака'''
    await state.set_state(VideoState.delete_sticker_state)
    await message.answer('Отправьте стикер для удаления')


@dp.message(VideoState.delete_sticker_state)
async def delete_sticker_on(message: types.Sticker, state: FSMContext):
    '''Принятие стикера для удаления'''
    await state.clear()


@dp.message(F.text == 'Удалить стикер-пак')
async def delete_sticker_pack(message: types.Message):
    '''Удаление стикер-пака'''
    pass


@dp.message(F.text == 'Добавить стикер')
async def create_sticker(message: types.Message, state: FSMContext):
    '''Принимает запрос на добавление стикера'''
    await state.set_state(VideoState.add_sticker_state)
    await message.answer('Отправьте файл для создания стикера.')


@dp.message(VideoState.add_sticker_state, F.Video)
async def add_sticker_video(message: types.Message, bot: Bot, state: FSMContext):
    '''Принимает видео для обработки в видео стикер'''
    video_file = os.path.join(TEMP_FOLDER, f'video_{message.from_user.id}.mp4')
    await bot.download(message.video, destination=video_file)
    converted_video = await asyncio.to_thread(convert.convert_video, video_file)
    # Добавить в метод создание стикера converted_video
    shutil.rmtree(TEMP_FOLDER)
    await state.set_state(VideoState.emoji_in_sticker)
    await message.answer('Отправьте эмоджи подходящий стикеру')


@dp.message(VideoState.add_sticker_state, F.Image)
async def add_sticker_image(message: types.Message, bot: Bot, state: FSMContext):
    '''Принимает фото для обработки в стикер'''
    image_file = os.path.join(TEMP_FOLDER, f'image_{message.from_user.id}.jpg')
    await bot.download(message.photo[-1].file_id, destination=image_file)
    converted_image = await asyncio.to_thread(convert.convert_image, image_file)
    # Добавить converted_image в add_sticker
    shutil.rmtree(TEMP_FOLDER)
    await state.set_state(VideoState.emoji_in_sticker)
    await message.answer('Отправьте эмоджи подходящий стикеру')


@dp.message(VideoState.add_sticker_state)
async def unscripted_event_handler(message: types.Message):
    '''Обработчик событий не по сценарию, отправляет кнопки'''
    await message.answer('Неверный формат сообщения, попробуйте еще раз отправить видео-файл')


@dp.message(VideoState.emoji_in_sticker, F.Emoji)
async def add_sticker_in_emoji(message: types.Message, state: FSMContext):
    '''Принимает эмоджи'''
    await message.answer('Стикер успешно создан')
    await state.clear()
    # Вернуться в меню стикер-пака


async def main():
    while True:
        try:
            await dp.start_polling(bot)
            logging.info('Бот запущен.')
        except ConnectionError:
            logging.error('Произошла ошибка соединения с сервером')
            # Перезапуск бота.
            restart_bot = subprocess.Popen(['python', 'bot.py'])
            restart_bot.wait()


if __name__ == '__main__':
    asyncio.run(main())
