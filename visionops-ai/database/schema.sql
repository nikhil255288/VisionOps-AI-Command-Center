CREATE TABLE stores (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cameras (
    id SERIAL PRIMARY KEY,
    store_id INT REFERENCES stores(id),
    camera_name VARCHAR(100),
    zone VARCHAR(100),
    stream_url TEXT
);

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    track_id INT,
    event_type VARCHAR(100),
    zone VARCHAR(100),
    severity VARCHAR(20),
    confidence FLOAT,
    camera_id INT REFERENCES cameras(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(100),
    message TEXT,
    severity VARCHAR(20),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analytics_snapshots (
    id SERIAL PRIMARY KEY,
    visitor_count INT,
    average_dwell_time FLOAT,
    queue_count INT,
    anomaly_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);