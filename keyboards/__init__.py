from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from typing import List
from models import Service, ServiceType, Master


class Keyboards:
    """Keyboard builders for the bot"""
    
    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """Main menu keyboard"""
        builder = ReplyKeyboardBuilder()
        builder.button(text="🛠 Buyurtma berish")
        builder.button(text="📋 Mening buyurtmalarim")
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def phone_request() -> ReplyKeyboardMarkup:
        """Request phone number keyboard"""
        builder = ReplyKeyboardBuilder()
        builder.button(text="📞 Raqam yuborish", request_contact=True)
        builder.button(text="⬅️ Orqaga")
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def location_request() -> ReplyKeyboardMarkup:
        """Request location keyboard"""
        builder = ReplyKeyboardBuilder()
        builder.button(text="📍 Lokatsiya yuborish", request_location=True)
        builder.button(text="⬅️ Orqaga")
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def services(services: List[Service]) -> InlineKeyboardMarkup:
        """Services selection keyboard"""
        builder = InlineKeyboardBuilder()
        for service in services:
            builder.button(
                text=service.name,
                callback_data=f"service_{service.id}"
            )
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def service_types(service_types: List[ServiceType]) -> InlineKeyboardMarkup:
        """Service types selection keyboard"""
        builder = InlineKeyboardBuilder()
        for service_type in service_types:
            builder.button(
                text=service_type.name,
                callback_data=f"type_{service_type.id}"
            )
        builder.button(text="⬅️ Orqaga", callback_data="back_to_services")
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def confirm_order() -> InlineKeyboardMarkup:
        """Order confirmation keyboard"""
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Tasdiqlash", callback_data="confirm_yes")
        builder.button(text="❌ Bekor qilish", callback_data="confirm_no")
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def admin_panel() -> InlineKeyboardMarkup:
        """Admin panel keyboard"""
        builder = InlineKeyboardBuilder()
        builder.button(text="➕ Usta qo'shish", callback_data="admin_add_master")
        builder.button(text="➖ Usta o'chirish", callback_data="admin_delete_master")
        builder.button(text="👥 Ustalar ro'yxati", callback_data="admin_list_masters")
        builder.button(text="📋 Buyurtmalar", callback_data="admin_list_orders")
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def services_selection(services: List[Service], selected: List[int] = None) -> InlineKeyboardMarkup:
        """Services selection for master (with checkboxes)"""
        if selected is None:
            selected = []
        
        builder = InlineKeyboardBuilder()
        for service in services:
            checkbox = "✅" if service.id in selected else "☐"
            builder.button(
                text=f"{checkbox} {service.name}",
                callback_data=f"toggle_service_{service.id}"
            )
        builder.button(text="✅ Davom etish", callback_data="services_done")
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def masters_list(masters: List[Master], action: str = "delete") -> InlineKeyboardMarkup:
        """Masters list keyboard"""
        builder = InlineKeyboardBuilder()
        for master in masters:
            builder.button(
                text=f"{master.full_name} - {master.phone_number}",
                callback_data=f"{action}_master_{master.id}"
            )
        builder.button(text="⬅️ Orqaga", callback_data="back_to_admin")
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def back_to_admin() -> InlineKeyboardMarkup:
        """Back to admin panel button"""
        builder = InlineKeyboardBuilder()
        builder.button(text="⬅️ Admin paneliga qaytish", callback_data="back_to_admin")
        return builder.as_markup()
    
    @staticmethod
    def cancel() -> ReplyKeyboardMarkup:
        """Cancel keyboard"""
        builder = ReplyKeyboardBuilder()
        builder.button(text="❌ Bekor qilish")
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)


keyboards = Keyboards()
