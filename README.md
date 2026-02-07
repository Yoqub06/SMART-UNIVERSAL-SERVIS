# Telegram Bot - Uy Xizmatlari

Production-ready Telegram bot uy xizmatlarini buyurtma qilish uchun.

## 🚀 Xususiyatlar

- **Foydalanuvchi uchun:**
  - Xizmat turini tanlash (Konditsioner, Elektrika, Santexnika, Qurilish)
  - Ish turini tanlash (Ustanovka, Remont, Montaj, va boshqalar)
  - Lokatsiya yuborish
  - Telefon raqam yuborish
  - Buyurtmani tasdiqlash
  - O'z buyurtmalarini ko'rish

- **Usta uchun:**
  - Avtomatik buyurtma xabarlari
  - Mijoz ma'lumotlari (ism, telefon, lokatsiya)
  - Xizmat va ish turi ma'lumotlari

- **Admin uchun:**
  - Ustalarni qo'shish/o'chirish
  - Ustalarni xizmatlarga biriktirish
  - Barcha buyurtmalarni ko'rish
  - Barcha ustalarni ko'rish

## 📋 Talablar

- Python 3.11+
- PostgreSQL 14+
- Telegram Bot Token

## 🛠 O'rnatish

### 1. Repositoriyani klonlash

```bash
git clone <repository-url>
cd home_services_bot
```

### 2. Virtual environment yaratish

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows
```

### 3. Kerakli kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 4. PostgreSQL database yaratish

```bash
# PostgreSQL ga kirish
psql -U postgres

# Database yaratish
CREATE DATABASE home_services_bot;

# Foydalanuvchi yaratish (ixtiyoriy)
CREATE USER bot_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE home_services_bot TO bot_user;
```

### 5. Database sxemasini import qilish

```bash
psql -U postgres -d home_services_bot -f schema.sql
```

### 6. Environment sozlamalari

`.env.example` faylidan `.env` yarating va to'ldiring:

```bash
cp .env.example .env
```

`.env` faylini tahrirlang:

```env
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_IDS=123456789,987654321  # Admin Telegram ID'lari (vergul bilan ajratilgan)

DB_HOST=localhost
DB_PORT=5432
DB_NAME=home_services_bot
DB_USER=postgres
DB_PASSWORD=your_password
```

### 7. Botni ishga tushirish

```bash
python main.py
```

## 📁 Loyiha tuzilishi

```
home_services_bot/
├── config/              # Sozlamalar
│   ├── __init__.py
│   └── settings.py
├── models/              # Database modellari va FSM states
│   ├── __init__.py
│   ├── database.py
│   └── states.py
├── repositories/        # Database operatsiyalari
│   ├── __init__.py
│   ├── user_repo.py
│   ├── service_repo.py
│   ├── master_repo.py
│   └── order_repo.py
├── services/            # Business logika
│   ├── __init__.py
│   └── order_service.py
├── handlers/            # Telegram bot handlers
│   ├── __init__.py
│   ├── common.py
│   ├── order.py
│   └── admin.py
├── keyboards/           # Klaviatura builderlari
│   └── __init__.py
├── middlewares/         # Middleware'lar
│   ├── __init__.py
│   └── admin.py
├── utils/               # Yordamchi funksiyalar
│   ├── __init__.py
│   ├── database.py
│   └── messages.py
├── main.py              # Asosiy fayl
├── schema.sql           # Database sxemasi
├── requirements.txt     # Python dependencies
└── README.md           # Dokumentatsiya
```

## 🎯 Foydalanish

### Oddiy foydalanuvchi

1. Botni ishga tushiring: `/start`
2. "🛠 Buyurtma berish" tugmasini bosing
3. Xizmat turini tanlang
4. Ish turini tanlang
5. Lokatsiyani yuboring
6. Telefon raqamingizni yuboring
7. Buyurtmani tasdiqlang

### Admin

1. `/admin` komandasini yuboring
2. Quyidagi amallarni bajaring:
   - ➕ Usta qo'shish
   - ➖ Usta o'chirish
   - 👥 Ustalar ro'yxati
   - 📋 Buyurtmalar

## 🗄 Database Sxemasi

### Tables

- **users** - Foydalanuvchilar
- **services** - Xizmatlar (Konditsioner, Elektrika, va h.k.)
- **service_types** - Xizmat turlari (Ustanovka, Remont, va h.k.)
- **masters** - Ustalar
- **master_services** - Usta va xizmatlar bog'lanishi (many-to-many)
- **orders** - Buyurtmalar

## 🔐 Xavfsizlik

- Admin funksiyalari faqat `.env` faylidagi `ADMIN_IDS` ro'yxatidagi foydalanuvchilarga ochiq
- Database parollari environment variablelarda saqlanadi
- Bot token environment variabledan yuklanadi

## 🚀 Production uchun tavsiyalar

1. **Systemd service yarating** (Linux):

```bash
sudo nano /etc/systemd/system/home-services-bot.service
```

```ini
[Unit]
Description=Home Services Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/home_services_bot
Environment="PATH=/path/to/home_services_bot/venv/bin"
ExecStart=/path/to/home_services_bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **Service'ni ishga tushirish**:

```bash
sudo systemctl daemon-reload
sudo systemctl enable home-services-bot
sudo systemctl start home-services-bot
sudo systemctl status home-services-bot
```

3. **Loglarni ko'rish**:

```bash
sudo journalctl -u home-services-bot -f
```

## 📝 Qo'shimcha sozlamalar

### Webhook o'rnatish (ixtiyoriy)

Polling o'rniga webhook ishlatish uchun `main.py` ni o'zgartiring:

```python
# main.py ichida
async def on_startup(bot: Bot):
    await db.connect()
    await bot.set_webhook(
        url=f"https://your-domain.com/webhook",
        drop_pending_updates=True
    )
```

### PostgreSQL backup

```bash
# Backup yaratish
pg_dump -U postgres home_services_bot > backup.sql

# Backup dan tiklash
psql -U postgres home_services_bot < backup.sql
```

## 🐛 Muammolarni hal qilish

### Bot ishlamayapti

1. `.env` faylini tekshiring
2. Database ulanishini tekshiring
3. Bot tokenni tekshiring
4. Loglarni ko'ring

### Database xatosi

1. PostgreSQL ishlab turganini tekshiring: `sudo systemctl status postgresql`
2. Database mavjudligini tekshiring: `psql -U postgres -l`
3. Schema import qilinganini tekshiring

## 📞 Yordam

Muammolar yoki savollar bo'lsa:
- Email: yoquballayev@example.com
- Telegram: @jacob_0_0_6
## 📄 Litsenziya

MIT License

## 👨‍💻 Muallif

Developed by JACOB
