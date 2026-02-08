const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface VideoRequest {
  script: string
  style: string[]
  avatar: string
  voice: string
}

export interface TaskResponse {
  task_id: string
  status: string
  message: string
}

export async function generateVideo(request: VideoRequest): Promise<TaskResponse> {
  const response = await fetch(`${API_BASE}/api/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })
  
  if (!response.ok) {
    throw new Error('Failed to generate video')
  }
  
  return response.json()
}

export async function getTaskStatus(taskId: string) {
  const response = await fetch(`${API_BASE}/api/status/${taskId}`)
  
  if (!response.ok) {
    throw new Error('Failed to get task status')
  }
  
  return response.json()
}

export function getVideoUrl(videoId: string): string {
  return `${API_BASE}/api/videos/${videoId}`
}
