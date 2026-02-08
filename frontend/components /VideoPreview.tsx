'use client'

interface VideoPreviewProps {
  src?: string
  isLoading?: boolean
}

export default function VideoPreview({ src, isLoading = false }: VideoPreviewProps) {
  if (isLoading) {
    return (
      <div className="aspect-[9/16] bg-gray-900 rounded-xl flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="aspect-[9/16] bg-black rounded-xl overflow-hidden">
      {src ? (
        <video
          src={src}
          controls
          className="w-full h-full object-cover"
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center text-gray-500">
          Video preview will appear here
        </div>
      )}
    </div>
  )
}
