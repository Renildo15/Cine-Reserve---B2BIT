def get_lock_key(session_id, seat_id):
    return f"lock:session:{session_id}:seat:{seat_id}"
