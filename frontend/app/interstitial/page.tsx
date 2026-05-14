"use client"

import { useEffect, useState } from "react"

export default function InterstitialPage() {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 400)
    return () => clearTimeout(t)
  }, [])

  return (
    <div className="h-[844px] bg-[#F4D7E5] flex flex-col items-center justify-center px-6 text-center">
      <div
        className={`transition-all duration-700 ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}
      >
        <p className="text-2xl font-semibold text-foreground tracking-tight mb-3">
          Going out to check different data...
        </p>
        <p className="text-base font-normal text-foreground/60">
          Crunching crunching...
        </p>

        {/* Dots loader */}
        <div className="flex items-center justify-center gap-2 mt-10">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="w-2 h-2 rounded-full bg-foreground/40 animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
