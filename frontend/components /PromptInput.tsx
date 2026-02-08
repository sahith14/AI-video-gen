'use client'

interface PromptInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
}

export default function PromptInput({ value, onChange, placeholder }: PromptInputProps) {
  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full h-48 p-4 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
      maxLength={1000}
    />
  )
}
