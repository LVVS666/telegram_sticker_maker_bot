import subprocess

def convert(video):
    output_video_path = 'output_video.webm'

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

convert('IMG_0050.MOV')


