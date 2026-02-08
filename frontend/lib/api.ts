const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Add this function to frontend/lib/api.ts
export async function checkBackendHealth() {
  try {
    const response = await fetch('http://localhost:8000/', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    })
    return response.ok
  } catch (error) {
    console.error('Backend not reachable:', error)
    return false
  }
}

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
    throw new Error('Failed to generate video. Make sure backend is running on port 8000.')
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
