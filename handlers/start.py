"""
Обработчик команды /start и базовых команд
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from services.db_service import db_service
from keyboards.main import get_main_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Обработка команды /start"""
    # Регистрируем пользователя в БД
    await db_service.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    welcome_text = """👋 Привет! Я ИИ-ГДЗ бот.

Пришли мне задание текстом или скриншотом — я решу и объясню 😎

📝 Просто напиши задачу или отправь фото
📚 Я помогу с математикой, физикой, химией, русским и другими предметами

Давай начнём! 🚀"""
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard()
    )


@router.message(Command("help"))
@router.message(F.text == "❓ Помощь")
async def cmd_help(message: Message) -> None:
    """Обработка команды /help"""
    help_text = """📖 Как пользоваться ботом:

1️⃣ Отправь текст задания
   Просто напиши задачу в чат

2️⃣ Или отправь скриншот
   Сфотографируй задание и отправь фото

3️⃣ Получи решение
   Я подробно объясню решение и дам ответ

💡 Советы:
• Для фото — используй чёткие скриншоты
• Пиши задание полностью
• Указывай все данные из условия

🎓 Поддерживаемые предметы:
Математика, Алгебра, Геометрия, Физика, Химия, Русский язык, Литература, История, Биология, География, Английский и другие"""
    
    await message.answer(help_text)


@router.message(F.text == "📊 Моя статистика")
async def cmd_stats(message: Message) -> None:
    """Показать статистику пользователя"""
    stats = await db_service.get_user_stats(message.from_user.id)
    
    stats_text = f"""📊 Твоя статистика:

📝 Всего запросов: {stats['total_requests']}

Продолжай учиться! 💪"""
    
    await message.answer(stats_text)
