from typing import List, Optional
from models import Service, ServiceType
from utils import db


class ServiceRepository:
    """Repository for service database operations"""
    
    async def get_all_services(self) -> List[Service]:
        """Get all services"""
        rows = await db.fetch("SELECT * FROM services ORDER BY id")
        
        return [
            Service(
                id=row['id'],
                name=row['name'],
                created_at=row['created_at']
            )
            for row in rows
        ]
    
    async def get_service_by_id(self, service_id: int) -> Optional[Service]:
        """Get service by ID"""
        row = await db.fetchrow(
            "SELECT * FROM services WHERE id = $1",
            service_id
        )
        
        if not row:
            return None
        
        return Service(
            id=row['id'],
            name=row['name'],
            created_at=row['created_at']
        )
    
    async def get_service_types(self, service_id: int) -> List[ServiceType]:
        """Get all types for a specific service"""
        rows = await db.fetch(
            "SELECT * FROM service_types WHERE service_id = $1 ORDER BY id",
            service_id
        )
        
        return [
            ServiceType(
                id=row['id'],
                service_id=row['service_id'],
                name=row['name'],
                created_at=row['created_at']
            )
            for row in rows
        ]
    
    async def get_service_type_by_id(self, service_type_id: int) -> Optional[ServiceType]:
        """Get service type by ID"""
        row = await db.fetchrow(
            "SELECT * FROM service_types WHERE id = $1",
            service_type_id
        )
        
        if not row:
            return None
        
        return ServiceType(
            id=row['id'],
            service_id=row['service_id'],
            name=row['name'],
            created_at=row['created_at']
        )


service_repo = ServiceRepository()
