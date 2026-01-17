"""
Webhook endpoint для Vercel
"""
import os
import sys
import json
import logging
from http.server import BaseHTTPRequestHandler

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import config
from handlers import setup_routers
from services.db_service import db_service

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
dp.include_router(setup_routers())

# Инициализация БД (выполняется один раз)
_db_initialized = False


async def init_db_once():
    """Инициализация БД один раз"""
    global _db_initialized
    if not _db_initialized:
        await db_service.init_db()
        _db_initialized = True
        logger.info("База данных инициализирована")


class handler(BaseHTTPRequestHandler):
    """Обработчик webhook запросов от Telegram"""
    
    def do_POST(self):
        """Обработка POST запросов"""
        try:
            # Читаем тело запроса
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            # Парсим JSON
            update_data = json.loads(body)
            logger.info(f"Получен update: {update_data.get('update_id')}")
            
            # Обрабатываем update
            import asyncio
            asyncio.run(self.process_update(update_data))
            
            # Отправляем ответ
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
            
        except Exception as e:
            logger.error(f"Ошибка обработки webhook: {e}", exc_info=True)
            self.send_response(500)
            self.end_headers()
    
    async def process_update(self, update_data: dict):
        """Асинхронная обработка update"""
        try:
            # Инициализируем БД если нужно
            await init_db_once()
            
            # Создаём объект Update
            update = Update(**update_data)
            
            # Обрабатываем через диспетчер
            await dp.feed_update(bot, update)
            
        except Exception as e:
            logger.error(f"Ошибка обработки update: {e}", exc_info=True)
    
    def do_GET(self):
        """Обработка GET запросов (для проверки работоспособности)"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is running!")
