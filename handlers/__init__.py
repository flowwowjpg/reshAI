"""
Обработчики сообщений бота
"""
from aiogram import Router

from handlers.start import router as start_router
from handlers.text import router as text_router
from handlers.image import router as image_router


def setup_routers() -> Router:
    """Настройка и объединение всех роутеров"""
    main_router = Router()
    
    # Порядок важен: start должен быть первым
    main_router.include_router(start_router)
    main_router.include_router(image_router)  # Фото перед текстом
    main_router.include_router(text_router)
    
    return main_router
