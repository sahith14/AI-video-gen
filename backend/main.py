from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os
from datetime import datetime, timedelta
import shutil
import uuid
import asyncio

app = FastAPI(title="AI Video Generator API", version="1.0.0")

# Fix CORS - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
os.makedirs("output", exist_ok=True)
os.makedirs("temp", exist_ok=True)
app.mount("/output", StaticFiles(directory="output"), name="output")

# Models
class VideoRequest(BaseModel):
    script: str
    style: List[str] = ["cinematic"]
    avatar: str = "male"
    voice: str = "male"

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

# In-memory storage for tasks
tasks = {}

@app.get("/")
async def root():
    return {"message": "AI Video Generator API", "status": "running"}

# Add this function BEFORE the @app.post("/api/generate") route
async def process_video_task(task_id: str, request: VideoRequest):
    """MVP: Simple pipeline - Prompt → Image → Voice → Video"""
    try:
        # Try to import here to avoid circular imports
        from services.video_service import VideoService
        video_service = VideoService()
        
        tasks[task_id]["progress"] = 10
        tasks[task_id]["message"] = "Processing prompt..."
        tasks[task_id]["status"] = "processing"
        
        # MVP: Just use the whole prompt as one scene
        scene = request.script
        
        tasks[task_id]["progress"] = 30
        tasks[task_id]["message"] = "Creating image..."
        
        # Generate placeholder image
        image_path = await video_service.create_placeholder_image(
            prompt=scene,
            filename=f"scene_{task_id}"
        )
        
        tasks[task_id]["progress"] = 50
        tasks[task_id]["message"] = "Generating voice..."
        
        # Generate voice (limit to 100 chars for speed)
        text_for_voice = scene[:100] if len(scene) > 100 else scene
        audio_path = await video_service.generate_simple_voice(
            text=text_for_voice,
            voice_type=request.voice
        )
        
        tasks[task_id]["progress"] = 70
        tasks[task_id]["message"] = "Creating video..."
        
        # Create Ken Burns video
        video_id = f"video_{uuid.uuid4().hex[:8]}"
        final_path = await video_service.create_ken_burns_video(
            image_path=image_path,
            audio_path=audio_path,
            output_id=video_id
        )
        
        tasks[task_id]["progress"] = 100
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["message"] = "Video ready!"
        tasks[task_id]["video_id"] = video_id
        
        print(f"✅ Video generated: {final_path}")
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["message"] = f"Error: {str(e)}"
        print(f"❌ Task failed: {e}")
    
    # Add this after VideoRequest class
    class TaskResponse(BaseModel):
        task_id: str
        status: str
        message: str

@app.post("/api/generate", response_model=TaskResponse)
async def generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    
    # Validate input
    if not request.script.strip():
        raise HTTPException(status_code=400, detail="Script cannot be empty")
    
    if len(request.script) > 1000:
        raise HTTPException(status_code=400, detail="Script too long (max 1000 chars)")
    
    # Initialize task
    tasks[task_id] = {
        "status": "pending",
        "progress": 0,
        "message": "Starting video generation...",
        "created_at": datetime.now().isoformat(),
        "request": request.dict(),
        "video_id": None,
        "error": None
    }
    
    # Start background task
    background_tasks.add_task(process_video_task, task_id, request)
    
    return TaskResponse(
        task_id=task_id,
        status="started",
        message="Video generation started"
    )

@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    # Auto-cleanup old tasks
    created_at = datetime.fromisoformat(task["created_at"])
    if datetime.now() - created_at > timedelta(hours=1):
        del tasks[task_id]
        raise HTTPException(status_code=404, detail="Task expired")
    
    response = {
        "task_id": task_id,
        "status": task["status"],
        "progress": task["progress"],
        "message": task["message"],
        "video_id": task.get("video_id")
    }
    
    # Change this in get_status endpoint:
    if task.get("video_id"):
        response["video_url"] = f"/output/{task['video_id']}.mp4"  # Changed from /api/videos/
    
    return response

@app.get("/api/videos/{video_id}")
async def get_video(video_id: str):
    video_path = f"output/{video_id}.mp4"
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")

    return {
        "download_url": f"/output/{video_id}.mp4",
        "stream_url": f"/api/videos/{video_id}"
    }
    
    # Clean up old videos
    cleanup_old_videos()
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"ai-video-{video_id}.mp4"
    )

@app.get("/api/styles")
async def get_styles():
    styles = [
        {"id": "cinematic", "name": "Cinematic", "icon": "🎬", "description": "Movie-like quality"},
        {"id": "reels", "name": "Reels", "icon": "📱", "description": "Vertical video for social media"},
        {"id": "dark", "name": "Dark", "icon": "🌙", "description": "Dark theme with dramatic lighting"},
        {"id": "documentary", "name": "Documentary", "icon": "📹", "description": "Educational style"},
        {"id": "corporate", "name": "Corporate", "icon": "💼", "description": "Professional business style"},
        {"id": "animated", "name": "Animated", "icon": "✨", "description": "Animated graphics"}
    ]
    return styles

@app.get("/api/voices")
async def get_voices():
    voices = [
        {"id": "male", "name": "Male", "description": "Standard male voice"},
        {"id": "female", "name": "Female", "description": "Standard female voice"},
        {"id": "narrator", "name": "Narrator", "description": "Documentary narrator voice"}
    ]
    return voices

@app.get("/api/avatars")
async def get_avatars():
    avatars = [
        {"id": "male", "name": "Male", "emoji": "👨‍💼"},
        {"id": "female", "name": "Female", "emoji": "👩‍💼"},
        {"id": "ai", "name": "AI", "emoji": "🤖"},
        {"id": "none", "name": "No Avatar", "emoji": "🚫"}
    ]
    return avatars

# Background task
# Add this function (replace your existing process_video_task)
async def process_video_task(task_id: str, request: VideoRequest):
    """MVP: Simple pipeline - Prompt → Image → Voice → Video"""
    try:
        from services.video_service import VideoService
        video_service = VideoService()
        
        tasks[task_id]["progress"] = 10
        # Inside process_video_task, add this line after setting progress:
        tasks[task_id]["status"] = "processing"  # Add this line
        tasks[task_id]["message"] = "Processing prompt..."
        
        # MVP: Just use the whole prompt as one scene
        scene = request.script
        
        tasks[task_id]["progress"] = 30
        tasks[task_id]["message"] = "Creating image..."
        
        # Generate placeholder image
        image_path = await video_service.create_placeholder_image(
            prompt=scene,
            filename=f"scene_{task_id}"
        )
        
        tasks[task_id]["progress"] = 50
        tasks[task_id]["message"] = "Generating voice..."
        
        # Generate voice (limit to 100 chars for speed)
        text_for_voice = scene[:100] if len(scene) > 100 else scene
        audio_path = await video_service.generate_simple_voice(
            text=text_for_voice,
            voice_type=request.voice
        )
        
        tasks[task_id]["progress"] = 70
        tasks[task_id]["message"] = "Creating video..."
        
        # Create Ken Burns video
        video_id = f"video_{uuid.uuid4().hex[:8]}"
        final_path = await video_service.create_ken_burns_video(
            image_path=image_path,
            audio_path=audio_path,
            output_id=video_id
        )
        
        tasks[task_id]["progress"] = 100
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["message"] = "Video ready!"
        tasks[task_id]["video_id"] = video_id
        
        print(f"✅ Video generated: {final_path}")
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["message"] = f"Error: {str(e)}"
        print(f"❌ Task failed: {e}")


def cleanup_old_videos():
    """Clean up videos older than 24 hours"""
    now = datetime.now()
    for file in os.listdir("output"):
        if file.endswith(('.mp4', '.webm', '.mov', '.wav', '.jpg', '.png')):
            file_path = os.path.join("output", file)
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if now - file_time > timedelta(hours=24):
                try:
                    os.remove(file_path)
                except:
                    pass

# Cleanup on startup
cleanup_old_videos()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
