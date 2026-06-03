CREATE TABLE IF NOT EXISTS spirit_applications (
    id SERIAL PRIMARY KEY,
    nickname VARCHAR(64) NOT NULL,
    email VARCHAR(256) NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);