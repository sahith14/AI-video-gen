import os
import subprocess
import asyncio
import uuid
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from services.ffmpeg_service import animate_single_image

clips = []

for i, img in enumerate(images):
    clip = f"temp_clip_{i}.mp4"
    animate_single_image(img, clip)
    clips.append(clip)

class VideoService:
    def __init__(self):
        self.output_dir = "output"
        self.temp_dir = "temp"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def create_placeholder_image(self, prompt: str, filename: str) -> str:
        """Create simple image with text"""
        width, height = 1080, 1920
        
        # Create gradient background
        img = Image.new('RGB', (width, height), color='black')
        draw = ImageDraw.Draw(img)
        
        # Add gradient
        for i in range(height):
            r = int(20 + (i / height) * 50)
            g = int(40 + (i / height) * 60)
            b = int(100 + (i / height) * 100)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        # Add text
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        # Wrap text
        lines = []
        words = prompt.split()
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] < width - 100:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # Draw text
        y_text = height // 2 - (len(lines) * 70) // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x_text = (width - text_width) // 2
            
            # Shadow
            draw.text((x_text+2, y_text+2), line, font=font, fill=(0, 0, 0))
            # Main text
            draw.text((x_text, y_text), line, font=font, fill=(255, 255, 255))
            y_text += 70
        
        # Save
        image_path = f"{self.temp_dir}/{filename}.jpg"
        img.save(image_path)
        return image_path
    
    async def generate_simple_voice(self, text: str, voice_type: str = "male") -> str:
        """Generate voice using edge-tts or fallback"""
        try:
            import edge_tts
            voice_map = {
                "male": "en-US-ChristopherNeural",
                "female": "en-US-JennyNeural",
                "narrator": "en-GB-RyanNeural"
            }
            
            voice = voice_map.get(voice_type, "en-US-ChristopherNeural")
            output_path = f"{self.temp_dir}/voice_{uuid.uuid4().hex[:8]}.mp3"
            
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            
            # Convert to WAV for FFmpeg
            wav_path = output_path.replace('.mp3', '.wav')
            self._convert_audio(output_path, wav_path)
            return wav_path
            
        except ImportError:
            # Fallback: create silent audio
            return await self._create_silent_audio()
    
    def _convert_audio(self, input_path: str, output_path: str):
        """Convert audio format"""
        subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000',
            output_path
        ], capture_output=True)
    
    async def _create_silent_audio(self) -> str:
        """Create silent audio as fallback"""
        output_path = f"{self.temp_dir}/silent.wav"
        # Create 10 seconds of silence
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
            '-t', '10', output_path
        ], capture_output=True)
        return output_path
    
    async def create_ken_burns_video(self, image_path: str, audio_path: str, output_id: str) -> str:
        """Create video with Ken Burns effect"""
        output_path = f"{self.output_dir}/{output_id}.mp4"
        
        # Get audio duration
        duration = 10
        try:
            import subprocess
            result = subprocess.run([
                'ffprobe', '-v', 'error', '-show_entries', 
                'format=duration', '-of', 
                'default=noprint_wrappers=1:nokey=1', audio_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                duration = float(result.stdout.strip())
        except:
            pass
        
        # FFmpeg command
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', image_path,
            '-i', audio_path,
            '-vf', f"scale=1080:1920,zoompan=z='zoom+0.0015':d={int(duration*30)}:s=1080x1920",
            '-t', str(duration),
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-shortest',
            '-pix_fmt', 'yuv420p',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ Video created: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg failed: {e.stderr}")
            # Fallback: simple conversion
            self._create_fallback_video(image_path, audio_path, output_path)
            return output_path
    
    def _create_fallback_video(self, image_path: str, audio_path: str, output_path: str):
        """Simple fallback video"""
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', image_path,
            '-i', audio_path,
            '-t', '10',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-shortest',
            output_path
        ]
        subprocess.run(cmd, capture_output=True)
