'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Download, Share2, Copy, Video, CheckCircle, RotateCcw } from 'lucide-react'

export default function DownloadPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const videoId = searchParams.get('videoId') || 'sample'
  
  const [copied, setCopied] = useState(false)
  const [videoUrl, setVideoUrl] = useState('')
  const [downloadUrl, setDownloadUrl] = useState('')

  useEffect(() => {
    if (videoId) {
      const url = `http://localhost:8000/api/videos/${videoId}`
      setVideoUrl(url)
      setDownloadUrl(url)
    }
  }, [videoId])

  const handleDownload = () => {
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = `ai-video-${videoId}.mp4`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'AI Generated Video',
          text: 'Check out this AI generated video!',
          url: window.location.href,
        })
      } catch (error) {
        console.log('Sharing cancelled')
      }
    } else {
      await navigator.clipboard.writeText(window.location.href)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleCreateAnother = () => {
    router.push('/create')
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold mb-4">Your Video is Ready!</h1>
          <p className="text-gray-400">Download your AI-generated video</p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Video Preview */}
          <div className="glass-effect rounded-2xl p-6">
            <div className="aspect-[9/16] bg-black rounded-xl overflow-hidden mb-4">
              {videoUrl ? (
                <video
                  src={videoUrl}
                  controls
                  className="w-full h-full object-cover"
                  poster="/video-poster.jpg"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <Video className="h-16 w-16 text-gray-600" />
                </div>
              )}
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex items-center">
                <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                <span>1080x1920 MP4</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                <span>No watermark</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                <span>HD quality</span>
              </div>
            </div>
          </div>

          {/* Download Options */}
          <div className="space-y-6">
            <div className="glass-effect rounded-2xl p-6">
              <h2 className="text-xl font-semibold mb-4">Download</h2>
              
              <button
                onClick={handleDownload}
                className="w-full py-4 px-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl text-lg font-semibold flex items-center justify-center hover:opacity-90 transition mb-4"
              >
                <Download className="h-5 w-5 mr-2" />
                Download MP4
              </button>
              
              <button
                onClick={handleShare}
                className="w-full py-4 px-6 glass-effect rounded-xl text-lg font-semibold flex items-center justify-center hover:bg-white/10 transition"
              >
                {copied ? (
                  <>
                    <Copy className="h-5 w-5 mr-2" />
                    Link Copied!
                  </>
                ) : (
                  <>
                    <Share2 className="h-5 w-5 mr-2" />
                    Share Video
                  </>
                )}
              </button>
            </div>

            <div className="glass-effect rounded-2xl p-6">
              <h2 className="text-xl font-semibold mb-4">Video Details</h2>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Video ID:</span>
                  <code className="bg-white/5 px-2 py-1 rounded">{videoId}</code>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Format:</span>
                  <span>MP4 (H.264)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Resolution:</span>
                  <span>1080x1920</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Duration:</span>
                  <span>~30 seconds</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Size:</span>
                  <span>~15 MB</span>
                </div>
              </div>
            </div>

            <button
              onClick={handleCreateAnother}
              className="w-full py-4 px-6 glass-effect rounded-xl text-lg font-semibold flex items-center justify-center hover:bg-white/10 transition"
            >
              <RotateCcw className="h-5 w-5 mr-2" />
              Create Another Video
            </button>

            <div className="text-center text-sm text-gray-400">
              <p>Videos are automatically deleted after 24 hours</p>
              <p>100% free - no limits</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
