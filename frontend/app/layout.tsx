import type { Metadata } from 'next'
import './globals.css'
import Navbar from '@/components/Navbar'
import { inter } from './font'

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
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen bg-gradient-to-br from-gray-900 to-black">
        <Navbar />
        {children}
      </body>
    </html>
  )
}
