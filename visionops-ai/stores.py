# stores.py

events_db = []

def save_event(event):
    events_db.append(event)

def get_events():
    return events_db