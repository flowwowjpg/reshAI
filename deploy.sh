#!/bin/bash
# Скрипт установки бота на Ubuntu/Debian сервер

echo "🚀 Установка ИИ-ГДЗ бота..."

# Обновляем пакеты
sudo apt update

# Устанавливаем Python и pip
sudo apt install -y python3 python3-pip python3-venv

# Устанавливаем Tesseract OCR с русским и английским языками
sudo apt install -y tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng

# Создаём виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

echo "✅ Установка завершена!"
echo ""
echo "Следующие шаги:"
echo "1. Отредактируй .env файл с твоими ключами"
echo "2. Запусти бота: source venv/bin/activate && python bot.py"
echo ""
echo "Для запуска в фоне используй:"
echo "nohup python bot.py > bot.log 2>&1 &"
