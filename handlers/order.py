from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from models import OrderStates
from repositories import service_repo, master_repo, user_repo
from services import order_service
from keyboards import keyboards
from utils import messages
import re

router = Router()


@router.message(F.text == "🛠 Buyurtma berish")
async def start_order(message: Message, state: FSMContext):
    """Start order creation process"""
    services = await service_repo.get_all_services()
    
    await message.answer(
        messages.SELECT_SERVICE,
        reply_markup=keyboards.services(services)
    )
    await state.set_state(OrderStates.choosing_service)


@router.callback_query(F.data.startswith("service_"), OrderStates.choosing_service)
async def service_selected(callback: CallbackQuery, state: FSMContext):
    """Handle service selection"""
    service_id = int(callback.data.split("_")[1])
    
    # Save service ID
    await state.update_data(service_id=service_id)
    
    # Get service types
    service_types = await service_repo.get_service_types(service_id)
    
    await callback.message.edit_text(
        messages.SELECT_SERVICE_TYPE,
        reply_markup=keyboards.service_types(service_types)
    )
    await state.set_state(OrderStates.choosing_service_type)
    await callback.answer()


@router.callback_query(F.data == "back_to_services", OrderStates.choosing_service_type)
async def back_to_services(callback: CallbackQuery, state: FSMContext):
    """Go back to service selection"""
    services = await service_repo.get_all_services()
    
    await callback.message.edit_text(
        messages.SELECT_SERVICE,
        reply_markup=keyboards.services(services)
    )
    await state.set_state(OrderStates.choosing_service)
    await callback.answer()


@router.callback_query(F.data.startswith("type_"), OrderStates.choosing_service_type)
async def service_type_selected(callback: CallbackQuery, state: FSMContext):
    """Handle service type selection"""
    service_type_id = int(callback.data.split("_")[1])
    
    # Save service type ID
    await state.update_data(service_type_id=service_type_id)
    
    await callback.message.answer(
        messages.SEND_LOCATION,
        reply_markup=keyboards.location_request()
    )
    await state.set_state(OrderStates.waiting_location)
    await callback.answer()


@router.message(F.location, OrderStates.waiting_location)
async def location_received(message: Message, state: FSMContext):
    """Handle location from user"""
    location = message.location
    
    # Save location
    await state.update_data(
        location_latitude=location.latitude,
        location_longitude=location.longitude,
        location_address=None
    )
    
    await message.answer(
        messages.SEND_PHONE,
        reply_markup=keyboards.phone_request()
    )
    await state.set_state(OrderStates.waiting_phone)


@router.message(F.text, OrderStates.waiting_location)
async def location_text_received(message: Message, state: FSMContext):
    """Handle location as text"""
    if message.text in ["⬅️ Orqaga", "❌ Bekor qilish"]:
        return
    
    # Save location as text
    await state.update_data(
        location_latitude=None,
        location_longitude=None,
        location_address=message.text
    )
    
    await message.answer(
        messages.SEND_PHONE,
        reply_markup=keyboards.phone_request()
    )
    await state.set_state(OrderStates.waiting_phone)


@router.message(F.contact, OrderStates.waiting_phone)
async def contact_received(message: Message, state: FSMContext):
    """Handle contact from user"""
    phone = message.contact.phone_number
    
    # Update user's phone in database
    await user_repo.update_phone(message.from_user.id, phone)
    
    # Save phone
    await state.update_data(user_phone=phone)
    
    # Show confirmation
    await show_order_confirmation(message, state)


@router.message(F.text.regexp(r'^\+?\d{9,15}$'), OrderStates.waiting_phone)
async def phone_text_received(message: Message, state: FSMContext):
    """Handle phone number as text"""
    phone = message.text.strip()
    
    # Validate phone format
    if not re.match(r'^\+?\d{9,15}$', phone):
        await message.answer(messages.ERROR_INVALID_PHONE)
        return
    
    # Update user's phone in database
    await user_repo.update_phone(message.from_user.id, phone)
    
    # Save phone
    await state.update_data(user_phone=phone)
    
    # Show confirmation
    await show_order_confirmation(message, state)


async def show_order_confirmation(message: Message, state: FSMContext):
    """Show order confirmation to user"""
    data = await state.get_data()
    
    # Get service and service type names
    service = await service_repo.get_service_by_id(data['service_id'])
    service_type = await service_repo.get_service_type_by_id(data['service_type_id'])
    
    # Format location
    location_text = data.get('location_address', 'Manzil ko\'rsatilmagan')
    if not location_text and data.get('location_latitude'):
        location_text = f"{data['location_latitude']}, {data['location_longitude']}"
    
    confirmation_text = messages.CONFIRM_ORDER.format(
        service=service.name,
        service_type=service_type.name,
        location=location_text,
        phone=data['user_phone']
    )
    
    await message.answer(
        confirmation_text,
        reply_markup=keyboards.confirm_order()
    )
    await state.set_state(OrderStates.confirming_order)


@router.callback_query(F.data == "confirm_yes", OrderStates.confirming_order)
async def confirm_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Handle order confirmation"""
    data = await state.get_data()
    
    # Create order
    order = await order_service.create_order(
        user_id=callback.from_user.id,
        service_id=data['service_id'],
        service_type_id=data['service_type_id'],
        user_phone=data['user_phone'],
        location_latitude=data.get('location_latitude'),
        location_longitude=data.get('location_longitude'),
        location_address=data.get('location_address')
    )
    
    # Notify master
    if order.master_id:
        master = await master_repo.get_by_id(order.master_id)
        await order_service.notify_master(bot, order, callback.from_user.first_name or "Mijoz")
        
        # Build username line
        username_line = ""
        if master.telegram_username:
            username_line = f"💬 Telegram: @{master.telegram_username}"
        
        success_message = messages.ORDER_SUCCESS.format(
            master_name=master.full_name,
            master_phone=master.phone_number,
            username_line=username_line
        )
    else:
        success_message = messages.ORDER_NO_MASTER
    
    await callback.message.edit_text(success_message)
    await callback.message.answer(
        "🏠 Bosh menyu",
        reply_markup=keyboards.main_menu()
    )
    
    # Clear state
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "confirm_no", OrderStates.confirming_order)
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    """Cancel order"""
    await state.clear()
    await callback.message.edit_text("❌ Buyurtma bekor qilindi")
    await callback.message.answer(
        "🏠 Bosh menyu",
        reply_markup=keyboards.main_menu()
    )
    await callback.answer()


@router.message(F.text == "📋 Mening buyurtmalarim")
async def my_orders(message: Message):
    """Show user's orders"""
    from repositories import order_repo
    
    orders = await order_repo.get_by_user(message.from_user.id)
    
    if not orders:
        await message.answer("📋 Sizda hali buyurtmalar yo'q")
        return
    
    response = "📋 Sizning buyurtmalaringiz:\n\n"
    
    for order in orders[:10]:  # Show last 10 orders
        service = await service_repo.get_service_by_id(order.service_id)
        service_type = await service_repo.get_service_type_by_id(order.service_type_id)
        
        response += f"🆔 #{order.id}\n"
        response += f"📋 {service.name} - {service_type.name}\n"
        response += f"📱 {order.user_phone}\n"
        response += f"📅 {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        response += f"📊 Status: {order.status}\n\n"
    
    await message.answer(response)
