import os
import subprocess

from bot import TEMP_FOLDER


def convert_video(video):
    '''Функция принимает видео файл и возвращает его в формате webm с параметрами видео-стикера'''

    output_video_path = os.path.join(TEMP_FOLDER, "converted_video.webm")

    # Команда для конвертации видео в формат WebM с VP9 кодеком и без аудио
    command = [
        '/opt/homebrew/bin/ffmpeg',
        '-i', video,
        '-c:v', 'libvpx-vp9',
        '-an',  # Отключение аудио
        '-vf', 'scale=512:512',  # Изменение размера
        '-t', '3',  # Продолжительность 3 секунды
        '-f', 'webm',
        output_video_path
    ]

    subprocess.run(command, check=True)
    return output_video_path




