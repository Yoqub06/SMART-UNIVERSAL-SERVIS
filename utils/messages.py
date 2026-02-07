"""Text messages for the bot"""


class Messages:
    """Bot messages"""
    
    # Welcome messages
    WELCOME = """
👋 Assalomu alaykum!

Uy xizmatlariga buyurtma berish botiga xush kelibsiz.

Quyidagi xizmatlardan birini tanlang:
"""
    
    # Service selection
    SELECT_SERVICE = "Quyidagi xizmatlardan birini tanlang:"
    SELECT_SERVICE_TYPE = "Qaysi turdagi ishni bajarishingiz kerak?"
    
    # Location
    SEND_LOCATION = """
📍 Iltimos, manzilni yuboring.

Pastdagi "📍 Lokatsiya yuborish" tugmasini bosing yoki xarita orqali manzilni tanlang.
"""
    
    # Phone number
    SEND_PHONE = """
📱 Iltimos, telefon raqamingizni yuboring.

Pastdagi "📞 Raqam yuborish" tugmasini bosing.
"""
    
    # Order confirmation
    CONFIRM_ORDER = """
✅ Buyurtmangizni tasdiqlang:

📋 Xizmat: {service}
🔧 Ish turi: {service_type}
📍 Manzil: {location}
📱 Telefon: {phone}

Buyurtmani tasdiqlamoqchimisiz?
"""
    
    # Success messages
    ORDER_SUCCESS = """
✅ Buyurtma muvaffaqiyatli qabul qilindi!

Tez orada usta siz bilan bog'lanadi.

📱 Usta bilan bog'lanish:
👤 Ism: {master_name}
📞 Telefon: {master_phone}
{username_line}
"""
    
    ORDER_NO_MASTER = """
✅ Buyurtma qabul qilindi!

Afsuski, hozirda bu xizmat uchun mavjud usta yo'q. 
Adminlar tez orada siz bilan bog'lanadi.
"""
    
    # Master notification
    MASTER_NOTIFICATION = """
🔔 Yangi buyurtma!

👤 Mijoz: {client_name}
📱 Telefon: {client_phone}
📋 Xizmat: {service}
🔧 Ish turi: {service_type}
📍 Manzil: {location}

⏰ Vaqt: {time}
"""
    
    # Admin messages
    ADMIN_PANEL = """
🔐 Admin Panel

Quyidagi amallardan birini tanlang:
"""
    
    MASTER_ADD_FIRST_NAME = "Ustaning ismini kiriting:"
    MASTER_ADD_LAST_NAME = "Ustaning familiyasini kiriting:"
    MASTER_ADD_USERNAME = "Ustaning Telegram username'ini kiriting (@ belgisisiz) yoki o'tkazib yuborish uchun /skip ni bosing:"
    MASTER_ADD_PHONE = "Ustaning telefon raqamini kiriting (+998 formatida):"
    MASTER_ADD_SERVICES = "Usta qaysi xizmatlarni ko'rsatadi? Raqamlarni vergul bilan ajrating (masalan: 1,2,3)"
    
    MASTER_ADDED = "✅ Usta muvaffaqiyatli qo'shildi!"
    MASTER_DELETED = "✅ Usta o'chirildi!"
    MASTER_NOT_FOUND = "❌ Usta topilmadi"
    
    MASTERS_LIST = "👥 Barcha ustalar:\n\n"
    NO_MASTERS = "❌ Hozircha ustalar yo'q"
    
    ORDERS_LIST = "📋 Barcha buyurtmalar:\n\n"
    NO_ORDERS = "❌ Hozircha buyurtmalar yo'q"
    
    SELECT_MASTER_TO_DELETE = "O'chirish uchun ustani tanlang:"
    
    # Error messages
    ERROR_GENERAL = "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring."
    ERROR_INVALID_PHONE = "❌ Noto'g'ri telefon raqam formati. Iltimos, +998 bilan boshlangan raqam kiriting."
    ERROR_INVALID_INPUT = "❌ Noto'g'ri ma'lumot. Iltimos, qaytadan urinib ko'ring."
    
    # Buttons
    BTN_BACK = "⬅️ Orqaga"
    BTN_CANCEL = "❌ Bekor qilish"
    BTN_CONFIRM = "✅ Tasdiqlash"
    BTN_MAIN_MENU = "🏠 Bosh menyu"
    
    # Admin buttons
    BTN_ADD_MASTER = "➕ Usta qo'shish"
    BTN_DELETE_MASTER = "➖ Usta o'chirish"
    BTN_LIST_MASTERS = "👥 Ustalar ro'yxati"
    BTN_LIST_ORDERS = "📋 Buyurtmalar"
    BTN_BACK_TO_ADMIN = "⬅️ Admin paneliga qaytish"


messages = Messages()
