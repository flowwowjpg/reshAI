#!/usr/bin/env bash
# Скрипт сборки для Render

apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng
pip install -r requirements.txt
