"use client"

import { useState, useRef, useEffect } from "react"
import { ChevronDown, Check } from "lucide-react"
import { useProfile } from "@/lib/profile-context"

export function LogoBar() {
  const { active, setActive, companies } = useProfile()
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClick)
    return () => document.removeEventListener("mousedown", handleClick)
  }, [])

  const tradingName = active.user_provided.trading_name

  return (
    <div className="flex items-center justify-between">
      <span className="text-xl font-black tracking-tight text-foreground">
        Funding<span className="text-accent">Fit</span>
      </span>

      <div className="relative" ref={ref}>
        <button
          onClick={() => setOpen((o) => !o)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#FCF5F8] border border-[#F4D7E5] text-xs font-medium text-foreground hover:border-foreground/20 transition-colors"
        >
          <span className="max-w-[120px] truncate">{tradingName}</span>
          <ChevronDown className={`h-3 w-3 text-muted-foreground transition-transform ${open ? "rotate-180" : ""}`} />
        </button>

        {open && (
          <div className="absolute right-0 top-full mt-2 w-52 bg-white border border-[#F4D7E5] rounded-2xl shadow-lg overflow-hidden z-50">
            {companies.map((company) => {
              const name = company.user_provided.trading_name
              const sector = company.derived.sector.replace(/_/g, " ")
              const isActive = company.profile_id === active.profile_id
              return (
                <button
                  key={company.profile_id}
                  onClick={() => { setActive(company); setOpen(false) }}
                  className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-[#FCF5F8] transition-colors"
                >
                  <div>
                    <p className="text-sm font-medium text-foreground leading-tight">{name}</p>
                    <p className="text-xs text-muted-foreground capitalize mt-0.5">{sector}</p>
                  </div>
                  {isActive && <Check className="h-4 w-4 text-accent flex-shrink-0" />}
                </button>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
