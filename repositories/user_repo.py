from typing import Optional
from models import User
from utils import db


class UserRepository:
    """Repository for user database operations"""
    
    async def get_or_create(self, telegram_id: int, username: Optional[str] = None, 
                           first_name: Optional[str] = None) -> User:
        """Get existing user or create new one"""
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            return user
        
        return await self.create(telegram_id, username, first_name)
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by telegram ID"""
        row = await db.fetchrow(
            "SELECT * FROM users WHERE telegram_id = $1",
            telegram_id
        )
        
        if not row:
            return None
        
        return User(
            id=row['id'],
            telegram_id=row['telegram_id'],
            username=row['username'],
            first_name=row['first_name'],
            phone_number=row['phone_number'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    async def create(self, telegram_id: int, username: Optional[str] = None,
                    first_name: Optional[str] = None) -> User:
        """Create new user"""
        row = await db.fetchrow(
            """
            INSERT INTO users (telegram_id, username, first_name)
            VALUES ($1, $2, $3)
            RETURNING *
            """,
            telegram_id, username, first_name
        )
        
        return User(
            id=row['id'],
            telegram_id=row['telegram_id'],
            username=row['username'],
            first_name=row['first_name'],
            phone_number=row['phone_number'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    async def update_phone(self, telegram_id: int, phone_number: str):
        """Update user's phone number"""
        await db.execute(
            "UPDATE users SET phone_number = $1 WHERE telegram_id = $2",
            phone_number, telegram_id
        )


user_repo = UserRepository()
