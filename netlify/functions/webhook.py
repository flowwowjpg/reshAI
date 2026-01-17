"""
Netlify Function для обработки webhook от Telegram
"""
import os
import sys
import json
import logging

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

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

# Инициализация БД
_db_initialized = False


async def init_db_once():
    """Инициализация БД один раз"""
    global _db_initialized
    if not _db_initialized:
        await db_service.init_db()
        _db_initialized = True
        logger.info("База данных инициализирована")


async def process_update(update_data: dict):
    """Обработка update от Telegram"""
    try:
        await init_db_once()
        update = Update(**update_data)
        await dp.feed_update(bot, update)
    except Exception as e:
        logger.error(f"Ошибка обработки update: {e}", exc_info=True)
        raise


def handler(event, context):
    """Netlify Function handler"""
    import asyncio
    
    try:
        # Проверяем метод
        http_method = event.get('httpMethod', '')
        
        if http_method == 'GET':
            return {
                'statusCode': 200,
                'body': 'Bot is running!'
            }
        
        if http_method != 'POST':
            return {
                'statusCode': 405,
                'body': 'Method not allowed'
            }
        
        # Парсим тело запроса
        body = event.get('body', '{}')
        update_data = json.loads(body)
        
        logger.info(f"Получен update: {update_data.get('update_id')}")
        
        # Обрабатываем update
        asyncio.run(process_update(update_data))
        
        return {
            'statusCode': 200,
            'body': json.dumps({'ok': True})
        }
        
    except Exception as e:
        logger.error(f"Ошибка в handler: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'ok': False, 'error': str(e)})
        }
