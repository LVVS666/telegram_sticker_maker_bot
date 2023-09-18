import os
import subprocess

from bot import TEMP_FOLDER


def convert_video(video, conversion_format):
    '''Функция принимает видео файл и возвращает его в формате webm с параметрами видео-стикера'''

    output_video_path = os.path.join(TEMP_FOLDER, "converted_video.webm")

    # Команда для конвертации видео в формат WebM с VP9 кодеком и без аудио
    command = [
        '/opt/homebrew/bin/ffmpeg',
        '-i', video,
        '-c:v', 'libvpx-vp9',
        '-an',  # Отключение аудио
        '-vf', 'scale=512:512:force_original_aspect_ratio=decrease',  # Изменение размера и обрезка под размер
        '-t', '3',  # Продолжительность 3 секунды
        '-f', 'webm',
        output_video_path
    ]
    if conversion_format == 'emoji':
        command_emoji = command.copy()
        command_emoji[7] = 'scale=100:-1,crop=100:100'
        subprocess.run(command_emoji, check=True)
        return output_video_path
    subprocess.run(command, check=True)
    return output_video_path





