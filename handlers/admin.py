from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from models import AdminStates
from repositories import master_repo, service_repo, order_repo
from keyboards import keyboards
from utils import messages
from middlewares import AdminMiddleware
import re

router = Router()
router.message.middleware(AdminMiddleware())
router.callback_query.middleware(AdminMiddleware())


@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    """Show admin panel"""
    await state.clear()
    await message.answer(
        messages.ADMIN_PANEL,
        reply_markup=keyboards.admin_panel()
    )


@router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery, state: FSMContext):
    """Return to admin panel"""
    await state.clear()
    await callback.message.edit_text(
        messages.ADMIN_PANEL,
        reply_markup=keyboards.admin_panel()
    )
    await callback.answer()


# ============ ADD MASTER ============

@router.callback_query(F.data == "admin_add_master")
async def add_master_start(callback: CallbackQuery, state: FSMContext):
    """Start adding new master"""
    await callback.message.answer(messages.MASTER_ADD_FIRST_NAME)
    await state.set_state(AdminStates.waiting_master_first_name)
    await callback.answer()


@router.message(AdminStates.waiting_master_first_name)
async def master_first_name(message: Message, state: FSMContext):
    """Receive master's first name"""
    await state.update_data(first_name=message.text.strip())
    await message.answer(messages.MASTER_ADD_LAST_NAME)
    await state.set_state(AdminStates.waiting_master_last_name)


@router.message(AdminStates.waiting_master_last_name)
async def master_last_name(message: Message, state: FSMContext):
    """Receive master's last name"""
    await state.update_data(last_name=message.text.strip())
    await message.answer(messages.MASTER_ADD_USERNAME, reply_markup=keyboards.cancel())
    await state.set_state(AdminStates.waiting_master_username)


@router.message(AdminStates.waiting_master_username)
async def master_username(message: Message, state: FSMContext):
    """Receive master's username"""
    username = None
    if message.text and message.text != "/skip":
        username = message.text.strip().lstrip("@")
    
    await state.update_data(username=username)
    await message.answer(messages.MASTER_ADD_PHONE)
    await state.set_state(AdminStates.waiting_master_phone)


@router.message(AdminStates.waiting_master_phone)
async def master_phone(message: Message, state: FSMContext):
    """Receive master's phone number"""
    phone = message.text.strip()
    
    # Validate phone format
    if not re.match(r'^\+?\d{9,15}$', phone):
        await message.answer(messages.ERROR_INVALID_PHONE)
        return
    
    await state.update_data(phone=phone)
    
    # Show services selection
    services = await service_repo.get_all_services()
    service_list = "\n".join([f"{s.id}. {s.name}" for s in services])
    
    await message.answer(
        f"{messages.MASTER_ADD_SERVICES}\n\n{service_list}"
    )
    await state.set_state(AdminStates.waiting_master_services)


@router.message(AdminStates.waiting_master_services)
async def master_services(message: Message, state: FSMContext):
    """Receive master's services"""
    try:
        # Parse service IDs
        service_ids = [int(x.strip()) for x in message.text.split(",")]
        
        # Validate service IDs
        all_services = await service_repo.get_all_services()
        valid_ids = [s.id for s in all_services]
        
        invalid = [sid for sid in service_ids if sid not in valid_ids]
        if invalid:
            await message.answer(f"❌ Noto'g'ri xizmat ID: {invalid}")
            return
        
        # Get master data
        data = await state.get_data()
        
        # Create master
        master = await master_repo.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data['phone'],
            telegram_username=data.get('username'),
            service_ids=service_ids
        )
        
        await message.answer(
            f"{messages.MASTER_ADDED}\n\n"
            f"👤 {master.full_name}\n"
            f"📱 {master.phone_number}",
            reply_markup=keyboards.back_to_admin()
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer(messages.ERROR_INVALID_INPUT)


# ============ DELETE MASTER ============

@router.callback_query(F.data == "admin_delete_master")
async def delete_master_start(callback: CallbackQuery, state: FSMContext):
    """Start deleting master"""
    masters = await master_repo.get_all(active_only=False)
    
    if not masters:
        await callback.answer(messages.NO_MASTERS, show_alert=True)
        return
    
    await callback.message.edit_text(
        messages.SELECT_MASTER_TO_DELETE,
        reply_markup=keyboards.masters_list(masters, action="delete")
    )
    await state.set_state(AdminStates.selecting_master_to_delete)
    await callback.answer()


@router.callback_query(F.data.startswith("delete_master_"), AdminStates.selecting_master_to_delete)
async def delete_master_confirm(callback: CallbackQuery, state: FSMContext):
    """Confirm and delete master"""
    master_id = int(callback.data.split("_")[2])
    
    master = await master_repo.get_by_id(master_id)
    if not master:
        await callback.answer(messages.MASTER_NOT_FOUND, show_alert=True)
        return
    
    # Delete master (soft delete)
    await master_repo.delete(master_id)
    
    await callback.message.edit_text(
        f"{messages.MASTER_DELETED}\n\n"
        f"👤 {master.full_name}",
        reply_markup=keyboards.back_to_admin()
    )
    
    await state.clear()
    await callback.answer()


# ============ LIST MASTERS ============

@router.callback_query(F.data == "admin_list_masters")
async def list_masters(callback: CallbackQuery):
    """Show all masters"""
    masters = await master_repo.get_all(active_only=False)
    
    if not masters:
        await callback.answer(messages.NO_MASTERS, show_alert=True)
        return
    
    response = messages.MASTERS_LIST
    
    for master in masters:
        status = "✅" if master.is_active else "❌"
        response += f"{status} {master.full_name}\n"
        response += f"📱 {master.phone_number}\n"
        
        if master.telegram_username:
            response += f"💬 @{master.telegram_username}\n"
        
        # Get master's services
        if master.services:
            service_names = []
            for service_id in master.services:
                service = await service_repo.get_service_by_id(service_id)
                if service:
                    service_names.append(service.name)
            response += f"🛠 {', '.join(service_names)}\n"
        
        response += "\n"
    
    await callback.message.edit_text(
        response,
        reply_markup=keyboards.back_to_admin()
    )
    await callback.answer()


# ============ LIST ORDERS ============

@router.callback_query(F.data == "admin_list_orders")
async def list_orders(callback: CallbackQuery):
    """Show all orders"""
    orders = await order_repo.get_all(limit=20)
    
    if not orders:
        await callback.answer(messages.NO_ORDERS, show_alert=True)
        return
    
    response = messages.ORDERS_LIST
    
    for order in orders:
        service = await service_repo.get_service_by_id(order.service_id)
        service_type = await service_repo.get_service_type_by_id(order.service_type_id)
        
        response += f"🆔 #{order.id}\n"
        response += f"📋 {service.name} - {service_type.name}\n"
        response += f"📱 {order.user_phone}\n"
        
        if order.master_id:
            master = await master_repo.get_by_id(order.master_id)
            if master:
                response += f"👨‍🔧 Usta: {master.full_name}\n"
        
        response += f"📅 {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        response += f"📊 {order.status}\n\n"
    
    await callback.message.edit_text(
        response,
        reply_markup=keyboards.back_to_admin()
    )
    await callback.answer()
