"""
Сервисы бота
"""
from services.db_service import db_service
from services.ai_service import ai_service
from services.ocr_service import ocr_service

__all__ = ["db_service", "ai_service", "ocr_service"]
