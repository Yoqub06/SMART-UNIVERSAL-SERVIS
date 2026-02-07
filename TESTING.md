# Testing Guide

## Manual Testing Checklist

### 1. Foydalanuvchi flow

#### Buyurtma berish jarayoni

- [ ] Botni ishga tushirish `/start`
- [ ] "🛠 Buyurtma berish" tugmasini bosish
- [ ] Xizmat tanlash (masalan: Konditsioner)
- [ ] Xizmat turini tanlash (masalan: Ustanovka)
- [ ] Lokatsiya yuborish (GPS yoki matn)
- [ ] Telefon raqam yuborish (kontakt yoki matn)
- [ ] Buyurtmani tasdiqlash
- [ ] Usta haqida ma'lumot olish
- [ ] Usta xabar olganini tekshirish

#### Orqaga qaytish

- [ ] Xizmat tanlashdan orqaga qaytish
- [ ] Lokatsiya yuborishdan orqaga qaytish
- [ ] Har qanday bosqichda "Bekor qilish" tugmasi

#### Mening buyurtmalarim

- [ ] "📋 Mening buyurtmalarim" tugmasini bosish
- [ ] Buyurtmalar ro'yxatini ko'rish
- [ ] Bo'sh ro'yxat uchun xabar

### 2. Admin flow

#### Admin paneliga kirish

- [ ] `/admin` komandasi (admin ID bilan)
- [ ] `/admin` komandasi (admin bo'lmagan ID bilan - rad etilishi kerak)

#### Usta qo'shish

- [ ] "➕ Usta qo'shish" tugmasini bosish
- [ ] Ism kiritish
- [ ] Familiya kiritish
- [ ] Username kiritish (ixtiyoriy)
- [ ] Username o'tkazib yuborish (`/skip`)
- [ ] Telefon raqam kiritish (to'g'ri format)
- [ ] Telefon raqam kiritish (noto'g'ri format - xato bo'lishi kerak)
- [ ] Xizmatlarni tanlash (masalan: 1,2,3)
- [ ] Noto'g'ri xizmat ID (xato bo'lishi kerak)
- [ ] Usta yaratilganini tasdiqlash

#### Usta o'chirish

- [ ] "➖ Usta o'chirish" tugmasini bosish
- [ ] Ustani ro'yxatdan tanlash
- [ ] O'chirilganini tasdiqlash
- [ ] Usta yangi buyurtma olmasligini tekshirish

#### Ustalar ro'yxati

- [ ] "👥 Ustalar ro'yxati" tugmasini bosish
- [ ] Barcha ustalarni ko'rish
- [ ] Usta ma'lumotlari to'g'riligini tekshirish
- [ ] Active/inactive statusni ko'rish

#### Buyurtmalar ro'yxati

- [ ] "📋 Buyurtmalar" tugmasini bosish
- [ ] Barcha buyurtmalarni ko'rish
- [ ] Buyurtma tafsilotlari to'g'riligini tekshirish

### 3. Database Testing

#### PostgreSQL orqali

```sql
-- Userlar mavjudligini tekshirish
SELECT * FROM users;

-- Buyurtmalar mavjudligini tekshirish
SELECT * FROM orders;

-- Ustalar va ularning xizmatlari
SELECT m.*, ms.service_id 
FROM masters m 
LEFT JOIN master_services ms ON m.id = ms.master_id;

-- Service va service_types
SELECT s.name, st.name 
FROM services s 
JOIN service_types st ON s.id = st.service_id;
```

### 4. Error Handling

#### Network errors

- [ ] Internet o'chirilgan holda xabar yuborish
- [ ] Database ulanishi yo'q holda operatsiya bajarish
- [ ] Telegram API timeout

#### Validation errors

- [ ] Bo'sh telefon raqam
- [ ] Noto'g'ri formatdagi telefon
- [ ] Mavjud bo'lmagan xizmat ID
- [ ] Bo'sh input fieldlar

#### User errors

- [ ] Noto'g'ri komanda yuborish
- [ ] Noto'g'ri callback data
- [ ] Noto'g'ri state'da xabar yuborish

### 5. Performance Testing

- [ ] 10 ta parallel buyurtma
- [ ] 50 ta parallel buyurtma
- [ ] 100 ta parallel buyurtma
- [ ] Database query tezligi
- [ ] Bot javob berish tezligi

### 6. Security Testing

- [ ] Admin funksiyalariga oddiy user kirisha olmasligini tekshirish
- [ ] SQL injection urinishi
- [ ] XSS urinishi (agar HTML ishlatilsa)
- [ ] Environment variables maxfiyligini tekshirish

## Automated Testing

### Unit Tests

```python
# test_repositories.py
import pytest
from repositories import user_repo

@pytest.mark.asyncio
async def test_create_user():
    user = await user_repo.create(
        telegram_id=123456789,
        username="test_user",
        first_name="Test"
    )
    assert user.telegram_id == 123456789
    assert user.username == "test_user"

@pytest.mark.asyncio
async def test_get_user():
    user = await user_repo.get_by_telegram_id(123456789)
    assert user is not None
```

### Integration Tests

```python
# test_order_flow.py
import pytest
from services import order_service

@pytest.mark.asyncio
async def test_create_order_with_master():
    order = await order_service.create_order(
        user_id=123456789,
        service_id=1,
        service_type_id=1,
        user_phone="+998901234567"
    )
    assert order.master_id is not None
```

### Load Testing

```bash
# Using locust or similar tools
# Create virtual users to simulate load
```

## Test Environment Setup

### 1. Create test database

```sql
CREATE DATABASE home_services_bot_test;
```

### 2. Run migrations

```bash
psql -U postgres -d home_services_bot_test -f schema.sql
```

### 3. Create test .env

```bash
cp .env .env.test
# Edit with test database credentials
```

### 4. Run tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

## Regression Testing

Before each release:

1. [ ] Run full manual test checklist
2. [ ] Run all automated tests
3. [ ] Check database integrity
4. [ ] Verify all error messages
5. [ ] Test with different user permissions
6. [ ] Test edge cases

## Bug Reporting Template

```markdown
**Bug Title**: Clear, descriptive title

**Environment**:
- OS: Ubuntu 22.04
- Python: 3.11
- Database: PostgreSQL 14

**Steps to Reproduce**:
1. Start bot
2. Send /start
3. Click "Buyurtma berish"
4. ...

**Expected Behavior**:
User should see service selection

**Actual Behavior**:
Error message appears

**Screenshots**:
[Attach if applicable]

**Logs**:
```
[Paste relevant logs]
```

**Priority**: High/Medium/Low
```

## Performance Benchmarks

Target metrics:

- Response time: < 1 second
- Database query time: < 100ms
- Maximum concurrent users: 1000+
- Uptime: 99.9%

## CI/CD Testing

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: test_db
          POSTGRES_PASSWORD: test_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      
      - name: Run tests
        run: pytest tests/
```
