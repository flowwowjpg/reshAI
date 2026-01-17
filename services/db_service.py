"""
Сервис работы с базой данных SQLite
"""
import aiosqlite
from datetime import datetime
from typing import Optional
import os

from config import config


class DatabaseService:
    """Асинхронный сервис для работы с SQLite"""
    
    def __init__(self):
        self.db_path = config.DATABASE_PATH
    
    async def init_db(self) -> None:
        """Инициализация базы данных и создание таблиц"""
        # Создаём директорию если не существует
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица запросов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    request_text TEXT NOT NULL,
                    response_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Индексы для быстрого поиска
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_telegram_id 
                ON users (telegram_id)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_requests_user_id 
                ON requests (user_id)
            """)
            
            await db.commit()
    
    async def get_or_create_user(
        self, 
        telegram_id: int, 
        username: Optional[str] = None,
        first_name: Optional[str] = None
    ) -> int:
        """Получить или создать пользователя, возвращает user_id"""
        async with aiosqlite.connect(self.db_path) as db:
            # Проверяем существует ли пользователь
            cursor = await db.execute(
                "SELECT id FROM users WHERE telegram_id = ?",
                (telegram_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                return row[0]
            
            # Создаём нового пользователя
            cursor = await db.execute(
                """INSERT INTO users (telegram_id, username, first_name) 
                   VALUES (?, ?, ?)""",
                (telegram_id, username, first_name)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def log_request(
        self, 
        user_id: int, 
        request_text: str, 
        response_text: Optional[str] = None
    ) -> int:
        """Логирование запроса в БД, возвращает request_id"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO requests (user_id, request_text, response_text) 
                   VALUES (?, ?, ?)""",
                (user_id, request_text, response_text)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def update_response(self, request_id: int, response_text: str) -> None:
        """Обновление ответа в запросе"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE requests SET response_text = ? WHERE id = ?",
                (response_text, request_id)
            )
            await db.commit()
    
    async def get_user_stats(self, telegram_id: int) -> dict:
        """Получить статистику пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """SELECT COUNT(*) FROM requests r
                   JOIN users u ON r.user_id = u.id
                   WHERE u.telegram_id = ?""",
                (telegram_id,)
            )
            row = await cursor.fetchone()
            return {"total_requests": row[0] if row else 0}


# Singleton экземпляр сервиса
db_service = DatabaseService()
