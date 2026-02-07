from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class User:
    """User model"""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    phone_number: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Service:
    """Service model"""
    id: int
    name: str
    created_at: Optional[datetime] = None


@dataclass
class ServiceType:
    """Service type model"""
    id: int
    service_id: int
    name: str
    created_at: Optional[datetime] = None


@dataclass
class Master:
    """Master model"""
    id: int
    first_name: str
    last_name: str
    phone_number: str
    telegram_username: Optional[str] = None
    telegram_id: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    services: Optional[List[int]] = None
    
    @property
    def full_name(self) -> str:
        """Get master's full name"""
        return f"{self.first_name} {self.last_name}"


@dataclass
class Order:
    """Order model"""
    user_id: int
    service_id: int
    service_type_id: int
    user_phone: str
    location_latitude: Optional[float] = None
    location_longitude: Optional[float] = None
    location_address: Optional[str] = None
    master_id: Optional[int] = None
    status: str = 'pending'
    notes: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
