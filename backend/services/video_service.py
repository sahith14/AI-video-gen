import os
import random
import subprocess
import uuid
from typing import List, Optional
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests

class VideoService:
    def __init__(self):
        self.output_dir = "output"
        self.temp_dir = "temp"
        
        # Create directories
        for d in [self.output_dir, self.temp_dir]:
            os.makedirs(d, exist_ok=True)
        
        # Scene templates
        self.scene_templates = [
            "{scene} cinematic shot, 4K, professional photography, detailed",
            "{scene} dramatic lighting, epic composition, movie still",
            "{scene} dynamic angle, shallow depth of field, color graded",
            "{scene} professional cinematography, cinematic lighting, 8K"
        ]
        
        # Style modifiers
        self.style_modifiers = {
            "cinematic": "cinematic, movie scene, professional lighting",
            "reels": "vertical video, social media, trendy, modern",
            "dark": "dark theme, dramatic lighting, moody, contrast",
            "documentary": "documentary style, educational, informative",
            "corporate": "professional, business, clean, modern office",
            "animated": "animated graphics, motion design, colorful"
        }
    
    def process_script(self, script: str) -> List[str]:
        """Split script into visual scenes"""
        # Simple sentence splitting
        sentences = [s.strip() for s in script.replace('\n', ' ').split('.') if s.strip()]
        
        scenes = []
        for sentence in sentences[:5]:  # Max 5 scenes for demo
            # Convert sentence to visual prompt
            scene_prompt = self._sentence_to_scene(sentence)
            
            # Add random template
            template = random.choice(self.scene_templates)
            scene = template.format(scene=scene_prompt)
            
            scenes.append(scene)
        
        return scenes if scenes else ["professional scene, cinematic, 4K"]
    
    def _sentence_to_scene(self, sentence: str) -> str:
        """Convert text sentence to visual description"""
        sentence_lower = sentence.lower()
        
        # Keyword mapping
        keyword_map = {
            "work": "person working at desk with laptop",
            "hard": "determined person overcoming challenges",
            "success": "celebration scene with confetti",
            "learn": "person studying with books and tablet",
            "achieve": "person reaching goal, triumphant",
            "future": "futuristic technology, innovation",
            "team": "team collaborating in modern office",
            "growth": "plant growing, progress visualization",
            "technology": "advanced tech, digital interface",
            "business": "professional meeting in office",
            "motivation": "inspirational sunrise scene",
            "productivity": "organized workspace, efficiency",
            "leadership": "person leading team meeting",
            "innovation": "creative brainstorming session",
            "digital": "digital transformation visualization"
        }
        
        # Find matching keywords
        for keyword, visual in keyword_map.items():
            if keyword in sentence_lower:
                return visual
        
        # Default scene
        if len(sentence) > 50:
            return f"scene representing: {sentence[:50]}..."
        return "professional cinematic scene"
    
    async def generate_image(self, prompt: str, styles: List[str], scene_num: int) -> str:
        """Generate image from prompt"""
        # Create placeholder image
        image_path = await self._create_placeholder_image(prompt, scene_num)
        return image_path
    
    async def _create_placeholder_image(self, prompt: str, scene_num: int) -> str:
        """Create placeholder image with text"""
        # Create gradient background
        width, height = 1080, 1920
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        # Create gradient
        colors = [
            (20, 40, 100),   # Dark blue
            (40, 60, 150),   # Medium blue
            (60, 80, 200),   # Light blue
            (80, 100, 220),  # Very light blue
        ]
        
        for i in range(height):
            # Interpolate between colors
            color_idx = (i / height) * (len(colors) - 1)
            idx1 = int(color_idx)
            idx2 = min(idx1 + 1, len(colors) - 1)
            ratio = color_idx - idx1
            
            r = int(colors[idx1][0] * (1 - ratio) + colors[idx2][0] * ratio)
            g = int(colors[idx1][1] * (1 - ratio) + colors[idx2][1] * ratio)
            b = int(colors[idx1][2] * (1 - ratio) + colors[idx2][2] * ratio)
            
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        # Add text
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        text = prompt[:100] + "..." if len(prompt) > 100 else prompt
        lines = []
        words = text.split()
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] < width - 100:
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
            
            # Text shadow
            draw.text((x_text + 3, y_text + 3), line, font=font, fill=(0, 0, 0))
            draw.text((x_text, y_text), line, font=font, fill=(255, 255, 255))
            y_text += 70
        
        # Add scene number
        draw.text((50, 50), f"Scene {scene_num + 1}", font=font, fill=(255, 255, 255))
        
        # Save image
        image_path = f"{self.temp_dir}/scene_{scene_num}.jpg"
        image.save(image_path)
        
        return image_path
    
    async def generate_voice(self, text: str, voice_type: str) -> str:
        """Generate voiceover from text"""
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
            
            # Convert to WAV
            wav_path = output_path.replace('.mp3', '.wav')
            self._convert_audio(output_path, wav_path)
            
            return wav_path
        except:
            # Create dummy audio
            return await self._create_dummy_audio()
    
    def _convert_audio(self, input_path: str, output_path: str):
        """Convert audio format"""
        try:
            subprocess.run([
                'ffmpeg', '-y', '-i', input_path,
                '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000',
                output_path
            ], check=True, capture_output=True)
        except:
            import shutil
            shutil.copy(input_path, output_path)
    
    async def _create_dummy_audio(self) -> str:
        """Create dummy audio"""
        import wave
        import struct
        import numpy as np
        
        sample_rate = 16000
        duration = 3
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = np.sin(2 * np.pi * 220 * t)
        audio = (audio * 32767).astype(np.int16)
        
        output_path = f"{self.temp_dir}/dummy_audio.wav"
        
        with wave.open(output_path, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            for sample in audio:
                data = struct.pack('<h', sample)
                wav_file.writeframes(data)
        
        return output_path
    
    async def generate_avatar(self, avatar_type: str, audio_path: str) -> str:
        """Generate talking avatar video"""
        return await self._create_animated_avatar(avatar_type, audio_path)
    
    async def _create_animated_avatar(self, avatar_type: str, audio_path: str) -> str:
        """Create animated avatar"""
        import cv2
        import numpy as np
        
        # Avatar colors
        avatar_colors = {
            "male": (255, 200, 150),
            "female": (255, 200, 220),
            "ai": (100, 200, 255)
        }
        
        color = avatar_colors.get(avatar_type, (200, 200, 200))
        size = 400
        
        # Get audio duration
        duration = 5
        try:
            import wave
            with wave.open(audio_path, 'r') as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                duration = frames / float(rate)
        except:
            pass
        
        # Create video
        fps = 30
        total_frames = int(duration * fps)
        output_path = f"{self.temp_dir}/avatar_{avatar_type}.mp4"
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (size, size))
        
        for frame in range(total_frames):
            # Create frame
            img = np.ones((size, size, 3), dtype=np.uint8) * 255
            
            # Draw face
            cv2.circle(img, (size//2, size//2), 150, color, -1)
            
            # Draw eyes
            cv2.circle(img, (size//2 - 50, size//2 - 30), 30, (255, 255, 255), -1)
            cv2.circle(img, (size//2 + 50, size//2 - 30), 30, (255, 255, 255), -1)
            cv2.circle(img, (size//2 - 50, size//2 - 30), 15, (0, 0, 0), -1)
            cv2.circle(img, (size//2 + 50, size//2 - 30), 15, (0, 0, 0), -1)
            
            # Animate mouth
            mouth_open = np.sin(frame * 0.5) * 0.5 + 0.5
            mouth_height = int(20 + mouth_open * 40)
            cv2.ellipse(img, 
                       (size//2, size//2 + 50),
                       (50, mouth_height//2),
                       0, 0, 360, (0, 0, 0), -1)
            
            out.write(img)
        
        out.release()
        
        return output_path
    
    async def create_video(self, image_paths: List[str], audio_path: str, 
                          avatar_path: Optional[str], style: List[str], output_id: str) -> str:
        """Create final video"""
        
        if not image_paths:
            # Create placeholder
            image_paths = [await self._create_placeholder_image("Video Scene", 0)]
        
        # Create slideshow
        slideshow_path = self._create_slideshow(image_paths, style)
        
        # Add audio
        video_with_audio = self._add_audio(slideshow_path, audio_path)
        
        # Add avatar if exists
        if avatar_path:
            final_video = self._add_avatar_overlay(video_with_audio, avatar_path)
        else:
            final_video = video_with_audio
        
        # Save final video
        output_path = f"{self.output_dir}/{output_id}.mp4"
        self._finalize_video(final_video, output_path)
        
        return output_path
    
    def _create_slideshow(self, image_paths: List[str], style: List[str]) -> str:
        """Create slideshow from images"""
        output_path = f"{self.temp_dir}/slideshow.mp4"
        
        # Create input file
        input_file = f"{self.temp_dir}/input.txt"
        with open(input_file, 'w') as f:
            for img_path in image_paths:
                f.write(f"file '{os.path.abspath(img_path)}'\n")
                f.write(f"duration 3\n")
        
        # FFmpeg command
        filter_complex = "scale=1080:1920"
        
        if "cinematic" in style:
            filter_complex += ",zoompan=z='zoom+0.002':d=90:s=1080x1920"
        elif "reels" in style:
            filter_complex += ",crop=1080:1920,zoompan=z='zoom+0.003':d=90"
        else:
            filter_complex += ",zoompan=z='zoom+0.0015':d=90:s=1080x1920"
        
        filter_complex += ",fade=t=in:st=0:d=0.5,fade=t=out:st=2.5:d=0.5"
        
        cmd = [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', input_file,
            '-vf', filter_complex,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-pix_fmt', 'yuv420p',
            '-r', '30',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except:
            self._create_fallback_slideshow(image_paths, output_path)
        
        return output_path
    
    def _create_fallback_slideshow(self, image_paths: List[str], output_path: str):
        """Fallback slideshow"""
        import cv2
        import numpy as np
        
        height, width = 1920, 1080
        fps = 30
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        for img_path in image_paths:
            img = cv2.imread(img_path)
            if img is None:
                img = np.zeros((height, width, 3), dtype=np.uint8)
                img[:] = [random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)]
            
            img_resized = cv2.resize(img, (width, height))
            
            # Write 3 seconds of frames
            for _ in range(3 * fps):
                out.write(img_resized)
        
        out.release()
    
    def _add_audio(self, video_path: str, audio_path: str) -> str:
        """Add audio to video"""
        output_path = f"{self.temp_dir}/with_audio.mp4"
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except:
            import shutil
            shutil.copy(video_path, output_path)
        
        return output_path
    
    def _add_avatar_overlay(self, video_path: str, avatar_path: str) -> str:
        """Overlay avatar on video"""
        output_path = f"{self.temp_dir}/with_avatar.mp4"
        
        # Resize avatar
        resized_avatar = f"{self.temp_dir}/avatar_resized.mp4"
        resize_cmd = [
            'ffmpeg', '-y',
            '-i', avatar_path,
            '-vf', 'scale=300:300',
            '-c:a', 'copy',
            resized_avatar
        ]
        
        try:
            subprocess.run(resize_cmd, check=True, capture_output=True)
            
            # Overlay
            overlay_cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', resized_avatar,
                '-filter_complex', '[0][1]overlay=(W-w)/2:H-h-100',
                '-c:a', 'copy',
                output_path
            ]
            
            subprocess.run(overlay_cmd, check=True, capture_output=True)
        except:
            import shutil
            shutil.copy(video_path, output_path)
        
        return output_path
    
    def _finalize_video(self, video_path: str, output_path: str):
        """Final video processing"""
        import shutil
        shutil.copy(video_path, output_path)
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            os.makedirs(self.temp_dir)
