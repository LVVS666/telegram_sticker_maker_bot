import os
import subprocess
from io import BytesIO

from PIL import Image
from rembg import remove

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


def convert_image(image):
    input_image = Image.open(image)
    output_image = remove(input_image)
    output_image = output_image.resize((512, 512))
    image_bytes = BytesIO()
    output_image.save(image_bytes, format="PNG")
    return image_bytes.getvalue()
