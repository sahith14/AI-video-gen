import { Video, Sparkles } from 'lucide-react'
import Link from 'next/link'

export default function Navbar() {
  return (
    <nav className="border-b border-white/10">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link href="/" className="flex items-center space-x-2">
          <Video className="h-8 w-8 text-blue-400" />
          <span className="text-xl font-bold">AI Video Gen</span>
          <span className="text-xs bg-blue-500 text-white px-2 py-1 rounded-full">FREE</span>
        </Link>
        
        <div className="flex items-center space-x-4">
          <Link 
            href="/create" 
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg hover:opacity-90 transition"
          >
            <Sparkles className="h-4 w-4" />
            <span>Create Video</span>
          </Link>
        </div>
      </div>
    </nav>
  )
}
