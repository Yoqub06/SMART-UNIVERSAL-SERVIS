-- Database Schema for Home Services Bot

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    phone_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Services table
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service types (sub-services)
CREATE TABLE IF NOT EXISTS service_types (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service_id, name)
);

-- Masters table
CREATE TABLE IF NOT EXISTS masters (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    telegram_username VARCHAR(255),
    telegram_id BIGINT,
    phone_number VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Master services (many-to-many relationship)
CREATE TABLE IF NOT EXISTS master_services (
    id SERIAL PRIMARY KEY,
    master_id INTEGER REFERENCES masters(id) ON DELETE CASCADE,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(master_id, service_id)
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_id) ON DELETE SET NULL,
    master_id INTEGER REFERENCES masters(id) ON DELETE SET NULL,
    service_id INTEGER REFERENCES services(id) ON DELETE SET NULL,
    service_type_id INTEGER REFERENCES service_types(id) ON DELETE SET NULL,
    user_phone VARCHAR(20) NOT NULL,
    location_latitude DECIMAL(10, 8),
    location_longitude DECIMAL(11, 8),
    location_address TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default services
INSERT INTO services (name) VALUES 
    ('Konditsioner'),
    ('Elektrika'),
    ('Santexnika'),
    ('Qurilish')
ON CONFLICT (name) DO NOTHING;

-- Insert service types
INSERT INTO service_types (service_id, name) 
SELECT id, 'Ustanovka' FROM services WHERE name = 'Konditsioner'
UNION ALL
SELECT id, 'Remont' FROM services WHERE name = 'Konditsioner'
UNION ALL
SELECT id, 'Montaj' FROM services WHERE name = 'Elektrika'
UNION ALL
SELECT id, 'Ustanovka' FROM services WHERE name = 'Elektrika'
UNION ALL
SELECT id, 'Remont' FROM services WHERE name = 'Elektrika'
UNION ALL
SELECT id, 'Montaj' FROM services WHERE name = 'Santexnika'
UNION ALL
SELECT id, 'Ustanovka' FROM services WHERE name = 'Santexnika'
UNION ALL
SELECT id, 'Remont' FROM services WHERE name = 'Santexnika'
UNION ALL
SELECT id, 'Dizayn' FROM services WHERE name = 'Qurilish'
UNION ALL
SELECT id, 'Loyiha' FROM services WHERE name = 'Qurilish'
UNION ALL
SELECT id, 'Proekt' FROM services WHERE name = 'Qurilish'
ON CONFLICT (service_id, name) DO NOTHING;

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_master_id ON orders(master_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_masters_active ON masters(is_active);
CREATE INDEX IF NOT EXISTS idx_master_services_master ON master_services(master_id);
CREATE INDEX IF NOT EXISTS idx_master_services_service ON master_services(service_id);

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_masters_updated_at BEFORE UPDATE ON masters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
