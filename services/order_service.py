from typing import Optional, Dict
from datetime import datetime
from aiogram import Bot
from models import Order, Master
from repositories import order_repo, service_repo, master_repo
from utils import messages
import random


class OrderService:
    """Service for order business logic"""
    
    async def create_order(self, user_id: int, service_id: int, service_type_id: int,
                          user_phone: str, location_latitude: Optional[float] = None,
                          location_longitude: Optional[float] = None,
                          location_address: Optional[str] = None) -> Order:
        """Create new order and assign to master"""
        # Get available masters for this service
        masters = await master_repo.get_by_service(service_id)
        
        # Select random master if available
        master_id = None
        if masters:
            selected_master = random.choice(masters)
            master_id = selected_master.id
        
        # Create order
        order = await order_repo.create(
            user_id=user_id,
            service_id=service_id,
            service_type_id=service_type_id,
            user_phone=user_phone,
            location_latitude=location_latitude,
            location_longitude=location_longitude,
            location_address=location_address,
            master_id=master_id
        )
        
        return order
    
    async def notify_master(self, bot: Bot, order: Order, user_first_name: str) -> bool:
        """Notify master about new order"""
        if not order.master_id:
            return False
        
        master = await master_repo.get_by_id(order.master_id)
        if not master or not master.telegram_id:
            return False
        
        # Get service and service type info
        service = await service_repo.get_service_by_id(order.service_id)
        service_type = await service_repo.get_service_type_by_id(order.service_type_id)
        
        # Build location text
        location_text = "Manzil ko'rsatilmagan"
        if order.location_address:
            location_text = order.location_address
        elif order.location_latitude and order.location_longitude:
            location_text = f"Koordinatalar: {order.location_latitude}, {order.location_longitude}"
        
        # Send notification to master
        notification = messages.MASTER_NOTIFICATION.format(
            client_name=user_first_name,
            client_phone=order.user_phone,
            service=service.name if service else "Noma'lum",
            service_type=service_type.name if service_type else "Noma'lum",
            location=location_text,
            time=order.created_at.strftime("%d.%m.%Y %H:%M") if order.created_at else datetime.now().strftime("%d.%m.%Y %H:%M")
        )
        
        try:
            await bot.send_message(master.telegram_id, notification)
            
            # If location coordinates available, send location
            if order.location_latitude and order.location_longitude:
                await bot.send_location(
                    master.telegram_id,
                    latitude=order.location_latitude,
                    longitude=order.location_longitude
                )
            
            return True
        except Exception as e:
            print(f"Error notifying master: {e}")
            return False
    
    async def get_order_details(self, order: Order) -> Dict[str, str]:
        """Get formatted order details"""
        service = await service_repo.get_service_by_id(order.service_id)
        service_type = await service_repo.get_service_type_by_id(order.service_type_id)
        
        location_text = "Manzil ko'rsatilmagan"
        if order.location_address:
            location_text = order.location_address
        elif order.location_latitude and order.location_longitude:
            location_text = f"{order.location_latitude}, {order.location_longitude}"
        
        return {
            'service': service.name if service else "Noma'lum",
            'service_type': service_type.name if service_type else "Noma'lum",
            'location': location_text,
            'phone': order.user_phone
        }


order_service = OrderService()
