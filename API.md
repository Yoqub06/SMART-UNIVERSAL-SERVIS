# API Documentation

## Repository API

### UserRepository

```python
from repositories import user_repo

# Get or create user
user = await user_repo.get_or_create(
    telegram_id=123456789,
    username="john_doe",
    first_name="John"
)

# Get user by telegram ID
user = await user_repo.get_by_telegram_id(123456789)

# Update user's phone
await user_repo.update_phone(123456789, "+998901234567")
```

### ServiceRepository

```python
from repositories import service_repo

# Get all services
services = await service_repo.get_all_services()

# Get service by ID
service = await service_repo.get_service_by_id(1)

# Get service types for a service
service_types = await service_repo.get_service_types(service_id=1)

# Get service type by ID
service_type = await service_repo.get_service_type_by_id(1)
```

### MasterRepository

```python
from repositories import master_repo

# Create master
master = await master_repo.create(
    first_name="Alisher",
    last_name="Karimov",
    phone_number="+998901234567",
    telegram_username="alisher_master",
    telegram_id=123456789,
    service_ids=[1, 2, 3]  # Service IDs
)

# Get master by ID
master = await master_repo.get_by_id(1)

# Get all masters
masters = await master_repo.get_all(active_only=True)

# Get masters by service
masters = await master_repo.get_by_service(service_id=1)

# Update master's services
await master_repo.update_services(
    master_id=1,
    service_ids=[1, 2]
)

# Delete master (soft delete)
await master_repo.delete(master_id=1)

# Delete permanently
await master_repo.delete_permanently(master_id=1)
```

### OrderRepository

```python
from repositories import order_repo

# Create order
order = await order_repo.create(
    user_id=123456789,
    service_id=1,
    service_type_id=1,
    user_phone="+998901234567",
    location_latitude=41.2995,
    location_longitude=69.2401,
    location_address="Tashkent, Chilanzar",
    master_id=1
)

# Get order by ID
order = await order_repo.get_by_id(1)

# Get all orders
orders = await order_repo.get_all(limit=50)

# Get orders by user
orders = await order_repo.get_by_user(user_id=123456789)

# Get orders by master
orders = await order_repo.get_by_master(master_id=1)

# Update order status
await order_repo.update_status(order_id=1, status="completed")
```

## Service API

### OrderService

```python
from services import order_service
from aiogram import Bot

# Create order and assign to master
order = await order_service.create_order(
    user_id=123456789,
    service_id=1,
    service_type_id=1,
    user_phone="+998901234567",
    location_latitude=41.2995,
    location_longitude=69.2401,
    location_address="Tashkent, Chilanzar"
)

# Notify master about new order
bot = Bot(token="YOUR_TOKEN")
success = await order_service.notify_master(
    bot=bot,
    order=order,
    user_first_name="John"
)

# Get order details (formatted)
details = await order_service.get_order_details(order)
# Returns: {
#   'service': 'Konditsioner',
#   'service_type': 'Ustanovka',
#   'location': 'Tashkent, Chilanzar',
#   'phone': '+998901234567'
# }
```

## Database Models

### User

```python
@dataclass
class User:
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    phone_number: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### Service

```python
@dataclass
class Service:
    id: int
    name: str
    created_at: Optional[datetime] = None
```

### ServiceType

```python
@dataclass
class ServiceType:
    id: int
    service_id: int
    name: str
    created_at: Optional[datetime] = None
```

### Master

```python
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
```

### Order

```python
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
    status: str = 'pending'
    notes: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

## FSM States

### OrderStates

```python
class OrderStates(StatesGroup):
    choosing_service = State()
    choosing_service_type = State()
    waiting_location = State()
    waiting_phone = State()
    confirming_order = State()
```

### AdminStates

```python
class AdminStates(StatesGroup):
    waiting_master_first_name = State()
    waiting_master_last_name = State()
    waiting_master_username = State()
    waiting_master_phone = State()
    waiting_master_services = State()
    selecting_master_to_edit = State()
    editing_master = State()
    selecting_master_to_delete = State()
```

## Keyboard Builders

```python
from keyboards import keyboards

# Main menu
keyboard = keyboards.main_menu()

# Phone request
keyboard = keyboards.phone_request()

# Location request
keyboard = keyboards.location_request()

# Services selection
services = await service_repo.get_all_services()
keyboard = keyboards.services(services)

# Service types selection
service_types = await service_repo.get_service_types(service_id=1)
keyboard = keyboards.service_types(service_types)

# Order confirmation
keyboard = keyboards.confirm_order()

# Admin panel
keyboard = keyboards.admin_panel()

# Services selection for master (with checkboxes)
keyboard = keyboards.services_selection(
    services=services,
    selected=[1, 2]  # Selected service IDs
)

# Masters list
masters = await master_repo.get_all()
keyboard = keyboards.masters_list(
    masters=masters,
    action="delete"  # or "edit"
)
```

## Database Utilities

```python
from utils import db

# Connect to database
await db.connect()

# Disconnect
await db.disconnect()

# Execute query (no results)
await db.execute("UPDATE users SET phone = $1 WHERE telegram_id = $2", phone, tid)

# Fetch multiple rows
rows = await db.fetch("SELECT * FROM users")

# Fetch single row
row = await db.fetchrow("SELECT * FROM users WHERE telegram_id = $1", tid)

# Fetch single value
count = await db.fetchval("SELECT COUNT(*) FROM users")
```

## Messages

```python
from utils import messages

# Use predefined messages
await message.answer(messages.WELCOME)
await message.answer(messages.SELECT_SERVICE)

# Format messages
text = messages.CONFIRM_ORDER.format(
    service="Konditsioner",
    service_type="Ustanovka",
    location="Tashkent",
    phone="+998901234567"
)
```

## Configuration

```python
from config import settings

# Access settings
bot_token = settings.BOT_TOKEN
admin_ids = settings.admin_ids_list  # List[int]
db_url = settings.database_url
```

## Middleware Usage

```python
from middlewares import AdminMiddleware
from aiogram import Router

router = Router()

# Apply middleware to all handlers in router
router.message.middleware(AdminMiddleware())
router.callback_query.middleware(AdminMiddleware())
```

## Handler Examples

### Simple handler

```python
from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == "Hello")
async def hello_handler(message: Message):
    await message.answer("Hi there!")
```

### Handler with FSM

```python
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from models import OrderStates

router = Router()

@router.message(OrderStates.waiting_phone)
async def phone_handler(message: Message, state: FSMContext):
    # Save data
    await state.update_data(phone=message.text)
    
    # Get data
    data = await state.get_data()
    
    # Clear state
    await state.clear()
```

### Callback handler

```python
from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(F.data.startswith("service_"))
async def service_callback(callback: CallbackQuery):
    service_id = int(callback.data.split("_")[1])
    await callback.answer("Service selected!")
    await callback.message.edit_text(f"You selected service {service_id}")
```
