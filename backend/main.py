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
    
    if task.get("video_id"):
        response["video_url"] = f"/api/videos/{task['video_id']}"
    
    return response

@app.get("/api/videos/{video_id}")
async def get_video(video_id: str):
    video_path = f"output/{video_id}.mp4"
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
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
async def process_video_task(task_id: str, request: VideoRequest):
    try:
        # Import services here to avoid circular imports
        from services.video_service import VideoService
        video_service = VideoService()
        
        # Update progress
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 10
        tasks[task_id]["message"] = "Processing script..."
        
        # Step 1: Process script into scenes
        scenes = video_service.process_script(request.script)
        
        tasks[task_id]["progress"] = 20
        tasks[task_id]["message"] = "Generating images..."
        
        # Step 2: Generate images
        image_paths = []
        for i, scene in enumerate(scenes[:5]):
            img_path = await video_service.generate_image(scene, request.style, i)
            image_paths.append(img_path)
            
            # Update progress
            progress = 20 + (i + 1) * 15
            tasks[task_id]["progress"] = min(progress, 50)
        
        tasks[task_id]["progress"] = 50
        tasks[task_id]["message"] = "Generating voiceover..."
        
        # Step 3: Generate voice
        audio_path = await video_service.generate_voice(request.script[:500], request.voice)
        
        tasks[task_id]["progress"] = 60
        tasks[task_id]["message"] = "Creating avatar..."
        
        # Step 4: Generate avatar video
        avatar_path = None
        if request.avatar != "none":
            avatar_path = await video_service.generate_avatar(request.avatar, audio_path)
        
        tasks[task_id]["progress"] = 70
        tasks[task_id]["message"] = "Composing video..."
        
        # Step 5: Create final video
        video_id = str(uuid.uuid4())
        video_path = await video_service.create_video(
            image_paths=image_paths,
            audio_path=audio_path,
            avatar_path=avatar_path,
            style=request.style,
            output_id=video_id
        )
        
        tasks[task_id]["progress"] = 100
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["message"] = "Video generated successfully!"
        tasks[task_id]["video_id"] = video_id
        
        # Clean up temp files
        video_service.cleanup_temp_files()
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["message"] = f"Error: {str(e)}"
        tasks[task_id]["error"] = str(e)
        print(f"Task {task_id} failed: {e}")

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
