'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Mic, Video, User, Palette, Sparkles, AlertCircle } from 'lucide-react'
import PromptInput from '@/components/PromptInput'
import StyleSelector from '@/components/StyleSelector'
import { checkBackendHealth } from '@/api'

export default function CreatePage() {
  const router = useRouter()
  const [script, setScript] = useState('')
  const [style, setStyle] = useState(['cinematic'])
  const [avatar, setAvatar] = useState('male')
  const [voice, setVoice] = useState('male')
  const [isLoading, setIsLoading] = useState(false)
  const [backendConnected, setBackendConnected] = useState(true)

  // Check backend connection on mount
  useEffect(() => {
    async function checkConnection() {
      const isConnected = await checkBackendHealth()
      setBackendConnected(isConnected)
      
      if (!isConnected) {
        console.error('Backend not connected. Please run: cd backend && python main.py')
      }
    }
    checkConnection()
  }, [])

  const exampleScripts = [
    "Welcome to our productivity masterclass. Today we'll learn how to achieve more in less time through focused work and smart planning.",
    "Hard work beats talent when talent doesn't work hard. Every morning is a new opportunity to improve and get closer to your dreams.",
    "The future of AI is here. Discover how artificial intelligence is transforming industries and creating new opportunities worldwide."
  ]

  const handleGenerate = async () => {
    if (!script.trim()) {
      alert('Please enter a script!')
      return
    }

    setIsLoading(true)
    
    try {
      const response = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ script, style, avatar, voice })
      })

      const data = await response.json()
      
      if (data.task_id) {
        router.push(`/render?taskId=${data.task_id}`)
      } else {
        throw new Error('No task ID received')
      }
    } catch (error) {
      console.error('Error:', error)
      alert('Failed to start generation. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  // Add this before the return statement:
  if (!backendConnected) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="glass-effect rounded-2xl p-8 max-w-md">
          <div className="flex items-center mb-4 text-red-400">
            <AlertCircle className="h-8 w-8 mr-2" />
            <h1 className="text-2xl font-bold">Backend Not Connected</h1>
          </div>
          
          <p className="text-gray-300 mb-4">
            The AI video generation backend is not running.
          </p>
          
          <div className="space-y-3 text-sm text-gray-400">
            <p>Please open a terminal and run:</p>
            <code className="block p-3 bg-gray-800 rounded-lg">
              cd backend<br />
              python main.py
            </code>
            <p>Then refresh this page.</p>
          </div>
          
          <button
            onClick={() => window.location.reload()}
            className="mt-6 w-full py-3 bg-blue-500 hover:bg-blue-600 rounded-lg font-semibold"
          >
            Refresh Page
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold mb-4">Create Your AI Video</h1>
          <p className="text-gray-400">Enter your script and customize the video style</p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Left Column */}
          <div className="space-y-6">
            {/* Script Input */}
            <div className="glass-effect rounded-2xl p-6">
              <div className="flex items-center mb-4">
                <Mic className="h-5 w-5 mr-2" />
                <h2 className="text-xl font-semibold">Script</h2>
              </div>
              
              <PromptInput
                value={script}
                onChange={setScript}
                placeholder="Enter your script here... Example: 'Welcome to our productivity masterclass...'"
              />
              
              <div className="mt-4 text-sm text-gray-500">
                Characters: {script.length}/1000
              </div>

              {/* Example Scripts */}
              <div className="mt-6">
                <p className="text-sm text-gray-400 mb-2">Try these examples:</p>
                <div className="space-y-2">
                  {exampleScripts.map((text, idx) => (
                    <button
                      key={idx}
                      onClick={() => setScript(text)}
                      className="w-full text-left p-3 text-sm bg-white/5 rounded-lg hover:bg-white/10 transition"
                    >
                      {text.substring(0, 80)}...
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Voice Settings */}
            <div className="glass-effect rounded-2xl p-6">
              <div className="flex items-center mb-4">
                <Mic className="h-5 w-5 mr-2" />
                <h2 className="text-xl font-semibold">Voice</h2>
              </div>
              
              <div className="grid grid-cols-3 gap-3">
                {[
                  { id: 'male', label: 'Male', emoji: '👨' },
                  { id: 'female', label: 'Female', emoji: '👩' },
                  { id: 'narrator', label: 'Narrator', emoji: '🎙️' },
                ].map((v) => (
                  <button
                    key={v.id}
                    onClick={() => setVoice(v.id)}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      voice === v.id 
                        ? 'border-blue-500 bg-blue-500/20' 
                        : 'border-white/10 bg-white/5 hover:bg-white/10'
                    }`}
                  >
                    <div className="text-2xl mb-2">{v.emoji}</div>
                    <div className="text-sm">{v.label}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Style Selector */}
            <div className="glass-effect rounded-2xl p-6">
              <div className="flex items-center mb-4">
                <Palette className="h-5 w-5 mr-2" />
                <h2 className="text-xl font-semibold">Style</h2>
              </div>
              
              <StyleSelector
                selected={style}
                onChange={setStyle}
                styles={[
                  { id: 'cinematic', label: 'Cinematic', icon: '🎬' },
                  { id: 'reels', label: 'Reels', icon: '📱' },
                  { id: 'dark', label: 'Dark', icon: '🌙' },
                  { id: 'documentary', label: 'Documentary', icon: '📹' },
                  { id: 'corporate', label: 'Corporate', icon: '💼' },
                  { id: 'animated', label: 'Animated', icon: '✨' },
                ]}
              />
            </div>

            {/* Avatar Selector */}
            <div className="glass-effect rounded-2xl p-6">
              <div className="flex items-center mb-4">
                <User className="h-5 w-5 mr-2" />
                <h2 className="text-xl font-semibold">Avatar</h2>
              </div>
              
              <div className="grid grid-cols-4 gap-3">
                {[
                  { id: 'male', label: 'Male', emoji: '👨‍💼' },
                  { id: 'female', label: 'Female', emoji: '👩‍💼' },
                  { id: 'ai', label: 'AI', emoji: '🤖' },
                  { id: 'none', label: 'None', emoji: '🚫' },
                ].map((av) => (
                  <button
                    key={av.id}
                    onClick={() => setAvatar(av.id)}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      avatar === av.id 
                        ? 'border-blue-500 bg-blue-500/20' 
                        : 'border-white/10 bg-white/5 hover:bg-white/10'
                    }`}
                  >
                    <div className="text-2xl mb-2">{av.emoji}</div>
                    <div className="text-sm">{av.label}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Generate Button */}
            <div className="glass-effect rounded-2xl p-6">
              <button
                onClick={handleGenerate}
                disabled={isLoading || !script.trim()}
                className="w-full py-4 px-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl text-lg font-semibold flex items-center justify-center hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-white mr-2"></div>
                    Starting...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5 mr-2" />
                    Generate Video (Free)
                  </>
                )}
              </button>
              
              <div className="mt-4 text-sm text-gray-500 space-y-1">
                <p className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  100% free - no credit card required
                </p>
                <p className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Max 60 seconds per video
                </p>
                <p className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  HD 1080x1920 MP4 output
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
