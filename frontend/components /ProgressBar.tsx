'use client'

interface ProgressBarProps {
  value: number
  max?: number
  label?: string
}

export default function ProgressBar({ value, max = 100, label }: ProgressBarProps) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between mb-2">
          <span className="text-sm text-gray-400">{label}</span>
          <span className="text-sm font-semibold">{Math.round(percentage)}%</span>
        </div>
      )}
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
