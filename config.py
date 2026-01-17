"""
Конфигурация бота - загрузка переменных окружения
"""
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()


class Config:
    """Класс конфигурации с валидацией"""
    
    # Telegram
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # AI API
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_API_URL: str = os.getenv("AI_API_URL", "https://api.openai.com/v1/chat/completions")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-3.5-turbo")
    
    # Лимиты
    MAX_MESSAGE_LENGTH: int = 4096  # Лимит Telegram
    MAX_INPUT_LENGTH: int = 4000    # Максимальная длина входного текста
    REQUEST_TIMEOUT: int = 60       # Таймаут запроса к AI API (секунды)
    
    # Пути
    DATABASE_PATH: str = "database/gdz.db"
    
    @classmethod
    def validate(cls) -> None:
        """Проверка обязательных переменных"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен в .env файле")
        if not cls.AI_API_KEY:
            raise ValueError("AI_API_KEY не установлен в .env файле")


config = Config()
