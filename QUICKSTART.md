# QUICKSTART (Windows)

## 1) Virtual environment
```powershell
python -m venv venv
venv\Scripts\activate
```

## 2) Dependencies
```powershell
pip install -r requirements.txt
```

## 3) PostgreSQL
```sql
CREATE DATABASE home_services_bot;
```

## 4) Schema
```powershell
psql -U postgres -d home_services_bot -f schema.sql
```

## 5) .env
```env
BOT_TOKEN=your_bot_token
ADMIN_IDS=123456789
DB_HOST=localhost
DB_PORT=5432
DB_NAME=home_services_bot
DB_USER=postgres
DB_PASSWORD=your_password
```

## 6) Run
```powershell
python main.py
```
