import asyncio
import logging
import os
import shutil
import subprocess

from aiogram import Bot, Dispatcher, types, F
from dotenv import load_dotenv
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup


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
    create_video = State()
    create_image = State()
    emoji_in_sticker = State()
    name_sticker_pack = State()
    title_sticker_pack = State()



@dp.message(Command('start'))
async def start(message: types.Message):
    '''
    Запуск бота, после команды старт отправляет кнопки.
    '''

    await message.answer('Что бы вы хотели сделать?', reply_markup=keyboards.kb_main_menu)


@dp.message(F.text == 'Выбрать готовый стикер-пак')
async def all_sticker_pack(message: types.Message):
    '''Отправляется список всех созданных стикер-паков'''
    pass


@dp.message(F.text == 'Создать новый стикер-пак')
async def create_new_sticker_pack(message: types.Message):
    '''Выбор создаваемого стикерпака'''

    await message.answer('Какой стикерпак вы бы хотели создать?', reply_markup=keyboards.kb_new_stickerpack)


@dp.message(F.text == ['Видео стикер-пак', 'Стандартный стикер-пак'])
async def type_sticker_pack(message: types.Message, state: FSMContext):
    '''Название для стикер-пака'''
    await state.set_state(VideoState.name_sticker_pack)
    await message.answer('Придумайте название для стикер-пака.')


@dp.message(VideoState.name_sticker_pack)
async def create_name_sticker_pack(message: types.Message, state: FSMContext):
    '''Адрес ссылки на стикер-пак'''
    await state.update_data(name_sticker_pack=message.text)
    await message.answer('Придумайте короткий адрес для стикер-пака.')
    await state.set_state(VideoState.title_sticker_pack)


@dp.message(VideoState.title_sticker_pack)
async def title_sticker_pack(message: types.Message, state: FSMContext):
    await state.update_data(title_sticker_pack=message.text)
    await message.answer('Стикерпак успешно создан!')
    await state.clear()





# @dp.message(F.text == 'Сделать видео-стикер')
# async def create_video_sticker(message: types.Message, state: FSMContext):
#     global conversion_format
#     conversion_format = 'sticker'
#     await message.answer('Отправьте видео.')
#     await state.set_state(VideoState.create_video)
#
#
#
# @dp.message(F.text == 'Сделать видео-эмоджи')
# async def create_video_emoji(message: types.Message, state: FSMContext):
#     global conversion_format
#     conversion_format = 'emoji'
#     await message.answer('Отправьте видео.')
#     await state.set_state(VideoState.create_video)


# @dp.message(VideoState.create_video, F.video)
# async def send_video_sticker(message: types.Message, bot: Bot, state: FSMContext):
#     '''
#     Обработка видео-файла присланного пользователем и отправка конвертированного видео-файла назад пользователю
#     '''
#
#     video_file = os.path.join(TEMP_FOLDER, f'video_{message.from_user.id}.mp4')
#     await bot.download(message.video, destination=video_file)
#     convert_video = await asyncio.to_thread(convert.convert_video, video_file, conversion_format)
#     with open(convert_video, 'rb') as video:
#         await message.answer_video(types.BufferedInputFile(video.read(), filename='convert_video.webm'))
#         logging.info(f'Конвертация файла для пользователя: {message.from_user.id} выполнена успешно')
#         await state.clear()
#     shutil.rmtree(TEMP_FOLDER)

#
# @dp.message(VideoState.create_video)
# async def unscripted_event_handler(message: types.Message):
#     # Обработчик событий не по сценарию, отправляет кнопки
#     await message.answer('Неверный формат сообщения, попробуйте еще раз отправить видео-файл')


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
