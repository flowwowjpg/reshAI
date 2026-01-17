"""
Обработчик текстовых сообщений (заданий)
"""
from aiogram import Router, F
from aiogram.types import Message
import logging

from services.db_service import db_service
from services.ai_service import ai_service
from config import config

router = Router()
logger = logging.getLogger(__name__)


def split_message(text: str, max_length: int = 4096) -> list[str]:
    """
    Разбивает длинное сообщение на части
    Старается разбивать по абзацам или предложениям
    """
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current_part = ""
    
    # Разбиваем по абзацам
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        # Если абзац сам по себе слишком длинный
        if len(paragraph) > max_length:
            # Сохраняем текущую часть если есть
            if current_part:
                parts.append(current_part.strip())
                current_part = ""
            
            # Разбиваем длинный абзац по предложениям
            sentences = paragraph.replace('. ', '.|').split('|')
            for sentence in sentences:
                if len(current_part) + len(sentence) + 1 <= max_length:
                    current_part += sentence + " "
                else:
                    if current_part:
                        parts.append(current_part.strip())
                    current_part = sentence + " "
        else:
            # Проверяем поместится ли абзац
            if len(current_part) + len(paragraph) + 2 <= max_length:
                current_part += paragraph + "\n\n"
            else:
                parts.append(current_part.strip())
                current_part = paragraph + "\n\n"
    
    # Добавляем последнюю часть
    if current_part.strip():
        parts.append(current_part.strip())
    
    return parts


@router.message(F.text)
async def handle_text_task(message: Message) -> None:
    """Обработка текстового задания"""
    task_text = message.text.strip()
    
    # Проверка на пустой текст
    if not task_text:
        await message.answer("❌ Пожалуйста, отправь текст задания.")
        return
    
    # Проверка длины текста
    if len(task_text) > config.MAX_INPUT_LENGTH:
        await message.answer(
            f"❌ Текст слишком длинный. Максимум {config.MAX_INPUT_LENGTH} символов.\n"
            "Попробуй сократить или разбить на части."
        )
        return
    
    # Получаем/создаём пользователя
    user_id = await db_service.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    # Логируем запрос
    request_id = await db_service.log_request(user_id, task_text)
    
    # Отправляем сообщение о обработке
    processing_msg = await message.answer("🤖 Думаю над решением...")
    
    try:
        # Получаем решение от ИИ
        solution = await ai_service.get_solution(task_text)
        
        if not solution:
            await processing_msg.edit_text(
                "❌ Не удалось получить решение. Попробуй ещё раз позже.\n"
                "Возможно, сервис временно недоступен."
            )
            return
        
        # Обновляем ответ в БД
        await db_service.update_response(request_id, solution)
        
        # Удаляем сообщение о обработке
        await processing_msg.delete()
        
        # Разбиваем ответ если он слишком длинный
        parts = split_message(solution, config.MAX_MESSAGE_LENGTH)
        
        for i, part in enumerate(parts):
            if i == 0:
                await message.answer(part)
            else:
                # Небольшая задержка между сообщениями
                await message.answer(f"📄 Продолжение ({i+1}/{len(parts)}):\n\n{part}")
                
    except Exception as e:
        logger.error(f"Ошибка обработки текстового задания: {e}")
        await processing_msg.edit_text(
            "❌ Произошла ошибка при обработке. Попробуй ещё раз."
        )
