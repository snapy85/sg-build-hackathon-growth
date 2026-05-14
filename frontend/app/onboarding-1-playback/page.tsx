"use client"

import { ChevronLeft, ArrowRight } from "lucide-react"
import { useRouter } from "next/navigation"

const summaryRows = [
  { label: "Company type", value: "Limited Company" },
  { label: "Registered", value: "March 2019" },
  { label: "Industry", value: "Creative & Digital" },
  { label: "Employees", value: "4" },
  { label: "Annual turnover", value: "£120,000" },
  { label: "VAT registered", value: "Yes" },
]

export default function Onboarding1PlaybackPage() {
  const router = useRouter()

  return (
    <div className="h-[844px] bg-white flex flex-col px-6 pt-12 pb-10">
      <button
        onClick={() => router.push("/onboarding")}
        className="w-10 h-10 rounded-full bg-[#F4D7E5] flex items-center justify-center mb-8 self-start"
      >
        <ChevronLeft className="h-5 w-5 text-foreground" />
      </button>

      <h1 className="text-3xl font-semibold text-foreground tracking-tight leading-snug mb-8">
        This is<br />NorthLight Studio<br />in a summary.
      </h1>

      <div className="flex flex-col gap-2 flex-1">
        {summaryRows.map((row) => (
          <div
            key={row.label}
            className="flex items-center justify-between px-4 py-3 bg-[#FCF5F8] border border-[#F4D7E5] rounded-xl"
          >
            <span className="text-sm text-muted-foreground">{row.label}</span>
            <span className="text-sm font-medium text-foreground">{row.value}</span>
          </div>
        ))}
      </div>

      <button
        onClick={() => router.push("/onboarding-2")}
        className="mt-6 w-full bg-foreground text-white font-medium py-4 rounded-2xl text-sm flex items-center justify-between px-6"
      >
        Looks right, continue
        <ArrowRight className="h-4 w-4" />
      </button>
    </div>
  )
}
