"use client"

import { ArrowRight } from "lucide-react"
import { useRouter } from "next/navigation"

const partners = ["GOV.UK", "Companies House", "HMRC"]

export default function HomePage() {
  const router = useRouter()

  return (
    <div className="h-[844px] bg-white flex flex-col px-6 pt-16 pb-10">
      <div className="mb-16">
        <span className="text-xl font-black tracking-tight text-foreground">
          Funding<span className="text-accent">Fit</span>
        </span>
      </div>

      <div className="flex-1">
        <h1 className="text-3xl font-semibold text-foreground tracking-tight leading-snug mb-6">
          Welcome to<br />FundingFit.
        </h1>
        <p className="text-base font-normal text-muted-foreground leading-relaxed mb-12">
          We use government data to match you with opportunities to grow your business.
        </p>

        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-4">
            We work with
          </p>
          <div className="flex gap-3">
            {partners.map((p) => (
              <span
                key={p}
                className="px-3 py-1.5 rounded-full border border-[#F4D7E5] bg-[#FCF5F8] text-xs font-medium text-foreground"
              >
                {p}
              </span>
            ))}
          </div>
        </div>
      </div>

      <button
        onClick={() => router.push("/login")}
        className="w-full bg-foreground text-white font-medium py-4 rounded-2xl text-sm flex items-center justify-between px-6"
      >
        Continue with your business log in
        <ArrowRight className="h-4 w-4" />
      </button>
    </div>
  )
}
