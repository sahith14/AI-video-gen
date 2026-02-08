import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path

def ensure_directory(path: str):
    """Ensure directory exists"""
    Path(path).mkdir(parents=True, exist_ok=True)

def generate_filename(prefix: str = "video", extension: str = "mp4") -> str:
    """Generate unique filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{unique_id}.{extension}"

def cleanup_old_files(directory: str, max_age_hours: int = 24):
    """Clean up files older than specified hours"""
    now = datetime.now()
    
    for filepath in Path(directory).glob("*"):
        if filepath.is_file():
            file_time = datetime.fromtimestamp(filepath.stat().st_mtime)
            age_hours = (now - file_time).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                try:
                    filepath.unlink()
                except Exception as e:
                    print(f"Error deleting {filepath}: {e}")

def get_file_size_mb(filepath: str) -> float:
    """Get file size in MB"""
    if not os.path.exists(filepath):
        return 0
    return os.path.getsize(filepath) / (1024 * 1024)

def is_video_file(filepath: str) -> bool:
    """Check if file is a video"""
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv'}
    return Path(filepath).suffix.lower() in video_extensions
