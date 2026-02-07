from typing import List, Optional
from models import Order
from utils import db


class OrderRepository:
    """Repository for order database operations"""
    
    async def create(self, user_id: int, service_id: int, service_type_id: int,
                    user_phone: str, location_latitude: Optional[float] = None,
                    location_longitude: Optional[float] = None,
                    location_address: Optional[str] = None,
                    master_id: Optional[int] = None) -> Order:
        """Create new order"""
        row = await db.fetchrow(
            """
            INSERT INTO orders (
                user_id, service_id, service_type_id, user_phone,
                location_latitude, location_longitude, location_address, master_id
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING *
            """,
            user_id, service_id, service_type_id, user_phone,
            location_latitude, location_longitude, location_address, master_id
        )
        
        return Order(
            id=row['id'],
            user_id=row['user_id'],
            service_id=row['service_id'],
            service_type_id=row['service_type_id'],
            user_phone=row['user_phone'],
            location_latitude=row['location_latitude'],
            location_longitude=row['location_longitude'],
            location_address=row['location_address'],
            master_id=row['master_id'],
            status=row['status'],
            notes=row['notes'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        row = await db.fetchrow(
            "SELECT * FROM orders WHERE id = $1",
            order_id
        )
        
        if not row:
            return None
        
        return Order(
            id=row['id'],
            user_id=row['user_id'],
            service_id=row['service_id'],
            service_type_id=row['service_type_id'],
            user_phone=row['user_phone'],
            location_latitude=row['location_latitude'],
            location_longitude=row['location_longitude'],
            location_address=row['location_address'],
            master_id=row['master_id'],
            status=row['status'],
            notes=row['notes'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    async def get_all(self, limit: int = 50) -> List[Order]:
        """Get all orders"""
        rows = await db.fetch(
            "SELECT * FROM orders ORDER BY created_at DESC LIMIT $1",
            limit
        )
        
        return [
            Order(
                id=row['id'],
                user_id=row['user_id'],
                service_id=row['service_id'],
                service_type_id=row['service_type_id'],
                user_phone=row['user_phone'],
                location_latitude=row['location_latitude'],
                location_longitude=row['location_longitude'],
                location_address=row['location_address'],
                master_id=row['master_id'],
                status=row['status'],
                notes=row['notes'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            for row in rows
        ]
    
    async def get_by_user(self, user_id: int) -> List[Order]:
        """Get orders by user"""
        rows = await db.fetch(
            "SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC",
            user_id
        )
        
        return [
            Order(
                id=row['id'],
                user_id=row['user_id'],
                service_id=row['service_id'],
                service_type_id=row['service_type_id'],
                user_phone=row['user_phone'],
                location_latitude=row['location_latitude'],
                location_longitude=row['location_longitude'],
                location_address=row['location_address'],
                master_id=row['master_id'],
                status=row['status'],
                notes=row['notes'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            for row in rows
        ]
    
    async def get_by_master(self, master_id: int) -> List[Order]:
        """Get orders by master"""
        rows = await db.fetch(
            "SELECT * FROM orders WHERE master_id = $1 ORDER BY created_at DESC",
            master_id
        )
        
        return [
            Order(
                id=row['id'],
                user_id=row['user_id'],
                service_id=row['service_id'],
                service_type_id=row['service_type_id'],
                user_phone=row['user_phone'],
                location_latitude=row['location_latitude'],
                location_longitude=row['location_longitude'],
                location_address=row['location_address'],
                master_id=row['master_id'],
                status=row['status'],
                notes=row['notes'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            for row in rows
        ]
    
    async def update_status(self, order_id: int, status: str):
        """Update order status"""
        await db.execute(
            "UPDATE orders SET status = $1 WHERE id = $2",
            status, order_id
        )


order_repo = OrderRepository()
