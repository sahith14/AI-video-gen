'use client'

interface Style {
  id: string
  label: string
  icon: string
}

interface StyleSelectorProps {
  selected: string[]
  onChange: (styles: string[]) => void
  styles: Style[]
}

export default function StyleSelector({ selected, onChange, styles }: StyleSelectorProps) {
  const toggleStyle = (styleId: string) => {
    if (selected.includes(styleId)) {
      onChange(selected.filter(id => id !== styleId))
    } else {
      onChange([...selected, styleId])
    }
  }

  return (
    <div className="grid grid-cols-2 gap-3">
      {styles.map((style) => (
        <button
          key={style.id}
          onClick={() => toggleStyle(style.id)}
          className={`p-4 rounded-xl border-2 transition-all ${
            selected.includes(style.id)
              ? 'border-blue-500 bg-blue-500/20'
              : 'border-white/10 bg-white/5 hover:bg-white/10'
          }`}
        >
          <div className="text-2xl mb-2">{style.icon}</div>
          <div className="text-sm">{style.label}</div>
        </button>
      ))}
    </div>
  )
}
