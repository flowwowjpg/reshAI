"""
Обработчик изображений (скриншотов заданий)
"""
from aiogram import Router, F, Bot
from aiogram.types import Message
import logging

from services.db_service import db_service
from services.ai_service import ai_service
from services.ocr_service import ocr_service
from config import config

router = Router()
logger = logging.getLogger(__name__)


def split_message(text: str, max_length: int = 4096) -> list[str]:
    """Разбивает длинное сообщение на части"""
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current_part = ""
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        if len(paragraph) > max_length:
            if current_part:
                parts.append(current_part.strip())
                current_part = ""
            sentences = paragraph.replace('. ', '.|').split('|')
            for sentence in sentences:
                if len(current_part) + len(sentence) + 1 <= max_length:
                    current_part += sentence + " "
                else:
                    if current_part:
                        parts.append(current_part.strip())
                    current_part = sentence + " "
        else:
            if len(current_part) + len(paragraph) + 2 <= max_length:
                current_part += paragraph + "\n\n"
            else:
                parts.append(current_part.strip())
                current_part = paragraph + "\n\n"
    
    if current_part.strip():
        parts.append(current_part.strip())
    
    return parts


@router.message(F.photo)
async def handle_image_task(message: Message, bot: Bot) -> None:
    """Обработка изображения с заданием"""
    
    # Отправляем сообщение о обработке
    processing_msg = await message.answer("📷 Распознаю текст на изображении...")
    
    try:
        # Получаем файл изображения (берём самое большое разрешение)
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        
        # Скачиваем изображение
        image_bytes = await bot.download_file(file.file_path)
        image_data = image_bytes.read()
        
        # Распознаём текст
        extracted_text = await ocr_service.extract_text(image_data)
        
        if not extracted_text:
            await processing_msg.edit_text(
                "❌ Не удалось распознать текст на изображении.\n\n"
                "💡 Советы:\n"
                "• Используй более чёткий скриншот\n"
                "• Убедись, что текст хорошо виден\n"
                "• Попробуй обрезать лишние части изображения\n"
                "• Или напиши задание текстом"
            )
            return
        
        # Проверка длины распознанного текста
        if len(extracted_text) > config.MAX_INPUT_LENGTH:
            await processing_msg.edit_text(
                f"❌ Распознанный текст слишком длинный ({len(extracted_text)} символов).\n"
                "Попробуй отправить изображение с меньшим количеством текста."
            )
            return
        
        # Показываем распознанный текст
        await processing_msg.edit_text(
            f"📝 Распознанный текст:\n\n{extracted_text[:500]}{'...' if len(extracted_text) > 500 else ''}\n\n"
            "🤖 Думаю над решением..."
        )
        
        # Получаем/создаём пользователя
        user_id = await db_service.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        
        # Логируем запрос
        request_id = await db_service.log_request(
            user_id, 
            f"[IMAGE OCR] {extracted_text}"
        )
        
        # Получаем решение от ИИ
        solution = await ai_service.get_solution(extracted_text)
        
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
                await message.answer(f"📄 Продолжение ({i+1}/{len(parts)}):\n\n{part}")
                
    except Exception as e:
        logger.error(f"Ошибка обработки изображения: {e}")
        await processing_msg.edit_text(
            "❌ Произошла ошибка при обработке изображения. Попробуй ещё раз."
        )


@router.message(F.document)
async def handle_document(message: Message) -> None:
    """Обработка документов (не поддерживается)"""
    await message.answer(
        "📎 Я пока не умею обрабатывать документы.\n\n"
        "Пожалуйста, отправь:\n"
        "• Текст задания\n"
        "• Или фото/скриншот"
    )
