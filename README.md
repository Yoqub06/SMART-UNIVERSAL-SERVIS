# Telegram Bot - SMART-UNIVERSAL-SERVIS

Uy xizmatlari uchun Telegram bot.

## Stack
- Python 3.11+
- aiogram 3
- PostgreSQL

## Yangi ixcham tuzilma
Loyiha Python bo'yicha 4 ta asosiy faylga qisqartirildi:
- `main.py` - botni ishga tushirish
- `core.py` - settings, db, models, repository, service, middleware, keyboards, messages
- `handlers_user.py` - foydalanuvchi va buyurtma handlerlari
- `handlers_admin.py` - admin handlerlari

## O'rnatish (Windows)
1. Virtual environment:
```powershell
python -m venv venv
venv\Scripts\activate
```

2. Kutubxonalar:
```powershell
pip install -r requirements.txt
```

3. PostgreSQL database:
```sql
CREATE DATABASE home_services_bot;
```

4. Schema import:
```powershell
psql -U postgres -d home_services_bot -f schema.sql
```

5. `.env` fayl:
```env
BOT_TOKEN=your_bot_token
ADMIN_IDS=123456789
DB_HOST=localhost
DB_PORT=5432
DB_NAME=home_services_bot
DB_USER=postgres
DB_PASSWORD=your_password
```

6. Botni ishga tushirish:
```powershell
python main.py
```

## Eslatma
Ushbu versiyada Linuxga xos `.sh` deploy skriptlari olib tashlangan.
