import type { Metadata } from 'next'
import './globals.css'
import Navbar from '@/components/Navbar'

export const metadata: Metadata = {
  title: 'AI Video Generator - Free',
  description: 'Create AI videos from text for free',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <head>
        {/* Use system fonts instead of Google Fonts */}
        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        `}</style>
      </head>
      <body className="min-h-screen bg-gradient-to-br from-gray-900 to-black">
        <Navbar />
        {children}
      </body>
    </html>
  )
}
