visitor_ids = set()

def count_visitors(track_ids):
    global visitor_ids

    if track_ids is None:
        return len(visitor_ids)

    for tid in track_ids:
        visitor_ids.add(int(tid))

    return len(visitor_ids)