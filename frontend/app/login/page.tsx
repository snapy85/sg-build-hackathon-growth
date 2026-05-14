import { ArrowRight } from "lucide-react"

export default function LoginPage() {
  return (
    <div className="h-[844px] bg-white flex flex-col px-6 pt-16 pb-10">
      {/* Logo */}
      <div className="mb-16">
        <span className="text-xl font-black tracking-tight text-foreground">
          Funding<span className="text-accent">Fit</span>
        </span>
      </div>

      {/* Content */}
      <div className="flex-1">
        <h1 className="text-3xl font-semibold text-foreground tracking-tight leading-snug mb-6">
          Are you NorthLight Studio?
        </h1>
        <p className="text-base font-normal text-muted-foreground leading-relaxed">
          We need 10 minutes of your time to get the right information about your business and your ambitions.
        </p>
      </div>

      {/* CTA */}
      <button className="w-full bg-foreground text-white font-medium py-4 rounded-2xl text-sm flex items-center justify-between px-6">
        Continue as NorthLight Studio
        <ArrowRight className="h-4 w-4" />
      </button>
    </div>
  )
}
