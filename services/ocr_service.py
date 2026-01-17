"""
Сервис распознавания текста с изображений (OCR)
Использует pytesseract + Pillow
"""
import pytesseract
from PIL import Image
from io import BytesIO
from typing import Optional
import asyncio
import logging
import os

logger = logging.getLogger(__name__)

# Укажи путь к tesseract.exe если он не в PATH
# Раскомментируй и измени путь если нужно:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Или через переменную окружения в .env:
if os.getenv("TESSERACT_PATH"):
    pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")


class OCRService:
    """Сервис для извлечения текста из изображений"""
    
    # Поддерживаемые языки для распознавания
    LANGUAGES = "rus+eng"
    
    async def extract_text(self, image_bytes: bytes) -> Optional[str]:
        """
        Извлечение текста из изображения
        
        Args:
            image_bytes: Байты изображения
            
        Returns:
            Распознанный текст или None при ошибке
        """
        try:
            # Выполняем OCR в отдельном потоке чтобы не блокировать event loop
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                None, 
                self._process_image, 
                image_bytes
            )
            return text
        except Exception as e:
            logger.error(f"Ошибка OCR: {e}")
            return None
    
    def _process_image(self, image_bytes: bytes) -> Optional[str]:
        """
        Синхронная обработка изображения (выполняется в executor)
        """
        try:
            # Открываем изображение
            image = Image.open(BytesIO(image_bytes))
            
            # Конвертируем в RGB если нужно (для PNG с прозрачностью)
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Предобработка для улучшения распознавания
            image = self._preprocess_image(image)
            
            # Распознаём текст
            text = pytesseract.image_to_string(
                image, 
                lang=self.LANGUAGES,
                config='--psm 6'  # Assume uniform block of text
            )
            
            # Очищаем результат
            text = text.strip()
            
            if not text:
                return None
                
            return text
            
        except Exception as e:
            logger.error(f"Ошибка обработки изображения: {e}")
            return None
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Предобработка изображения для улучшения OCR
        """
        # Увеличиваем размер если изображение маленькое
        width, height = image.size
        if width < 1000:
            ratio = 1000 / width
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Конвертируем в grayscale для лучшего распознавания
        image = image.convert('L')
        
        return image


# Singleton экземпляр сервиса
ocr_service = OCRService()
