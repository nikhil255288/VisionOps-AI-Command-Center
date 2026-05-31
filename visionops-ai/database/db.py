import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5433,
    "database": "visionops_db",
    "user": "visionops",
    "password": "visionops",
}

def get_connection():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return psycopg2.connect(**DB_CONFIG)


def create_session(video_name):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sessions(video_name)
                VALUES (%s)
                RETURNING id
                """,
                (video_name,)
            )
            return cursor.fetchone()[0]


def save_event(event, session_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO events(event_type, zone, severity, confidence, session_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    event["event_type"],
                    event["zone"],
                    event["severity"],
                    event.get("confidence", 1.0),
                    session_id,
                )
            )

def get_alerts():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, alert_type, message, severity, status, created_at
                FROM alerts
                ORDER BY created_at DESC
                """
            )
            return cursor.fetchall()

def get_session_summary():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT
                    s.id AS session_id,
                    s.video_name,
                    s.created_at,
                    COUNT(DISTINCT tp.track_id) AS unique_visitors,
                    COUNT(DISTINCT e.id) AS total_events,
                    COALESCE(ROUND(AVG(d.dwell_seconds)::numeric, 2), 0) AS avg_dwell_seconds,
                    COALESCE(ROUND(MAX(d.dwell_seconds)::numeric, 2), 0) AS max_dwell_seconds
                FROM sessions s
                LEFT JOIN events e ON e.session_id = s.id
                LEFT JOIN tracking_points tp ON tp.session_id = s.id
                LEFT JOIN (
                    SELECT
                        session_id,
                        track_id,
                        EXTRACT(EPOCH FROM (MAX(timestamp) - MIN(timestamp))) AS dwell_seconds
                    FROM tracking_points
                    GROUP BY session_id, track_id
                ) d ON d.session_id = s.id
                GROUP BY s.id, s.video_name, s.created_at
                ORDER BY s.created_at DESC
                """
            )
            return cursor.fetchall()


def save_analytics_snapshot(visitors, queue_count, anomaly_count):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO analytics_snapshots(
                    visitor_count,
                    average_dwell_time,
                    queue_count,
                    anomaly_count
                )
                VALUES (%s, %s, %s, %s)
                """,
                (visitors, 0, queue_count, anomaly_count)
            )


def save_alert(alert_type, message, severity):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO alerts(alert_type, message, severity, status)
                VALUES (%s, %s, %s, %s)
                """,
                (alert_type, message, severity, "OPEN")
            )


def get_sessions():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, video_name, created_at
                FROM sessions
                ORDER BY created_at DESC
                """
            )
            return cursor.fetchall()
        
def save_tracking_point(session_id, track_id, x, y):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tracking_points(session_id, track_id, x, y)
                VALUES (%s, %s, %s, %s)
                """,
                (session_id, int(track_id), float(x), float(y))
            )


def get_tracking_points(session_id=None):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if session_id is not None:
                cursor.execute(
                    """
                    SELECT session_id, track_id, x, y, timestamp
                    FROM tracking_points
                    WHERE session_id = %s
                    ORDER BY timestamp DESC
                    """,
                    (session_id,)
                )
            else:
                cursor.execute(
                    """
                    SELECT session_id, track_id, x, y, timestamp
                    FROM tracking_points
                    ORDER BY timestamp DESC
                    """
                )

            return cursor.fetchall()
        
def get_dwell_times(session_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT
                    track_id,
                    MIN(timestamp) AS entry_time,
                    MAX(timestamp) AS exit_time,
                    EXTRACT(EPOCH FROM (MAX(timestamp) - MIN(timestamp))) AS dwell_seconds
                FROM tracking_points
                WHERE session_id = %s
                GROUP BY track_id
                ORDER BY dwell_seconds DESC
                """,
                (session_id,)
            )
            return cursor.fetchall()


def get_events(session_id=None):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if session_id is not None:
                cursor.execute(
                    """
                    SELECT 
                        e.id,
                        e.event_type,
                        e.zone,
                        e.severity,
                        e.confidence,
                        e.session_id,
                        s.video_name,
                        e.timestamp
                    FROM events e
                    LEFT JOIN sessions s ON e.session_id = s.id
                    WHERE e.session_id = %s
                    ORDER BY e.timestamp DESC
                    """,
                    (session_id,)
                )
            else:
                cursor.execute(
                    """
                    SELECT 
                        e.id,
                        e.event_type,
                        e.zone,
                        e.severity,
                        e.confidence,
                        e.session_id,
                        s.video_name,
                        e.timestamp
                    FROM events e
                    LEFT JOIN sessions s ON e.session_id = s.id
                    ORDER BY e.timestamp DESC
                    """
                )

            return cursor.fetchall()


if __name__ == "__main__":
    conn = get_connection()
    conn.close()
    print("Connected successfully!")