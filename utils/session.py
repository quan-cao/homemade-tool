import string, random

def generate_session_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))