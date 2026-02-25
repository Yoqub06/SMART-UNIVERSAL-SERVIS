# Windows Quick Start (to'liq 3 fayl bilan)

Bu variantda botning **asosiy ishlashi 3 ta fayl** ichida:

- `main_3files.py`
- `flows_3files.py`
- `db_3files.py`

> Mavjud eski papkalar (`handlers/`, `services/`, `repositories/`...) o'chirilmaydi. Lekin 3-faylli rejim ularga bog'liq emas.

## 1) Talablar

- Python 3.11+
- PostgreSQL 14+
- Telegram bot token

## 2) Loyihani ochish

```powershell
cd C:\path\to\SMART-UNIVERSAL-SERVIS
```

## 3) Virtual environment

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
```

Agar PowerShell policy xatolik bersa:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## 4) Kutubxonalarni o'rnatish

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5) Database tayyorlash

```powershell
psql -U postgres -c "CREATE DATABASE home_services_bot;"
psql -U postgres -d home_services_bot -f schema.sql
```

## 6) `.env` fayl yaratish

```powershell
Copy-Item .env.example .env
notepad .env
```

Quyidagilarni to'ldiring:

```env
BOT_TOKEN=your_bot_token
ADMIN_IDS=123456789
DB_HOST=localhost
DB_PORT=5432
DB_NAME=home_services_bot
DB_USER=postgres
DB_PASSWORD=your_password
```

## 7) Botni ishga tushirish

```powershell
python main_3files.py
```

## 8) Tekshirish

- `/start` yuboring
- `🛠 Buyurtma berish` bilan order flow ni sinang
- `/admin` orqali admin panelni oching (ID `.env` da bo'lishi kerak)
