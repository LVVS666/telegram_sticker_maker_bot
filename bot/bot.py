import asyncio
import logging
import os
import shutil
import subprocess
import tempfile

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
    creating = State()
    adding = State()
    add_video_to_pack = State()
    add_image_to_pack = State()
    add_sticker_to_pack = State()
    delete_pack = State()


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


async def add_sticker_to_set(user_id, name, stickers):
    """Добавление стикера в пак"""
    add_sticker = await bot(AddStickerToSet(
        user_id=user_id,
        name=name,
        sticker=stickers
    ))
    return add_sticker


async def delete_sticker_from_set(sticker):
    """Удаление стикера из пака"""
    del_sticker = await bot(DeleteStickerFromSet(
        sticker=sticker
    ))
    return del_sticker


async def delete_sticker_set(name):
    """Удаление пака"""
    del_pack = await bot(DeleteStickerSet(
        name=name
    ))
    return del_pack


@dp.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    '''
    Запуск бота, после команды старт отправляет кнопки.
    '''

    await message.answer('Что бы вы хотели сделать?', reply_markup=keyboards.keyboard_main_menu)
    await state.set_state(VideoState.creating)
    await state.set_state(VideoState.adding)

@dp.message(F.text == 'Создать новый стикер-пак')
async def create_new_sticker_pack(message: types.Message, state: FSMContext):
    '''Выбор создаваемого стикерпака'''

    await message.answer('Какой стикерпак вы бы хотели создать?', reply_markup=keyboards.keyboard_new_stickerpack_menu)
    await state.update_data(creating=True)
    await state.set_state(VideoState.video_pack)
    await state.set_state(VideoState.static_pack)


@dp.message((F.text == 'Видео стикер-пак') | (F.text == 'Стандартный стикер-пак') | (F.text == 'Назад'))
async def type_sticker_pack(message: types.Message, state: FSMContext):
    '''Название для стикер-пака'''
    if message.text == 'Видео стикер-пак':
        await state.update_data(video_pack=True)
    elif message.text == 'Назад':
        return await start(message, state)
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
        print(data['video_pack'])
        await state.set_state(VideoState.video)
        await message.answer('Отправьте видео-файл продолжительностью не более 3 секунд для создания стикера.')
    elif 'static_pack' in data:
        print(data['static_pack'] + 1)
        await state.set_state(VideoState.image)
        await message.answer('Отправьте изображение для создания стикера.')


@dp.message(VideoState.video)
async def add_sticker_video(message: types.Message, bot: Bot, state: FSMContext):
    """Принимает видео для обработки в видео стикер"""
    video_file = os.path.join(TEMP_FOLDER, f'video_{message.from_user.id}.mp4')
    await bot.download(message.video, destination=video_file)
    converted_video = await asyncio.to_thread(convert.convert_video, video_file)
    await state.update_data(video=converted_video)
    await message.answer('Отправьте эмоджи подходящий видео-стикеру')
    await message.answer('Можно отправить только 1 эмоджи в одном сообщении.')
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
    if len(message.text) > 1:
        first_sticker = message.text[0]
        await state.update_data(emoji_in_sticker=first_sticker)
        await message.answer('Будет выбран первый отправленный эмоджи')
    else:
        await state.update_data(emoji_in_sticker=message.text)
    data = await state.get_data()
    if 'video_pack' in data:
        converted_file = data.get('video')
        sticker_format = 'video'
        with open(converted_file, 'rb') as file:
            sticker_file = FSInputFile(file.name)
    elif 'static_pack' in data:
        converted_file = data.get('image')
        temp_id, temp_filename = tempfile.mkstemp(suffix='.png')
        with open(temp_id, 'wb') as temp_file:
            temp_file.write(converted_file)
        sticker_file = FSInputFile(temp_filename)
        sticker_format = 'static'
    name = data['name_sticker_pack']
    stickers = [{'sticker': sticker_file,
                 'emoji_list': [data['emoji_in_sticker']]}]
    if 'creating' in data:
        title = data['title_sticker_pack']
        await create_sticker_set(
            user_id=message.from_user.id,
            name=name,
            title=title,
            stickers=stickers,
            sticker_format=sticker_format
        )
        await message.answer('Стикер-пак успешно создан, вот твой стикер')
        await state.clear()

    elif 'adding' in data:
        await add_sticker_to_set(
            user_id=message.from_user.id,
            name=name,
            stickers=stickers[0]
        )
        await message.answer('Стикер успешно добавлен, вот твой стикер')
        await state.clear()
    get_sticker = await bot(GetStickerSet(
        name=name
    ))
    file_id = get_sticker.stickers[-1].file_id
    await bot(SendSticker(
        chat_id=message.chat.id,
        sticker=file_id
    ))
    shutil.rmtree(TEMP_FOLDER)




'''Работа с меню стикерпака'''


@dp.message(F.text == 'Выбрать готовый стикер-пак')
async def all_sticker_pack(message: types.Message, state: FSMContext):
    '''Отправляется список всех созданных стикер-паков'''
    await message.answer('Выбрать действие', reply_markup=keyboards.keyboard_stickerpack_menu)
    await state.set_state(VideoState.adding)


@dp.message(F.text == 'Удалить стикер')
async def delete_sticker(message: types.Message, state: FSMContext):
    '''Удаление стикера из стикер пака'''
    await state.set_state(VideoState.delete_sticker_state)
    await message.answer('Отправьте стикер для удаления')


@dp.message(VideoState.delete_sticker_state)
async def del_sticker_from_pack(message: types.Message, state: FSMContext):
    """Принимает стикер и удаляет из пака"""
    await state.update_data(delete_sticker_state=message.sticker)
    data = await state.get_data()
    sticker = data['delete_sticker_state'].file_id
    await delete_sticker_from_set(sticker)
    await message.answer('Твой стикер удален из пака')
    await state.clear()
#
#
# @dp.message(VideoState.delete_sticker_state)
# async def delete_sticker_on(message: types.Sticker, state: FSMContext):
#     '''Принятие стикера для удаления'''
#     await state.clear()
#
#
@dp.message(F.text == 'Удалить стикер-пак')
async def delete_sticker_pack(message: types.Message, state: FSMContext):
    '''Удаление стикер-пака'''
    await state.set_state(VideoState.delete_pack)
    await message.answer('Отправьте стикер из пака который хотите удалить')


@dp.message(VideoState.delete_pack)
async def delete_all_pack(message: types.Message, state: FSMContext):
    """Принимает стикер и удаляет пак"""
    await state.update_data(delete_pack=message.sticker)
    data = await state.get_data()
    name = data['delete_pack'].set_name
    await delete_sticker_set(name)
    await message.answer('Твой пак удален')
    await state.clear()


@dp.message(F.text == 'Добавить стикер')
async def create_sticker(message: types.Message, state: FSMContext):
    '''Принимает запрос на добавление стикера'''
    await state.update_data(adding=True)
    await state.set_state(VideoState.add_sticker_to_pack)
    await message.answer('Отправьте стикер из набора в который хотите добавить.')


@dp.message(VideoState.add_sticker_to_pack)
async def get_name_sticker_pack(message: types.Message, state: FSMContext):
    '''Принимает имя стикер-пака и просит отправить файл для стикера'''
    await state.update_data(add_sticker_to_pack=message.sticker)
    data = await state.get_data()
    name = data['add_sticker_to_pack'].set_name
    await state.update_data(name_sticker_pack=name)
    get_set = await bot(GetStickerSet(name=name))
    print(name)
    if get_set.is_video:
        await message.answer('Ваш стикер-пак содержит видео-стикеры')
        await message.answer('Отправьте видео-файл для стикера')
    else:
        await message.answer('Ваш стикер-пак содержит статичные-стикеры')
        await message.answer('Отправьте изображение для стикера')


@dp.message(F.video | F.photo)
async def get_file(message: types.Message, bot, state: FSMContext):
    """Принимает видео и фото для обработки в стикер"""
    if message.video:
        video_file = os.path.join(TEMP_FOLDER, f'video_{message.from_user.id}.mp4')
        await bot.download(message.video, destination=video_file)
        converted_video = await asyncio.to_thread(convert.convert_video, video_file)
        await state.update_data(video=converted_video)
        await state.update_data(video_pack=True)
        await message.answer('Отправьте эмоджи подходящий видео-стикеру')
    else:
        image_file = os.path.join(TEMP_FOLDER, f'image_{message.from_user.id}.jpg')
        print(message)
        await bot.download(message.photo[-1].file_id, destination=image_file)
        converted_image = await asyncio.to_thread(convert.convert_image, image_file)
        await message.answer('Отправьте эмоджи подходящий стандартному стикеру')
        await state.update_data(image=converted_image)
        await state.update_data(static_pack=True)
    await message.answer('Можно отправить только 1 эмоджи в одном сообщении.')
    await state.set_state(VideoState.emoji_in_sticker)


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
