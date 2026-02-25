import asyncio
import logging
import random
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, List, Optional

import asyncpg
from aiogram import BaseMiddleware, Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from pydantic_settings import BaseSettings, SettingsConfigDict

# ============================================================
# SETTINGS
# ============================================================

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: str

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def admin_ids_list(self) -> List[int]:
        return [int(admin_id.strip()) for admin_id in self.ADMIN_IDS.split(",")]


settings = Settings()

# ============================================================
# DATABASE
# ============================================================

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            min_size=5,
            max_size=20,
        )
        print("Database connected successfully")

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            print("Database disconnected")

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)


db = Database()

# ============================================================
# MODELS
# ============================================================

@dataclass
class User:
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    phone_number: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Service:
    id: int
    name: str
    created_at: Optional[datetime] = None


@dataclass
class ServiceType:
    id: int
    service_id: int
    name: str
    created_at: Optional[datetime] = None


@dataclass
class Master:
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
        return f"{self.first_name} {self.last_name}"


@dataclass
class Order:
    user_id: int
    service_id: int
    service_type_id: int
    user_phone: str
    location_latitude: Optional[float] = None
    location_longitude: Optional[float] = None
    location_address: Optional[str] = None
    master_id: Optional[int] = None
    status: str = "pending"
    notes: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ============================================================
# STATES
# ============================================================

class OrderStates(StatesGroup):
    choosing_service = State()
    choosing_service_type = State()
    waiting_location = State()
    waiting_phone = State()
    confirming_order = State()


class AdminStates(StatesGroup):
    waiting_master_first_name = State()
    waiting_master_last_name = State()
    waiting_master_username = State()
    waiting_master_phone = State()
    waiting_master_services = State()
    selecting_master_to_edit = State()
    editing_master = State()
    selecting_master_to_delete = State()

# ============================================================
# MESSAGES
# ============================================================

class Messages:
    WELCOME = """
Assalomu alaykum!

Uy xizmatlariga buyurtma berish botiga xush kelibsiz.

Quyidagi xizmatlardan birini tanlang:
"""

    SELECT_SERVICE = "Quyidagi xizmatlardan birini tanlang:"
    SELECT_SERVICE_TYPE = "Qaysi turdagi ishni bajarishingiz kerak?"

    SEND_LOCATION = """
Iltimos, manzilni yuboring.

Pastdagi "Lokatsiya yuborish" tugmasini bosing yoki xarita orqali manzilni tanlang.
"""

    SEND_PHONE = """
Iltimos, telefon raqamingizni yuboring.

Pastdagi "Raqam yuborish" tugmasini bosing.
"""

    CONFIRM_ORDER = """
Buyurtmangizni tasdiqlang:

Xizmat: {service}
Ish turi: {service_type}
Manzil: {location}
Telefon: {phone}

Buyurtmani tasdiqlamoqchimisiz?
"""

    ORDER_SUCCESS = """
Buyurtma muvaffaqiyatli qabul qilindi!

Tez orada usta siz bilan bog'lanadi.

Usta bilan bog'lanish:
Ism: {master_name}
Telefon: {master_phone}
{username_line}
"""

    ORDER_NO_MASTER = """
Buyurtma qabul qilindi!

Afsuski, hozirda bu xizmat uchun mavjud usta yo'q.
Adminlar tez orada siz bilan bog'lanadi.
"""

    MASTER_NOTIFICATION = """
Yangi buyurtma!

Mijoz: {client_name}
Telefon: {client_phone}
Xizmat: {service}
Ish turi: {service_type}
Manzil: {location}

Vaqt: {time}
"""

    ADMIN_PANEL = """
Admin Panel

Quyidagi amallardan birini tanlang:
"""

    MASTER_ADD_FIRST_NAME = "Ustaning ismini kiriting:"
    MASTER_ADD_LAST_NAME = "Ustaning familiyasini kiriting:"
    MASTER_ADD_USERNAME = (
        "Ustaning Telegram username'ini kiriting (@ belgisisiz) "
        "yoki o'tkazib yuborish uchun /skip ni bosing:"
    )
    MASTER_ADD_PHONE = "Ustaning telefon raqamini kiriting (+998 formatida):"
    MASTER_ADD_SERVICES = (
        "Usta qaysi xizmatlarni ko'rsatadi? Raqamlarni vergul bilan ajrating "
        "(masalan: 1,2,3)"
    )

    MASTER_ADDED = "Usta muvaffaqiyatli qo'shildi!"
    MASTER_DELETED = "Usta o'chirildi!"
    MASTER_NOT_FOUND = "Usta topilmadi"

    MASTERS_LIST = "Barcha ustalar:\n\n"
    NO_MASTERS = "Hozircha ustalar yo'q"

    ORDERS_LIST = "Barcha buyurtmalar:\n\n"
    NO_ORDERS = "Hozircha buyurtmalar yo'q"

    SELECT_MASTER_TO_DELETE = "O'chirish uchun ustani tanlang:"

    ERROR_GENERAL = "Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring."
    ERROR_INVALID_PHONE = (
        "Noto'g'ri telefon raqam formati. Iltimos, +998 bilan boshlangan raqam kiriting."
    )
    ERROR_INVALID_INPUT = "Noto'g'ri ma'lumot. Iltimos, qaytadan urinib ko'ring."

    BTN_BACK = "Orqaga"
    BTN_CANCEL = "Bekor qilish"
    BTN_CONFIRM = "Tasdiqlash"
    BTN_MAIN_MENU = "Bosh menyu"
    BTN_ADD_MASTER = "Usta qo'shish"
    BTN_DELETE_MASTER = "Usta o'chirish"
    BTN_LIST_MASTERS = "Ustalar ro'yxati"
    BTN_LIST_ORDERS = "Buyurtmalar"
    BTN_BACK_TO_ADMIN = "Admin paneliga qaytish"


messages = Messages()

# ============================================================
# KEYBOARDS
# ============================================================

class Keyboards:
    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.button(text="Buyurtma berish")
        builder.button(text="Mening buyurtmalarim")
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def phone_request() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.add(KeyboardButton(text="Raqam yuborish", request_contact=True))
        builder.button(text="Orqaga")
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def location_request() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.add(KeyboardButton(text="Lokatsiya yuborish", request_location=True))
        builder.button(text="Orqaga")
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def services(services: List[Service]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for service in services:
            builder.button(text=service.name, callback_data=f"service_{service.id}")
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def service_types(service_types: List[ServiceType]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for service_type in service_types:
            builder.button(text=service_type.name, callback_data=f"type_{service_type.id}")
        builder.button(text="Orqaga", callback_data="back_to_services")
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def confirm_order() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="Tasdiqlash", callback_data="confirm_yes")
        builder.button(text="Bekor qilish", callback_data="confirm_no")
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def admin_panel() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="Usta qo'shish", callback_data="admin_add_master")
        builder.button(text="Usta o'chirish", callback_data="admin_delete_master")
        builder.button(text="Ustalar ro'yxati", callback_data="admin_list_masters")
        builder.button(text="Buyurtmalar", callback_data="admin_list_orders")
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def services_selection(
        services: List[Service], selected: Optional[List[int]] = None
    ) -> InlineKeyboardMarkup:
        if selected is None:
            selected = []

        builder = InlineKeyboardBuilder()
        for service in services:
            checkbox = "YES" if service.id in selected else "NO"
            builder.button(
                text=f"{checkbox} {service.name}",
                callback_data=f"toggle_service_{service.id}",
            )
        builder.button(text="Davom etish", callback_data="services_done")
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def masters_list(masters: List[Master], action: str = "delete") -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for master in masters:
            builder.button(
                text=f"{master.full_name} - {master.phone_number}",
                callback_data=f"{action}_master_{master.id}",
            )
        builder.button(text="Orqaga", callback_data="back_to_admin")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def back_to_admin() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="Admin paneliga qaytish", callback_data="back_to_admin")
        return builder.as_markup()

    @staticmethod
    def cancel() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.button(text="Bekor qilish")
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)


keyboards = Keyboards()

# ============================================================
# REPOSITORIES
# ============================================================

class UserRepository:
    async def get_or_create(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
    ) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            return user
        return await self.create(telegram_id, username, first_name)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        row = await db.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
        if not row:
            return None

        return User(
            id=row["id"],
            telegram_id=row["telegram_id"],
            username=row["username"],
            first_name=row["first_name"],
            phone_number=row["phone_number"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def create(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
    ) -> User:
        row = await db.fetchrow(
            """
            INSERT INTO users (telegram_id, username, first_name)
            VALUES ($1, $2, $3)
            RETURNING *
            """,
            telegram_id,
            username,
            first_name,
        )

        return User(
            id=row["id"],
            telegram_id=row["telegram_id"],
            username=row["username"],
            first_name=row["first_name"],
            phone_number=row["phone_number"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def update_phone(self, telegram_id: int, phone_number: str):
        await db.execute(
            "UPDATE users SET phone_number = $1 WHERE telegram_id = $2",
            phone_number,
            telegram_id,
        )


user_repo = UserRepository()


class ServiceRepository:
    async def get_all_services(self) -> List[Service]:
        rows = await db.fetch("SELECT * FROM services ORDER BY id")
        return [Service(id=row["id"], name=row["name"], created_at=row["created_at"]) for row in rows]

    async def get_service_by_id(self, service_id: int) -> Optional[Service]:
        row = await db.fetchrow("SELECT * FROM services WHERE id = $1", service_id)
        if not row:
            return None
        return Service(id=row["id"], name=row["name"], created_at=row["created_at"])

    async def get_service_types(self, service_id: int) -> List[ServiceType]:
        rows = await db.fetch(
            "SELECT * FROM service_types WHERE service_id = $1 ORDER BY id",
            service_id,
        )
        return [
            ServiceType(
                id=row["id"],
                service_id=row["service_id"],
                name=row["name"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    async def get_service_type_by_id(self, service_type_id: int) -> Optional[ServiceType]:
        row = await db.fetchrow("SELECT * FROM service_types WHERE id = $1", service_type_id)
        if not row:
            return None
        return ServiceType(
            id=row["id"],
            service_id=row["service_id"],
            name=row["name"],
            created_at=row["created_at"],
        )


service_repo = ServiceRepository()


class MasterRepository:
    async def create(
        self,
        first_name: str,
        last_name: str,
        phone_number: str,
        telegram_username: Optional[str] = None,
        telegram_id: Optional[int] = None,
        service_ids: Optional[List[int]] = None,
    ) -> Master:
        row = await db.fetchrow(
            """
            INSERT INTO masters (first_name, last_name, phone_number, telegram_username, telegram_id)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
            """,
            first_name,
            last_name,
            phone_number,
            telegram_username,
            telegram_id,
        )

        master = Master(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            phone_number=row["phone_number"],
            telegram_username=row["telegram_username"],
            telegram_id=row["telegram_id"],
            is_active=row["is_active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

        if service_ids:
            await self.update_services(master.id, service_ids)

        return master

    async def get_by_id(self, master_id: int) -> Optional[Master]:
        row = await db.fetchrow("SELECT * FROM masters WHERE id = $1", master_id)
        if not row:
            return None

        service_ids = await self.get_master_services(master_id)
        return Master(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            phone_number=row["phone_number"],
            telegram_username=row["telegram_username"],
            telegram_id=row["telegram_id"],
            is_active=row["is_active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            services=service_ids,
        )

    async def get_all(self, active_only: bool = True) -> List[Master]:
        query = "SELECT * FROM masters"
        if active_only:
            query += " WHERE is_active = TRUE"
        query += " ORDER BY id"

        rows = await db.fetch(query)
        masters = []
        for row in rows:
            service_ids = await self.get_master_services(row["id"])
            masters.append(
                Master(
                    id=row["id"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    phone_number=row["phone_number"],
                    telegram_username=row["telegram_username"],
                    telegram_id=row["telegram_id"],
                    is_active=row["is_active"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    services=service_ids,
                )
            )
        return masters

    async def get_by_service(self, service_id: int) -> List[Master]:
        rows = await db.fetch(
            """
            SELECT m.* FROM masters m
            JOIN master_services ms ON m.id = ms.master_id
            WHERE ms.service_id = $1 AND m.is_active = TRUE
            ORDER BY m.id
            """,
            service_id,
        )

        masters = []
        for row in rows:
            service_ids = await self.get_master_services(row["id"])
            masters.append(
                Master(
                    id=row["id"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    phone_number=row["phone_number"],
                    telegram_username=row["telegram_username"],
                    telegram_id=row["telegram_id"],
                    is_active=row["is_active"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    services=service_ids,
                )
            )
        return masters

    async def update_services(self, master_id: int, service_ids: List[int]):
        await db.execute("DELETE FROM master_services WHERE master_id = $1", master_id)
        for service_id in service_ids:
            await db.execute(
                "INSERT INTO master_services (master_id, service_id) VALUES ($1, $2)",
                master_id,
                service_id,
            )

    async def get_master_services(self, master_id: int) -> List[int]:
        rows = await db.fetch("SELECT service_id FROM master_services WHERE master_id = $1", master_id)
        return [row["service_id"] for row in rows]

    async def delete(self, master_id: int):
        await db.execute("UPDATE masters SET is_active = FALSE WHERE id = $1", master_id)

    async def delete_permanently(self, master_id: int):
        await db.execute("DELETE FROM masters WHERE id = $1", master_id)


master_repo = MasterRepository()


class OrderRepository:
    @staticmethod
    def _row_to_order(row) -> Order:
        return Order(
            id=row["id"],
            user_id=row["user_id"],
            service_id=row["service_id"],
            service_type_id=row["service_type_id"],
            user_phone=row["user_phone"],
            location_latitude=row["location_latitude"],
            location_longitude=row["location_longitude"],
            location_address=row["location_address"],
            master_id=row["master_id"],
            status=row["status"],
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def create(
        self,
        user_id: int,
        service_id: int,
        service_type_id: int,
        user_phone: str,
        location_latitude: Optional[float] = None,
        location_longitude: Optional[float] = None,
        location_address: Optional[str] = None,
        master_id: Optional[int] = None,
    ) -> Order:
        row = await db.fetchrow(
            """
            INSERT INTO orders (
                user_id, service_id, service_type_id, user_phone,
                location_latitude, location_longitude, location_address, master_id
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING *
            """,
            user_id,
            service_id,
            service_type_id,
            user_phone,
            location_latitude,
            location_longitude,
            location_address,
            master_id,
        )
        return self._row_to_order(row)

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        row = await db.fetchrow("SELECT * FROM orders WHERE id = $1", order_id)
        return self._row_to_order(row) if row else None

    async def get_all(self, limit: int = 50) -> List[Order]:
        rows = await db.fetch("SELECT * FROM orders ORDER BY created_at DESC LIMIT $1", limit)
        return [self._row_to_order(row) for row in rows]

    async def get_by_user(self, user_id: int) -> List[Order]:
        rows = await db.fetch(
            "SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC", user_id
        )
        return [self._row_to_order(row) for row in rows]

    async def get_by_master(self, master_id: int) -> List[Order]:
        rows = await db.fetch(
            "SELECT * FROM orders WHERE master_id = $1 ORDER BY created_at DESC",
            master_id,
        )
        return [self._row_to_order(row) for row in rows]

    async def update_status(self, order_id: int, status: str):
        await db.execute("UPDATE orders SET status = $1 WHERE id = $2", status, order_id)


order_repo = OrderRepository()


class OrderService:
    async def create_order(
        self,
        user_id: int,
        service_id: int,
        service_type_id: int,
        user_phone: str,
        location_latitude: Optional[float] = None,
        location_longitude: Optional[float] = None,
        location_address: Optional[str] = None,
    ) -> Order:
        masters = await master_repo.get_by_service(service_id)

        master_id = None
        if masters:
            selected_master = random.choice(masters)
            master_id = selected_master.id

        return await order_repo.create(
            user_id=user_id,
            service_id=service_id,
            service_type_id=service_type_id,
            user_phone=user_phone,
            location_latitude=location_latitude,
            location_longitude=location_longitude,
            location_address=location_address,
            master_id=master_id,
        )

    async def notify_master(self, bot: Bot, order: Order, user_first_name: str) -> bool:
        if not order.master_id:
            return False

        master = await master_repo.get_by_id(order.master_id)
        if not master or not master.telegram_id:
            return False

        service = await service_repo.get_service_by_id(order.service_id)
        service_type = await service_repo.get_service_type_by_id(order.service_type_id)

        location_text = "Manzil ko'rsatilmagan"
        if order.location_address:
            location_text = order.location_address
        elif order.location_latitude and order.location_longitude:
            location_text = f"Koordinatalar: {order.location_latitude}, {order.location_longitude}"

        notification = messages.MASTER_NOTIFICATION.format(
            client_name=user_first_name,
            client_phone=order.user_phone,
            service=service.name if service else "Noma'lum",
            service_type=service_type.name if service_type else "Noma'lum",
            location=location_text,
            time=order.created_at.strftime("%d.%m.%Y %H:%M")
            if order.created_at
            else datetime.now().strftime("%d.%m.%Y %H:%M"),
        )

        try:
            await bot.send_message(master.telegram_id, notification)
            if order.location_latitude and order.location_longitude:
                await bot.send_location(
                    master.telegram_id,
                    latitude=order.location_latitude,
                    longitude=order.location_longitude,
                )
            return True
        except Exception as e:
            print(f"Error notifying master: {e}")
            return False

    async def get_order_details(self, order: Order) -> Dict[str, str]:
        service = await service_repo.get_service_by_id(order.service_id)
        service_type = await service_repo.get_service_type_by_id(order.service_type_id)

        location_text = "Manzil ko'rsatilmagan"
        if order.location_address:
            location_text = order.location_address
        elif order.location_latitude and order.location_longitude:
            location_text = f"{order.location_latitude}, {order.location_longitude}"

        return {
            "service": service.name if service else "Noma'lum",
            "service_type": service_type.name if service_type else "Noma'lum",
            "location": location_text,
            "phone": order.user_phone,
        }


order_service = OrderService()

# ============================================================
# MIDDLEWARE
# ============================================================

class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id

        if user_id not in settings.admin_ids_list:
            if isinstance(event, Message):
                await event.answer("Sizda admin huquqi yo'q!")
            else:
                await event.answer("Sizda admin huquqi yo'q!", show_alert=True)
            return

        return await handler(event, data)

# ============================================================
# HANDLERS - USER
# ============================================================

common_router = Router()
order_router = Router()


@common_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    await user_repo.get_or_create(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    await message.answer(messages.WELCOME, reply_markup=keyboards.main_menu())


@common_router.message(F.text == "Bosh menyu")
@common_router.message(F.text == "Bekor qilish")
async def main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bosh menyu", reply_markup=keyboards.main_menu())


@order_router.message(F.text == "Buyurtma berish")
async def start_order(message: Message, state: FSMContext):
    services = await service_repo.get_all_services()

    await message.answer(messages.SELECT_SERVICE, reply_markup=keyboards.services(services))
    await state.set_state(OrderStates.choosing_service)


@order_router.callback_query(F.data.startswith("service_"), OrderStates.choosing_service)
async def service_selected(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split("_")[1])
    await state.update_data(service_id=service_id)

    service_types = await service_repo.get_service_types(service_id)

    await callback.message.edit_text(
        messages.SELECT_SERVICE_TYPE,
        reply_markup=keyboards.service_types(service_types),
    )
    await state.set_state(OrderStates.choosing_service_type)
    await callback.answer()


@order_router.callback_query(F.data == "back_to_services", OrderStates.choosing_service_type)
async def back_to_services(callback: CallbackQuery, state: FSMContext):
    services = await service_repo.get_all_services()

    await callback.message.edit_text(
        messages.SELECT_SERVICE,
        reply_markup=keyboards.services(services),
    )
    await state.set_state(OrderStates.choosing_service)
    await callback.answer()


@order_router.callback_query(F.data.startswith("type_"), OrderStates.choosing_service_type)
async def service_type_selected(callback: CallbackQuery, state: FSMContext):
    service_type_id = int(callback.data.split("_")[1])
    await state.update_data(service_type_id=service_type_id)

    await callback.message.answer(
        messages.SEND_LOCATION,
        reply_markup=keyboards.location_request(),
    )
    await state.set_state(OrderStates.waiting_location)
    await callback.answer()


@order_router.message(F.location, OrderStates.waiting_location)
async def location_received(message: Message, state: FSMContext):
    location = message.location

    await state.update_data(
        location_latitude=location.latitude,
        location_longitude=location.longitude,
        location_address=None,
    )

    await message.answer(messages.SEND_PHONE, reply_markup=keyboards.phone_request())
    await state.set_state(OrderStates.waiting_phone)


@order_router.message(F.text, OrderStates.waiting_location)
async def location_text_received(message: Message, state: FSMContext):
    if message.text in ["Orqaga", "Bekor qilish"]:
        return

    await state.update_data(
        location_latitude=None,
        location_longitude=None,
        location_address=message.text,
    )

    await message.answer(messages.SEND_PHONE, reply_markup=keyboards.phone_request())
    await state.set_state(OrderStates.waiting_phone)


@order_router.message(F.contact, OrderStates.waiting_phone)
async def contact_received(message: Message, state: FSMContext):
    phone = message.contact.phone_number

    await user_repo.update_phone(message.from_user.id, phone)
    await state.update_data(user_phone=phone)

    await show_order_confirmation(message, state)


@order_router.message(F.text.regexp(r"^\+?\d{9,15}$"), OrderStates.waiting_phone)
async def phone_text_received(message: Message, state: FSMContext):
    phone = message.text.strip()

    if not re.match(r"^\+?\d{9,15}$", phone):
        await message.answer(messages.ERROR_INVALID_PHONE)
        return

    await user_repo.update_phone(message.from_user.id, phone)
    await state.update_data(user_phone=phone)

    await show_order_confirmation(message, state)


async def show_order_confirmation(message: Message, state: FSMContext):
    data = await state.get_data()

    service = await service_repo.get_service_by_id(data["service_id"])
    service_type = await service_repo.get_service_type_by_id(data["service_type_id"])

    location_text = data.get("location_address", "Manzil ko'rsatilmagan")
    if not location_text and data.get("location_latitude"):
        location_text = f"{data['location_latitude']}, {data['location_longitude']}"

    confirmation_text = messages.CONFIRM_ORDER.format(
        service=service.name,
        service_type=service_type.name,
        location=location_text,
        phone=data["user_phone"],
    )

    await message.answer(confirmation_text, reply_markup=keyboards.confirm_order())
    await state.set_state(OrderStates.confirming_order)


@order_router.callback_query(F.data == "confirm_yes", OrderStates.confirming_order)
async def confirm_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()

    order = await order_service.create_order(
        user_id=callback.from_user.id,
        service_id=data["service_id"],
        service_type_id=data["service_type_id"],
        user_phone=data["user_phone"],
        location_latitude=data.get("location_latitude"),
        location_longitude=data.get("location_longitude"),
        location_address=data.get("location_address"),
    )

    if order.master_id:
        master = await master_repo.get_by_id(order.master_id)
        await order_service.notify_master(bot, order, callback.from_user.first_name or "Mijoz")

        username_line = ""
        if master.telegram_username:
            username_line = f"Telegram: @{master.telegram_username}"

        success_message = messages.ORDER_SUCCESS.format(
            master_name=master.full_name,
            master_phone=master.phone_number,
            username_line=username_line,
        )
    else:
        success_message = messages.ORDER_NO_MASTER

    await callback.message.edit_text(success_message)
    await callback.message.answer("Bosh menyu", reply_markup=keyboards.main_menu())

    await state.clear()
    await callback.answer()


@order_router.callback_query(F.data == "confirm_no", OrderStates.confirming_order)
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Buyurtma bekor qilindi")
    await callback.message.answer("Bosh menyu", reply_markup=keyboards.main_menu())
    await callback.answer()


@order_router.message(F.text == "Mening buyurtmalarim")
async def my_orders(message: Message):
    orders = await order_repo.get_by_user(message.from_user.id)

    if not orders:
        await message.answer("Sizda hali buyurtmalar yo'q")
        return

    response = "Sizning buyurtmalaringiz:\n\n"

    for order in orders[:10]:
        service = await service_repo.get_service_by_id(order.service_id)
        service_type = await service_repo.get_service_type_by_id(order.service_type_id)

        response += f"ID #{order.id}\n"
        response += f"{service.name} - {service_type.name}\n"
        response += f"{order.user_phone}\n"
        response += f"{order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        response += f"Status: {order.status}\n\n"

    await message.answer(response)

# ============================================================
# HANDLERS - ADMIN
# ============================================================

admin_router = Router()
admin_router.message.middleware(AdminMiddleware())
admin_router.callback_query.middleware(AdminMiddleware())


@admin_router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(messages.ADMIN_PANEL, reply_markup=keyboards.admin_panel())


@admin_router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(messages.ADMIN_PANEL, reply_markup=keyboards.admin_panel())
    await callback.answer()


@admin_router.callback_query(F.data == "admin_add_master")
async def add_master_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(messages.MASTER_ADD_FIRST_NAME)
    await state.set_state(AdminStates.waiting_master_first_name)
    await callback.answer()


@admin_router.message(AdminStates.waiting_master_first_name)
async def master_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text.strip())
    await message.answer(messages.MASTER_ADD_LAST_NAME)
    await state.set_state(AdminStates.waiting_master_last_name)


@admin_router.message(AdminStates.waiting_master_last_name)
async def master_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text.strip())
    await message.answer(messages.MASTER_ADD_USERNAME, reply_markup=keyboards.cancel())
    await state.set_state(AdminStates.waiting_master_username)


@admin_router.message(AdminStates.waiting_master_username)
async def master_username(message: Message, state: FSMContext):
    username = None
    if message.text and message.text != "/skip":
        username = message.text.strip().lstrip("@")

    await state.update_data(username=username)
    await message.answer(messages.MASTER_ADD_PHONE)
    await state.set_state(AdminStates.waiting_master_phone)


@admin_router.message(AdminStates.waiting_master_phone)
async def master_phone(message: Message, state: FSMContext):
    phone = message.text.strip()

    if not re.match(r"^\+?\d{9,15}$", phone):
        await message.answer(messages.ERROR_INVALID_PHONE)
        return

    await state.update_data(phone=phone)

    services = await service_repo.get_all_services()
    service_list = "\n".join([f"{s.id}. {s.name}" for s in services])

    await message.answer(f"{messages.MASTER_ADD_SERVICES}\n\n{service_list}")
    await state.set_state(AdminStates.waiting_master_services)


@admin_router.message(AdminStates.waiting_master_services)
async def master_services(message: Message, state: FSMContext):
    try:
        service_ids = [int(x.strip()) for x in message.text.split(",")]

        all_services = await service_repo.get_all_services()
        valid_ids = [s.id for s in all_services]

        invalid = [sid for sid in service_ids if sid not in valid_ids]
        if invalid:
            await message.answer(f"Noto'g'ri xizmat ID: {invalid}")
            return

        data = await state.get_data()

        master = await master_repo.create(
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone_number=data["phone"],
            telegram_username=data.get("username"),
            service_ids=service_ids,
        )

        await message.answer(
            f"{messages.MASTER_ADDED}\n\n"
            f"{master.full_name}\n"
            f"{master.phone_number}",
            reply_markup=keyboards.back_to_admin(),
        )

        await state.clear()

    except ValueError:
        await message.answer(messages.ERROR_INVALID_INPUT)


@admin_router.callback_query(F.data == "admin_delete_master")
async def delete_master_start(callback: CallbackQuery, state: FSMContext):
    masters = await master_repo.get_all(active_only=False)

    if not masters:
        await callback.answer(messages.NO_MASTERS, show_alert=True)
        return

    await callback.message.edit_text(
        messages.SELECT_MASTER_TO_DELETE,
        reply_markup=keyboards.masters_list(masters, action="delete"),
    )
    await state.set_state(AdminStates.selecting_master_to_delete)
    await callback.answer()


@admin_router.callback_query(
    F.data.startswith("delete_master_"), AdminStates.selecting_master_to_delete
)
async def delete_master_confirm(callback: CallbackQuery, state: FSMContext):
    master_id = int(callback.data.split("_")[2])

    master = await master_repo.get_by_id(master_id)
    if not master:
        await callback.answer(messages.MASTER_NOT_FOUND, show_alert=True)
        return

    await master_repo.delete(master_id)

    await callback.message.edit_text(
        f"{messages.MASTER_DELETED}\n\n{master.full_name}",
        reply_markup=keyboards.back_to_admin(),
    )

    await state.clear()
    await callback.answer()


@admin_router.callback_query(F.data == "admin_list_masters")
async def list_masters(callback: CallbackQuery):
    masters = await master_repo.get_all(active_only=False)

    if not masters:
        await callback.answer(messages.NO_MASTERS, show_alert=True)
        return

    response = messages.MASTERS_LIST

    for master in masters:
        status = "ACTIVE" if master.is_active else "INACTIVE"
        response += f"{status} {master.full_name}\n"
        response += f"{master.phone_number}\n"

        if master.telegram_username:
            response += f"@{master.telegram_username}\n"

        if master.services:
            service_names = []
            for service_id in master.services:
                service = await service_repo.get_service_by_id(service_id)
                if service:
                    service_names.append(service.name)
            response += f"{', '.join(service_names)}\n"

        response += "\n"

    await callback.message.edit_text(response, reply_markup=keyboards.back_to_admin())
    await callback.answer()


@admin_router.callback_query(F.data == "admin_list_orders")
async def list_orders(callback: CallbackQuery):
    orders = await order_repo.get_all(limit=20)

    if not orders:
        await callback.answer(messages.NO_ORDERS, show_alert=True)
        return

    response = messages.ORDERS_LIST

    for order in orders:
        service = await service_repo.get_service_by_id(order.service_id)
        service_type = await service_repo.get_service_type_by_id(order.service_type_id)

        response += f"ID #{order.id}\n"
        response += f"{service.name} - {service_type.name}\n"
        response += f"{order.user_phone}\n"

        if order.master_id:
            master = await master_repo.get_by_id(order.master_id)
            if master:
                response += f"Usta: {master.full_name}\n"

        response += f"{order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        response += f"{order.status}\n\n"

    await callback.message.edit_text(response, reply_markup=keyboards.back_to_admin())
    await callback.answer()

# ============================================================
# MAIN
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def on_startup():
    logger.info("Starting bot...")
    await db.connect()
    logger.info("Bot started successfully")


async def on_shutdown():
    logger.info("Shutting down bot...")
    await db.disconnect()
    logger.info("Bot stopped successfully")


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(common_router)
    dp.include_router(order_router)
    dp.include_router(admin_router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
