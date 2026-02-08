import json
import random
import string

def generate_id(length: int = 8) -> str:
    """Generate random ID"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def safe_json_loads(data: str, default=None):
    """Safely load JSON"""
    try:
        return json.loads(data)
    except:
        return default

def format_time(seconds: int) -> str:
    """Format seconds to MM:SS"""
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"
