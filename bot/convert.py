import os
import subprocess
from io import BytesIO

from PIL import Image


from bot import TEMP_FOLDER


def convert_video(video):
    '''
    Функция принимает видео файл и возвращает его в формате webm с параметрами видео-стикера/видео-эмоджи
    '''

    output_video_path = os.path.join(TEMP_FOLDER, "converted_video.webm")

    # Команда для конвертации видео в формат WebM с VP9 кодеком и без аудио
    command = [
        '/opt/homebrew/bin/ffmpeg',  # путь до ffmpeg
        '-i', video,  # Входное видео
        '-c:v', 'libvpx-vp9',  # Видеокодек VP9
        '-an',  # Отключение аудио
        '-vf', 'scale=512:512:force_original_aspect_ratio=decrease',  # Изменение размера и обрезка под размер
        '-t', '3',  # Продолжительность 3 секунды
        '-f', 'webm',
        output_video_path
    ]
    subprocess.run(command, check=True)
    return output_video_path


def convert_image(image_path):
    # Открываем изображение
    input_image = Image.open(image_path).convert('RGBA')
    # Создаем альфа-канал и устанавливаем его в 255 (полностью непрозрачный)
    alpha = Image.new('L', input_image.size, 255)
    input_image.putalpha(alpha)
    # Определяем новые размеры с учетом требований для стикеров
    target_size = 512
    new_width = target_size if input_image.width >= input_image.height else int(target_size * (input_image.width / input_image.height))
    new_height = target_size if input_image.height >= input_image.width else int(target_size * (input_image.height / input_image.width))
    # Изменяем размер изображения
    resized_image = input_image.resize((new_width, new_height), resample=Image.BICUBIC)
    left = int((new_width - target_size) / 2)
    top = int((new_height - target_size) / 2)
    right = int((new_width + target_size) / 2)
    bottom = int((new_height + target_size) / 2)
    cropped_image = resized_image.crop((left, top, right, bottom))
    # Сохраняем изображение в формате PNG
    sticker_bytes = BytesIO()
    cropped_image.save(sticker_bytes, format='PNG', optimize=True, quality=85, exif='')
    return sticker_bytes.getvalue()