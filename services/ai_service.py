"""
Сервис взаимодействия с AI API
Универсальный модуль для работы с различными AI провайдерами
"""
import httpx
import logging
from typing import Optional

from config import config

logger = logging.getLogger(__name__)


class AIService:
    """Сервис для получения решений от ИИ"""
    
    # Системный промпт для ИИ
    SYSTEM_PROMPT = """Ты — умный помощник по домашним заданиям (ГДЗ). 
Твоя задача:
1. Определить предмет задания (математика, физика, химия, русский язык, литература, история, биология, география, английский и т.д.)
2. Подробно решить задание с объяснением каждого шага
3. Дать финальный ответ

Формат ответа:
📚 Предмет: [название предмета]

📝 Решение:
[подробное пошаговое решение с объяснениями]

✅ Ответ: [финальный ответ]

Важно:
- Объясняй понятным языком
- Используй формулы где нужно
- Если задание неполное или непонятное — уточни что не хватает
- Будь дружелюбным и поддерживающим"""

    def __init__(self):
        self.api_url = config.AI_API_URL
        self.api_key = config.AI_API_KEY
        self.model = config.AI_MODEL
        self.timeout = config.REQUEST_TIMEOUT
    
    async def get_solution(self, task_text: str) -> Optional[str]:
        """
        Получить решение задания от ИИ
        
        Args:
            task_text: Текст задания
            
        Returns:
            Решение от ИИ или None при ошибке
        """
        try:
            # Формируем запрос в формате OpenAI API
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": task_text}
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )
                
                if response.status_code != 200:
                    logger.error(f"AI API ошибка {response.status_code}: {response.text}")
                    return None
                
                data = response.json()
                return self._extract_response(data)
                    
        except httpx.RequestError as e:
            logger.error(f"Ошибка сети при запросе к AI: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка AI сервиса: {e}")
            return None
    
    def _extract_response(self, data: dict) -> Optional[str]:
        """
        Извлечение текста ответа из JSON
        Поддерживает формат OpenAI и совместимые API
        """
        try:
            # Формат OpenAI / Claude API
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            
            # Альтернативный формат (некоторые API)
            if "response" in data:
                return data["response"]
            
            if "content" in data:
                return data["content"]
            
            logger.error(f"Неизвестный формат ответа AI: {data.keys()}")
            return None
            
        except (KeyError, IndexError) as e:
            logger.error(f"Ошибка парсинга ответа AI: {e}")
            return None


# Singleton экземпляр сервиса
ai_service = AIService()
