# Telegram sticker maker bot
```
Это телеграм бот для конвертации видео в формат для создания видео-стикеров и статичных-стикеров.
```

## Использование:
```
1. Откройте Telegram и найдите бота @TStickMBot.
2. Бот предложит вам выбрать создать видео-стикер пак или статичный пак.
3. Придумайте название и короткий адрес для стикер-пака.
4. Отправьте ему видео-файл или изображение, бот.
5. Отправьте подходящий эмодзи для стикера.
6. Бот автоматически конвертирует видео в формат .webm или изображение в формат .png и отправит вам готовый стикер и создаст пак.
```
### Поддерживаемые форматы:

Бот поддерживает следующие форматы видео:
```
MP4, AVI, WMV и MOV. Другие форматы могут быть не совместимы и не будут конвертироваться.
```

## Подготовка и запуск проекта
### Склонировать репозиторий:
```
git clone https://github.com/LVVS666/telegram_sticker_maker_bot.git
```
### Установить зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
### Создать файл .env
```
В нём созать переменную TOKEN_BOT = 'токен_вашего_бота'
```
### Перед запуском проекта нужно установить ffmpeg
для Mac OS:
```
brew install ffmpeg 
```
```
В файле convert.py, изменить путь до установленного ffmpeg
```
### Запуск проекта
Для запуска перейдите в терминал среды разработки и введите команду:
 ```
 python bot.py
 ```
