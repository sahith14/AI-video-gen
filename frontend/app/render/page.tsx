'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Loader2, CheckCircle, Image, Volume2, Film, Download } from 'lucide-react'

export default function RenderPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const taskId = searchParams.get('taskId')
  
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState('Starting video generation...')
  const [step, setStep] = useState(0)
  const [videoId, setVideoId] = useState('')

  const steps = [
    { icon: <Image />, label: 'Processing script', desc: 'Analyzing your text' },
    { icon: <Image />, label: 'Generating images', desc: 'Creating visuals' },
    { icon: <Volume2 />, label: 'Creating voiceover', desc: 'Generating audio' },
    { icon: <Film />, label: 'Rendering video', desc: 'Final composition' },
    { icon: <CheckCircle />, label: 'Complete', desc: 'Ready to download' },
  ]

  useEffect(() => {
    if (!taskId) {
      router.push('/create')
      return
    }

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/status/${taskId}`)
        const data = await response.json()
        
        setProgress(data.progress || 0)
        setStatus(data.message || 'Processing...')
        
        if (data.video_id) {
          setVideoId(data.video_id)
        }
        
        // Update step based on progress
        if (data.progress < 20) setStep(0)
        else if (data.progress < 40) setStep(1)
        else if (data.progress < 60) setStep(2)
        else if (data.progress < 80) setStep(3)
        else setStep(4)
        
        if (data.status === 'completed' || data.progress === 100) {
          clearInterval(interval)
          setTimeout(() => {
            router.push(`/download?videoId=${data.video_id}`)
          }, 1500)
        }
        
        if (data.status === 'failed') {
          clearInterval(interval)
          alert('Video generation failed. Please try again.')
          router.push('/create')
        }
      } catch (error) {
        console.error('Error checking status:', error)
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [taskId, router])

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="glass-effect rounded-2xl p-8 max-w-2xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Creating Your Video</h1>
          <p className="text-gray-400">This may take 1-2 minutes</p>
        </div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            <span className="text-lg">{status}</span>
            <span className="text-lg font-semibold">{progress}%</span>
          </div>
          <div className="h-3 bg-white/10 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Steps */}
        <div className="space-y-4 mb-8">
          {steps.map((s, idx) => (
            <div 
              key={idx} 
              className={`flex items-center p-4 rounded-xl transition-all ${
                idx === step 
                  ? 'bg-blue-500/20 border border-blue-500/50' 
                  : idx < step 
                    ? 'bg-green-500/10 border border-green-500/30' 
                    : 'bg-white/5'
              }`}
            >
              <div className={`p-2 rounded-lg mr-4 ${
                idx === step 
                  ? 'bg-blue-500' 
                  : idx < step 
                    ? 'bg-green-500' 
                    : 'bg-white/10'
              }`}>
                {s.icon}
              </div>
              <div className="flex-1">
                <div className="font-semibold">{s.label}</div>
                <div className="text-sm text-gray-400">{s.desc}</div>
              </div>
              {idx < step ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : idx === step ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : null}
            </div>
          ))}
        </div>

        {/* Info */}
        <div className="text-center text-sm text-gray-400">
          <p className="mb-2">Don't close this page. Your video is being generated.</p>
          <p>Task ID: <code className="bg-white/5 px-2 py-1 rounded">{taskId}</code></p>
        </div>

        {videoId && (
          <div className="mt-6 text-center">
            <button
              onClick={() => router.push(`/download?videoId=${videoId}`)}
              className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl font-semibold hover:opacity-90 transition"
            >
              <Download className="h-4 w-4 mr-2" />
              Go to Download
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
