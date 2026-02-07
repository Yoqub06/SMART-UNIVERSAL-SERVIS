#!/bin/bash

# Development setup script

echo "🔧 Setting up development environment..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your credentials"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✅ Development environment is ready!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Create PostgreSQL database and import schema.sql"
echo "3. Run: python main.py"
