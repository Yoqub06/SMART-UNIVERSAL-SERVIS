from typing import List, Optional
from models import Master
from utils import db


class MasterRepository:
    """Repository for master database operations"""
    
    async def create(self, first_name: str, last_name: str, phone_number: str,
                    telegram_username: Optional[str] = None, 
                    telegram_id: Optional[int] = None,
                    service_ids: Optional[List[int]] = None) -> Master:
        """Create new master"""
        row = await db.fetchrow(
            """
            INSERT INTO masters (first_name, last_name, phone_number, telegram_username, telegram_id)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
            """,
            first_name, last_name, phone_number, telegram_username, telegram_id
        )
        
        master = Master(
            id=row['id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            phone_number=row['phone_number'],
            telegram_username=row['telegram_username'],
            telegram_id=row['telegram_id'],
            is_active=row['is_active'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        
        # Add master services
        if service_ids:
            await self.update_services(master.id, service_ids)
        
        return master
    
    async def get_by_id(self, master_id: int) -> Optional[Master]:
        """Get master by ID"""
        row = await db.fetchrow(
            "SELECT * FROM masters WHERE id = $1",
            master_id
        )
        
        if not row:
            return None
        
        # Get master's services
        service_ids = await self.get_master_services(master_id)
        
        return Master(
            id=row['id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            phone_number=row['phone_number'],
            telegram_username=row['telegram_username'],
            telegram_id=row['telegram_id'],
            is_active=row['is_active'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            services=service_ids
        )
    
    async def get_all(self, active_only: bool = True) -> List[Master]:
        """Get all masters"""
        query = "SELECT * FROM masters"
        if active_only:
            query += " WHERE is_active = TRUE"
        query += " ORDER BY id"
        
        rows = await db.fetch(query)
        
        masters = []
        for row in rows:
            service_ids = await self.get_master_services(row['id'])
            masters.append(Master(
                id=row['id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                phone_number=row['phone_number'],
                telegram_username=row['telegram_username'],
                telegram_id=row['telegram_id'],
                is_active=row['is_active'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                services=service_ids
            ))
        
        return masters
    
    async def get_by_service(self, service_id: int) -> List[Master]:
        """Get masters who provide a specific service"""
        rows = await db.fetch(
            """
            SELECT m.* FROM masters m
            JOIN master_services ms ON m.id = ms.master_id
            WHERE ms.service_id = $1 AND m.is_active = TRUE
            ORDER BY m.id
            """,
            service_id
        )
        
        masters = []
        for row in rows:
            service_ids = await self.get_master_services(row['id'])
            masters.append(Master(
                id=row['id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                phone_number=row['phone_number'],
                telegram_username=row['telegram_username'],
                telegram_id=row['telegram_id'],
                is_active=row['is_active'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                services=service_ids
            ))
        
        return masters
    
    async def update_services(self, master_id: int, service_ids: List[int]):
        """Update master's services"""
        # Delete existing services
        await db.execute(
            "DELETE FROM master_services WHERE master_id = $1",
            master_id
        )
        
        # Add new services
        for service_id in service_ids:
            await db.execute(
                "INSERT INTO master_services (master_id, service_id) VALUES ($1, $2)",
                master_id, service_id
            )
    
    async def get_master_services(self, master_id: int) -> List[int]:
        """Get service IDs for a master"""
        rows = await db.fetch(
            "SELECT service_id FROM master_services WHERE master_id = $1",
            master_id
        )
        return [row['service_id'] for row in rows]
    
    async def delete(self, master_id: int):
        """Delete master (soft delete by setting is_active to False)"""
        await db.execute(
            "UPDATE masters SET is_active = FALSE WHERE id = $1",
            master_id
        )
    
    async def delete_permanently(self, master_id: int):
        """Permanently delete master"""
        await db.execute(
            "DELETE FROM masters WHERE id = $1",
            master_id
        )


master_repo = MasterRepository()
