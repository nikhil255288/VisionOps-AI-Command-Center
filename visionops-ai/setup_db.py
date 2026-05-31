import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL not found")

SCHEMA = """
CREATE TABLE IF NOT EXISTS stores (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cameras (
    id SERIAL PRIMARY KEY,
    store_id INT REFERENCES stores(id),
    camera_name VARCHAR(100),
    zone VARCHAR(100),
    stream_url TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    video_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    track_id INT,
    event_type VARCHAR(100),
    zone VARCHAR(100),
    severity VARCHAR(20),
    confidence FLOAT,
    camera_id INT REFERENCES cameras(id),
    session_id INT REFERENCES sessions(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tracking_points (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    track_id INT,
    x FLOAT,
    y FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(100),
    message TEXT,
    severity VARCHAR(20),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics_snapshots (
    id SERIAL PRIMARY KEY,
    visitor_count INT,
    average_dwell_time FLOAT,
    queue_count INT,
    anomaly_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
cur.execute(SCHEMA)
conn.commit()
cur.close()
conn.close()

print("✅ Database tables created successfully")