# Arxitektura hujjatlari

## 📐 Loyiha arxitekturasi

Loyiha Clean Architecture prinsiplariga asoslanib qurilgan.

### Qatlamlar

```
┌─────────────────────────────────────────┐
│         Handlers (Presentation)         │
│  - Telegram xabarlarini qabul qilish    │
│  - Foydalanuvchi bilan muloqot          │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│        Services (Business Logic)        │
│  - Buyurtmalarni yaratish logikasi      │
│  - Ustalarga xabar yuborish             │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│      Repositories (Data Access)         │
│  - Database CRUD operatsiyalari         │
│  - Ma'lumotlarni olish/saqlash          │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         Database (PostgreSQL)           │
│  - Ma'lumotlar saqlash                  │
└─────────────────────────────────────────┘
```

## 🔄 FSM (Finite State Machine) Flow

### Buyurtma yaratish jarayoni

```
START
  ↓
[choosing_service] → Service tanlash
  ↓
[choosing_service_type] → Service type tanlash
  ↓
[waiting_location] → Lokatsiya yuborish
  ↓
[waiting_phone] → Telefon yuborish
  ↓
[confirming_order] → Buyurtmani tasdiqlash
  ↓
END (Order created, Master notified)
```

### Admin - Usta qo'shish jarayoni

```
START (/admin → add master)
  ↓
[waiting_master_first_name] → Ism kiritish
  ↓
[waiting_master_last_name] → Familiya kiritish
  ↓
[waiting_master_username] → Username kiritish (ixtiyoriy)
  ↓
[waiting_master_phone] → Telefon kiritish
  ↓
[waiting_master_services] → Xizmatlarni tanlash
  ↓
END (Master created)
```

## 🗄️ Database Schema

### ER Diagram

```
┌─────────────┐       ┌─────────────┐
│    users    │       │   orders    │
├─────────────┤       ├─────────────┤
│ id          │       │ id          │
│ telegram_id │◄──────┤ user_id     │
│ username    │       │ master_id   │───┐
│ first_name  │       │ service_id  │   │
│ phone       │       │ service_type│   │
└─────────────┘       │ location    │   │
                      │ phone       │   │
                      │ status      │   │
                      └─────────────┘   │
                                        │
┌─────────────┐       ┌─────────────┐  │
│  services   │       │   masters   │  │
├─────────────┤       ├─────────────┤  │
│ id          │       │ id          │◄─┘
│ name        │       │ first_name  │
└──────┬──────┘       │ last_name   │
       │              │ username    │
       │              │ phone       │
       │              │ telegram_id │
       │              └──────┬──────┘
       │                     │
       │   ┌─────────────────┴─────────────┐
       │   │   master_services (junction)  │
       │   ├───────────────────────────────┤
       └───┤ master_id                     │
           │ service_id                    │
           └───────────────────────────────┘
```

### Relationships

- **User → Orders**: One-to-Many (Bir foydalanuvchi ko'p buyurtma)
- **Master → Orders**: One-to-Many (Bir usta ko'p buyurtma)
- **Service → Orders**: One-to-Many
- **Master ↔ Services**: Many-to-Many (master_services orqali)

## 📦 Modullar tuzilishi

### config/
Loyiha sozlamalari va environment variables

### models/
- `database.py`: Database modellari (dataclasses)
- `states.py`: FSM states

### repositories/
Database bilan ishlash uchun data access layer:
- `user_repo.py`: Users jadvalida CRUD
- `service_repo.py`: Services va service_types jadvallari
- `master_repo.py`: Masters va master_services jadvallari
- `order_repo.py`: Orders jadvalida CRUD

### services/
Business logic layer:
- `order_service.py`: Buyurtmalarni yaratish va ustaga yuborish

### handlers/
Telegram bot handlers:
- `common.py`: /start, main menu
- `order.py`: Buyurtma yaratish jarayoni
- `admin.py`: Admin panel

### keyboards/
Telegram klaviaturalari (Reply va Inline keyboards)

### middlewares/
- `admin.py`: Admin huquqlarini tekshirish

### utils/
- `database.py`: Database connection pool
- `messages.py`: Bot xabarlari

## 🔐 Xavfsizlik mexanizmlari

1. **Admin middleware**: Faqat `.env` dagi admin ID'lar admin funksiyalariga kiradi
2. **SQL Injection himoyasi**: asyncpg parameterized queries ishlatadi
3. **Environment variables**: Maxfiy ma'lumotlar `.env` faylda
4. **Input validation**: Telefon raqam va boshqa inputlar validatsiya qilinadi

## 🚀 Scalability

Loyiha quyidagi usullarda scale qilish mumkin:

1. **Database**: PostgreSQL replication va sharding
2. **Bot instances**: Webhook + load balancer bilan bir nechta bot instance
3. **Caching**: Redis qo'shish tez-tez so'raladigan ma'lumotlar uchun
4. **Queue**: Celery qo'shish og'ir vazifalar uchun

## 🧪 Testing strategiyasi

```
tests/
├── unit/           # Unit tests
│   ├── test_repositories.py
│   ├── test_services.py
│   └── test_models.py
├── integration/    # Integration tests
│   └── test_handlers.py
└── e2e/           # End-to-end tests
    └── test_user_flow.py
```

## 📊 Monitoring va Logging

Production muhitda qo'shish tavsiya etiladigan vositalar:

1. **Sentry**: Xatolarni kuzatish
2. **Prometheus + Grafana**: Metrikalarni yig'ish va vizualizatsiya
3. **ELK Stack**: Loglarni yig'ish va tahlil qilish
4. **Telegram error notifications**: Xatolar haqida adminlarga xabar yuborish

## 🔄 CI/CD Pipeline

Tavsiya etiladigan CI/CD:

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: ./deploy.sh
```
