from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from repositories import user_repo
from keyboards import keyboards
from utils import messages

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    # Clear any existing state
    await state.clear()
    
    # Get or create user
    await user_repo.get_or_create(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    await message.answer(
        messages.WELCOME,
        reply_markup=keyboards.main_menu()
    )


@router.message(F.text == "🏠 Bosh menyu")
@router.message(F.text == "❌ Bekor qilish")
async def main_menu(message: Message, state: FSMContext):
    """Return to main menu"""
    await state.clear()
    await message.answer(
        "🏠 Bosh menyu",
        reply_markup=keyboards.main_menu()
    )
