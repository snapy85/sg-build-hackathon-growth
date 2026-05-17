"use client"

import { ChevronLeft, ArrowRight } from "lucide-react"
import { useRouter } from "next/navigation"
import { useProfile } from "@/lib/profile-context"

export default function Onboarding1PlaybackPage() {
  const router = useRouter()
  const { active } = useProfile()

  const ch = active.companies_house
  const hmrc = active.hmrc
  const derived = active.derived
  const gov = active.gov_uk_one_login

  const rows = [
    { label: "Trading name", value: active.user_provided.trading_name },
    { label: "Legal name", value: ch?.legal_name ?? "—" },
    { label: "Company number", value: ch?.company_number ?? "—" },
    { label: "Company type", value: ch?.company_type?.toUpperCase() ?? derived.legal_structure.replace(/_/g, " ") },
    { label: "Incorporated", value: ch?.incorporation_date ?? "—" },
    { label: "Status", value: ch?.company_status ?? "—" },
    { label: "Sector", value: derived.sector.replace(/_/g, " ") },
    { label: "Region", value: derived.region },
    { label: "Trading age", value: `${derived.trading_age_years} years` },
    { label: "Industry (SIC)", value: ch?.sic_descriptions?.[0] ?? "—" },
    { label: "Directors", value: ch?.directors?.filter(d => !d.resigned_on).map(d => d.name).join(", ") ?? "—" },
    { label: "Address", value: ch ? `${ch.registered_office_address.address_line_1}, ${ch.registered_office_address.locality}, ${ch.registered_office_address.postal_code}` : "—" },
    { label: "Legal structure", value: hmrc.legal_structure.replace(/_/g, " ") },
    { label: "VAT registered", value: hmrc.vat_registered ? `Yes (${hmrc.vat_number})` : "No" },
    { label: "Annual turnover", value: hmrc.self_assessment ? `£${hmrc.self_assessment.turnover.toLocaleString()}` : "—" },
    { label: "Employees on payroll", value: hmrc.paye ? String(hmrc.paye.employees_on_payroll) : "—" },
    { label: "Email", value: gov.email },
    { label: "Identity verified", value: gov.identity_verified ? `Yes (${gov.verification_level})` : "No" },
  ]

  return (
    <div className="h-[844px] bg-white flex flex-col px-6 pt-12 pb-10 overflow-y-auto">
      <button
        onClick={() => router.push("/onboarding")}
        className="w-10 h-10 rounded-full bg-[#F4D7E5] flex items-center justify-center mb-8 self-start flex-shrink-0"
      >
        <ChevronLeft className="h-5 w-5 text-foreground" />
      </button>

      <h1 className="text-3xl font-semibold text-foreground tracking-tight leading-snug mb-8 flex-shrink-0">
        This is<br />{active.user_provided.trading_name}<br />in a summary.
      </h1>

      <div className="flex flex-col gap-2 flex-1">
        {rows.map((row) => (
          <div
            key={row.label}
            className="flex items-start justify-between px-4 py-3 bg-[#FCF5F8] border border-[#F4D7E5] rounded-xl gap-4"
          >
            <span className="text-sm text-muted-foreground flex-shrink-0">{row.label}</span>
            <span className="text-sm font-medium text-foreground text-right capitalize">{row.value}</span>
          </div>
        ))}
      </div>

      <button
        onClick={() => router.push("/onboarding-2")}
        className="mt-6 w-full bg-foreground text-white font-medium py-4 rounded-2xl text-sm flex items-center justify-between px-6 flex-shrink-0"
      >
        Looks right, continue
        <ArrowRight className="h-4 w-4" />
      </button>
    </div>
  )
}
