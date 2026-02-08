import { ArrowRight, CheckCircle, Zap, Download, Video } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  const features = [
    { icon: <Video />, title: 'Text to Video', desc: 'Transform scripts into cinematic videos' },
    { icon: <Zap />, title: 'AI Avatars', desc: 'Talking avatars with perfect lip sync' },
    { icon: <Download />, title: 'Free Download', desc: 'HD MP4 with no watermarks' },
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16 text-center">
        <h1 className="text-6xl md:text-7xl font-bold mb-6">
          Create <span className="gradient-text">AI Videos</span>
          <br />
          From Text
        </h1>
        
        <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto">
          Generate professional videos with AI avatars, voiceovers, and cinematic effects.
          100% free - no credit card required.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
          <Link 
            href="/create" 
            className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl hover:opacity-90 transition group"
          >
            Start Creating Free
            <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition" />
          </Link>
          <button className="px-8 py-4 text-lg font-semibold glass-effect rounded-xl hover:bg-white/10 transition">
            Watch Demo
          </button>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto mb-20">
          {features.map((feat, idx) => (
            <div key={idx} className="glass-effect p-6 rounded-2xl">
              <div className="inline-flex p-3 bg-blue-500/20 rounded-lg mb-4">
                {feat.icon}
              </div>
              <h3 className="text-xl font-semibold mb-2">{feat.title}</h3>
              <p className="text-gray-400">{feat.desc}</p>
            </div>
          ))}
        </div>

        {/* How It Works */}
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold mb-10">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-6">
            {[
              { step: '1', title: 'Write Script', desc: 'Enter your text' },
              { step: '2', title: 'Choose Style', desc: 'Select video style' },
              { step: '3', title: 'Generate', desc: 'AI creates video' },
              { step: '4', title: 'Download', desc: 'Get your video' },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                  {item.step}
                </div>
                <h4 className="font-semibold mb-2">{item.title}</h4>
                <p className="text-sm text-gray-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
