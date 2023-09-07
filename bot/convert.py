import os
import subprocess

from bot import TEMP_FOLDER


def convert_video(video):
    output_video_path = os.path.join(TEMP_FOLDER, "converted_video.mp4")


    # Команда для конвертации видео в формат WebM с VP9 кодеком и без аудио
    command = [
        '/opt/homebrew/bin/ffmpeg',
        '-i', video,
        '-c:v', 'libvpx-vp9',
        '-an',  # Отключение аудио
        '-vf', 'scale=100:100',  # Изменение размера
        '-t', '3',  # Продолжительность 3 секунды
        '-f', 'webm',
        output_video_path
    ]

    subprocess.run(command, check=True)



