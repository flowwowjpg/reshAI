"""
Скрипт для установки webhook на Vercel
Запустите после деплоя: python set_webhook.py
"""
import asyncio
import sys
from aiogram import Bot
from config import config

async def set_webhook():
    """Устанавливает webhook для бота"""
    bot = Bot(token=config.BOT_TOKEN)
    
    # URL вашего Vercel приложения
    # Замените на ваш реальный URL после деплоя
    webhook_url = input("Введите URL вашего Vercel приложения (например, https://your-app.vercel.app): ").strip()
    
    if not webhook_url:
        print("❌ URL не может быть пустым!")
        return
    
    # Добавляем путь к webhook
    full_webhook_url = f"{webhook_url}/api/webhook"
    
    try:
        # Удаляем старый webhook
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Старый webhook удалён")
        
        # Устанавливаем новый webhook
        await bot.set_webhook(
            url=full_webhook_url,
            drop_pending_updates=True
        )
        print(f"✅ Webhook установлен: {full_webhook_url}")
        
        # Проверяем webhook
        webhook_info = await bot.get_webhook_info()
        print(f"\n📊 Информация о webhook:")
        print(f"   URL: {webhook_info.url}")
        print(f"   Pending updates: {webhook_info.pending_update_count}")
        
        if webhook_info.last_error_message:
            print(f"   ⚠️ Последняя ошибка: {webhook_info.last_error_message}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        config.validate()
        asyncio.run(set_webhook())
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        sys.exit(1)
