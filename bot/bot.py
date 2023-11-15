import asyncio
import logging
import os
import shutil
import subprocess
import tempfile
from io import BytesIO

from aiogram import Bot, Dispatcher, types, F
from dotenv import load_dotenv
from aiogram.types import FSInputFile
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram.methods import (CreateNewStickerSet,
                             GetStickerSet,
                             SendSticker,
                             AddStickerToSet,
                             DeleteStickerSet,
                             DeleteStickerFromSet)

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

async def create_sticker_set(user_id, name, title, stickers, sticker_format):
    """Создание стикерпака"""
    create_set = await bot(CreateNewStickerSet(
        user_id=user_id,
        name=name,
        title=title,
        stickers=stickers,
        sticker_format=sticker_format
    ))
    return create_set

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


@dp.message((F.text == 'Видео стикер-пак') | (F.text == 'Стандартный стикер-пак') | (F.text == 'Назад'))
async def type_sticker_pack(message: types.Message, state: FSMContext):
    '''Название для стикер-пака'''
    if message.text == 'Видео стикер-пак':
        await state.update_data(video_pack=True)
    elif message.text == 'Назад':
        return await start(message)
    elif message.text == 'Стандартный стикер-пак':
        await state.update_data(static_pack=True)
    await state.set_state(VideoState.name_sticker_pack)
    await message.answer('Придумайте название для стикер-пака.')


@dp.message(VideoState.name_sticker_pack)
async def create_name_sticker_pack(message: types.Message, state: FSMContext):
    '''Адрес ссылки на стикер-пак'''
    await state.update_data(name_sticker_pack=message.text + '_by_TStickMBot')
    await message.answer('Придумайте короткий адрес для стикер-пака.')
    await state.set_state(VideoState.title_sticker_pack)


@dp.message(VideoState.title_sticker_pack)
async def title_sticker_pack(message: types.Message, state: FSMContext):
    """Файлы для стикеров"""
    await state.update_data(title_sticker_pack=message.text)
    data = await state.get_data()
    if 'video_pack' in data:
        await state.set_state(VideoState.video)
    elif 'static_pack' in data:
        await state.set_state(VideoState.image)
    await message.answer('Отправьте файл для создания стикера.')

@dp.message(VideoState.video)
async def add_sticker_video(message: types.Message, bot: Bot, state: FSMContext):
    """Принимает видео для обработки в видео стикер"""
    video_file = os.path.join(TEMP_FOLDER, f'video_{message.from_user.id}.mp4')
    await bot.download(message.video, destination=video_file)
    converted_video = await asyncio.to_thread(convert.convert_video, video_file)
    await state.update_data(video=converted_video)
    await message.answer('Отправьте эмоджи подходящий стикеру')
    await state.set_state(VideoState.emoji_in_sticker)


@dp.message(VideoState.image)
async def add_sticker_image(message: types.Message, bot: Bot, state: FSMContext):
    """Принимает фото для обработки в стикер"""
    image_file = os.path.join(TEMP_FOLDER, f'image_{message.from_user.id}.jpg')
    await bot.download(message.photo[-1].file_id, destination=image_file)
    converted_image = await asyncio.to_thread(convert.convert_image, image_file)
    await state.update_data(image=converted_image)
    shutil.rmtree(TEMP_FOLDER)
    await message.answer('Отправьте эмоджи подходящий стикеру')
    await state.set_state(VideoState.emoji_in_sticker)



@dp.message(VideoState.emoji_in_sticker)
async def add_sticker_in_emoji(message: types.Message, state: FSMContext):
    """Принимает эмоджи"""
    await state.update_data(emoji_in_sticker=message.text)
    data = await state.get_data()
    if 'video_pack' in data:
        converted_file = data.get('video')
        sticker_format = 'video'
        with open(converted_file, 'rb') as file:
            sticker_file = FSInputFile(file.name)
    elif 'static_pack' in data:
        converted_file = data.get('image')
        sticker_file = FSInputFile(converted_file)
        sticker_format = 'static'
    name = data['name_sticker_pack']
    title = data['title_sticker_pack']
    stickers = [{'sticker': sticker_file,
                 'emoji_list': [data['emoji_in_sticker']]}]
    await create_sticker_set(
                             user_id=message.from_user.id,
                             name=name,
                             title=title,
                             stickers=stickers,
                             sticker_format=sticker_format
                             )
    shutil.rmtree(TEMP_FOLDER)
    await message.answer('Стикек-пак успешно создан, вот твой стикер')
    get_sticker = await bot(GetStickerSet(
        name=name
    ))
    file_id = get_sticker.stickers[-1].file_id
    await bot(SendSticker(
        chat_id=message.chat.id,
        sticker=file_id
    ))




'''Работа с меню стикерпака'''

#
# @dp.message(F.text == 'Выбрать готовый стикер-пак')
# async def all_sticker_pack(message: types.Message):
#     '''Отправляется список всех созданных стикер-паков'''
#     await message.answer('Выбрать действие', reply_markup=keyboards.keyboard_stickerpack_menu)
#     pass

#
# @dp.message(F.text == 'Удалить стикер')
# async def delete_sticker(message: types.Message, state: FSMContext):
#     '''Удаление стикера из стикер пака'''
#     await state.set_state(VideoState.delete_sticker_state)
#     await message.answer('Отправьте стикер для удаления')
#
#
# @dp.message(VideoState.delete_sticker_state)
# async def delete_sticker_on(message: types.Sticker, state: FSMContext):
#     '''Принятие стикера для удаления'''
#     await state.clear()
#
#
# @dp.message(F.text == 'Удалить стикер-пак')
# async def delete_sticker_pack(message: types.Message):
#     '''Удаление стикер-пака'''
#     pass

#
# @dp.message(F.text == 'Добавить стикер')
# async def create_sticker(message: types.Message, state: FSMContext):
#     '''Принимает запрос на добавление стикера'''
#     await state.set_state(VideoState.add_sticker_state)
#     await message.answer('Отправьте файл для создания стикера.')


@dp.message(VideoState.add_sticker_state)
async def unscripted_event_handler(message: types.Message):
    '''Обработчик событий не по сценарию, отправляет кнопки'''
    await message.answer('Неверный формат сообщения, попробуйте еще раз отправить видео-файл')

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
