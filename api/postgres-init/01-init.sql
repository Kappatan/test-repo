-- Создать пользователя app
CREATE USER app WITH PASSWORD 'app';

-- Создать базу данных recruitment
CREATE DATABASE recruitment OWNER app;

-- Подключиться к базе recruitment
\c recruitment

-- Дать все права пользователю app на схему public
GRANT ALL ON SCHEMA public TO app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app;
ALTER SCHEMA public OWNER TO app;

-- Сообщение об успехе
DO $$ BEGIN
    RAISE NOTICE 'Database recruitment and user app created successfully';
END $$;

