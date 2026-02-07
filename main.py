import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import settings
from utils import db
from handlers import common, order, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def on_startup():
    """Execute on bot startup"""
    logger.info("🤖 Starting bot...")
    await db.connect()
    logger.info("✅ Bot started successfully!")


async def on_shutdown():
    """Execute on bot shutdown"""
    logger.info("🛑 Shutting down bot...")
    await db.disconnect()
    logger.info("✅ Bot stopped successfully!")


async def main():
    """Main function to run the bot"""
    # Initialize bot and dispatcher
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register routers
    dp.include_router(common.router)
    dp.include_router(order.router)
    dp.include_router(admin.router)
    
    # Set startup and shutdown hooks
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Start polling
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
