# 🚀 Quick Start Guide

## Tezkor boshlash (5 daqiqa)

### 1. Talablar

- Python 3.11 yoki yuqori
- PostgreSQL 14 yoki yuqori
- Telegram Bot Token (@BotFather dan olingan)

### 2. O'rnatish

```bash
# 1. Loyihani yuklab oling
cd home_services_bot

# 2. Virtual environment yarating
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate     # Windows

# 3. Dependencies o'rnatish
pip install -r requirements.txt

# 4. PostgreSQL database yaratish
sudo -u postgres psql
CREATE DATABASE home_services_bot;
\q

# 5. Database sxemasini import qilish
psql -U postgres -d home_services_bot -f schema.sql

# 6. .env faylini yaratish va to'ldirish
cp .env.example .env
nano .env  # yoki istalgan text editor
```

### 3. .env faylini sozlash

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz  # @BotFather dan olingan
ADMIN_IDS=123456789,987654321                    # Sizning Telegram ID'ingiz

DB_HOST=localhost
DB_PORT=5432
DB_NAME=home_services_bot
DB_USER=postgres
DB_PASSWORD=your_password
```

### 4. Telegram ID ni topish

1. [@userinfobot](https://t.me/userinfobot) ga /start yuboring
2. Sizning ID ni ko'rsatadi
3. Shu ID ni `.env` faylida `ADMIN_IDS` ga qo'shing

### 5. Botni ishga tushirish

```bash
python main.py
```

Agar hamma narsa to'g'ri bo'lsa, quyidagi xabarni ko'rasiz:

```
✅ Database connected successfully
🤖 Starting bot...
✅ Bot started successfully!
```

### 6. Botni tekshirish

1. Telegram da botingizni toping
2. `/start` ni yuboring
3. Xush kelibsiz xabarini ko'rasiz
4. "🛠 Buyurtma berish" tugmasini bosing

### 7. Admin panel

1. `/admin` komandani yuboring
2. Admin panelni ko'rasiz
3. "➕ Usta qo'shish" tugmasini bosib usta qo'shing

## Tez-tez so'raladigan savollar

### Botni to'xtatish

```bash
# Terminal da Ctrl+C bosing
```

### Database ni reset qilish

```bash
sudo -u postgres psql -d home_services_bot -f schema.sql
```

### Loglarni ko'rish

Bot ishlab turganida barcha loglar terminalda ko'rinadi.

### Production muhitda ishga tushirish

```bash
# Deploy scriptni ishga tushiring (faqat Linux)
sudo ./deploy.sh
```

Bu script:
- Barcha dependencies ni o'rnatadi
- Database ni sozlaydi
- Systemd service yaratadi
- Botni avtomat ishga tushiradi

### Muammolar

#### Database ulanish xatosi

```bash
# PostgreSQL ishlab turganini tekshiring
sudo systemctl status postgresql

# Agar ishlamasa, ishga tushiring
sudo systemctl start postgresql
```

#### Bot token xatosi

- `.env` fayldagi `BOT_TOKEN` ni tekshiring
- @BotFather dan yangi token oling

#### Admin panel ochilmaydi

- `.env` fayldagi `ADMIN_IDS` ni tekshiring
- O'z Telegram ID ingizni to'g'ri kiritganingizni tasdiqlang

## Keyingi qadamlar

1. [README.md](README.md) - To'liq dokumentatsiya
2. [ARCHITECTURE.md](ARCHITECTURE.md) - Arxitektura tushuntirish
3. [API.md](API.md) - Developer API hujjatlari
4. [TESTING.md](TESTING.md) - Test qilish yo'riqnomasi

## Yordam

Muammolar yuzaga kelsa:

1. Loglarni diqqat bilan o'qing
2. `.env` faylni tekshiring
3. Database ulanishini tekshiring
4. GitHub Issues da savol bering

---

**Muvaffaqiyat!** 🎉
