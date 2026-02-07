from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from config import settings


class AdminMiddleware(BaseMiddleware):
    """Middleware to check if user is admin"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        
        # Check if user is admin
        if user_id not in settings.admin_ids_list:
            if isinstance(event, Message):
                await event.answer("⛔️ Sizda admin huquqi yo'q!")
            else:
                await event.answer("⛔️ Sizda admin huquqi yo'q!", show_alert=True)
            return
        
        # User is admin, continue processing
        return await handler(event, data)
