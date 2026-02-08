import subprocess
import os

class FFmpegService:
    @staticmethod
    def check_ffmpeg():
        """Check if FFmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    @staticmethod
    def get_video_duration(video_path: str) -> float:
        """Get video duration in seconds"""
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'error', '-show_entries',
                'format=duration', '-of',
                'default=noprint_wrappers=1:nokey=1', video_path
            ], capture_output=True, text=True, check=True)
            
            return float(result.stdout.strip())
        except:
            return 0
    
    @staticmethod
    def compress_video(input_path: str, output_path: str, target_size_mb: int = 10):
        """Compress video to target size"""
        # Get current duration
        duration = FFmpegService.get_video_duration(input_path)
        
        if duration == 0:
            return False
        
        # Calculate target bitrate
        target_bitrate = (target_size_mb * 8192) / duration
        
        cmd = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx265',
            '-crf', '28',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-y', output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except:
            return False
