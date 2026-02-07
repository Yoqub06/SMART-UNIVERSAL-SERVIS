from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    """States for order creation flow"""
    choosing_service = State()
    choosing_service_type = State()
    waiting_location = State()
    waiting_phone = State()
    confirming_order = State()


class AdminStates(StatesGroup):
    """States for admin panel"""
    # Master management
    waiting_master_first_name = State()
    waiting_master_last_name = State()
    waiting_master_username = State()
    waiting_master_phone = State()
    waiting_master_services = State()
    
    # Edit master
    selecting_master_to_edit = State()
    editing_master = State()
    
    # Delete master
    selecting_master_to_delete = State()
