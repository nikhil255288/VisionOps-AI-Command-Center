import os, random
import psycopg2
from datetime import datetime, timedelta

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("""
INSERT INTO sessions(video_name)
VALUES ('road_traffic_demo.mp4')
RETURNING id
""")
session_id = cur.fetchone()[0]

# events
for i in range(8):
    cur.execute("""
    INSERT INTO events(event_type, zone, severity, confidence, session_id)
    VALUES (%s, %s, %s, %s, %s)
    """, ("footfall_spike", "store", "medium", 0.92, session_id))

# tracking points
base_time = datetime.now()
for track_id in range(1, 22):
    x = random.randint(10, 600)
    y = random.randint(200, 270)

    for step in range(random.randint(8, 25)):
        cur.execute("""
        INSERT INTO tracking_points(session_id, track_id, x, y, timestamp)
        VALUES (%s, %s, %s, %s, %s)
        """, (
            session_id,
            track_id,
            x + random.randint(-20, 20) + step * random.uniform(0.5, 3),
            y + random.randint(-8, 8),
            base_time + timedelta(seconds=step)
        ))

conn.commit()
cur.close()
conn.close()

print("✅ Demo analytics inserted successfully")