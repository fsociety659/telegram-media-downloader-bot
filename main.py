import asyncio
import logging

from aiogram import Bot, Dispatcher

from handlers.commands import router as commands_router
from handlers.download import router as download_router

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token="TOKEN")
    dp = Dispatcher()
    
    dp.include_router(router=commands_router)
    dp.include_router(router=download_router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
    except Exception as e:
        print(f"Неизведамная ошибка: {e}")


