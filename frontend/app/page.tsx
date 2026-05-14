import { ArrowRight, TrendingUp, Clock, Star } from "lucide-react"
import { BottomNav } from "@/components/bottom-nav"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

// Mock data for quick actions
const quickActions = [
  {
    icon: <TrendingUp className="h-5 w-5" />,
    title: "Innovation Grants",
    description: "R&D and tech funding",
  },
  {
    icon: <Clock className="h-5 w-5" />,
    title: "Closing Soon",
    description: "Apply before deadline",
  },
  {
    icon: <Star className="h-5 w-5" />,
    title: "Recommended",
    description: "Based on your profile",
  },
]

// Mock data for recent schemes
const recentSchemes = [
  {
    name: "Innovate UK Smart Grants",
    amount: "£25k - £500k",
    deadline: "Rolling",
    tag: "Innovation",
  },
  {
    name: "Growth Hub Business Support",
    amount: "Up to £10k",
    deadline: "31 Jul 2026",
    tag: "Growth",
  },
]

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <header className="px-6 pt-12 pb-8">
        <p className="text-sm text-muted-foreground mb-1">Good morning,</p>
        <h1 className="text-2xl font-semibold text-foreground tracking-tight">
          Northlight Studio.
        </h1>
      </header>

      {/* Main CTA Section */}
      <section className="px-6 mb-8">
        <Card className="bg-primary text-primary-foreground p-6 rounded-2xl">
          <h2 className="text-xl font-semibold mb-2 text-balance">
            Find funding for your business.
          </h2>
          <p className="text-sm opacity-90 mb-6 leading-relaxed">
            Discover grants, loans, and support schemes you&apos;re eligible for across the UK.
          </p>
          <Button 
            variant="secondary" 
            className="w-full justify-between text-secondary-foreground font-medium"
          >
            Start eligibility check
            <ArrowRight className="h-4 w-4" />
          </Button>
        </Card>
      </section>

      {/* Quick Actions */}
      <section className="px-6 mb-8">
        <h3 className="text-sm font-medium text-muted-foreground mb-4 uppercase tracking-wide">
          Quick Actions
        </h3>
        <div className="grid grid-cols-3 gap-3">
          {quickActions.map((action) => (
            <button
              key={action.title}
              className="flex flex-col items-center text-center p-4 bg-card rounded-xl border border-border hover:border-primary/30 transition-colors"
            >
              <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center mb-2 text-foreground">
                {action.icon}
              </div>
              <span className="text-xs font-medium text-foreground leading-tight">
                {action.title}
              </span>
            </button>
          ))}
        </div>
      </section>

      {/* Recent/Suggested Schemes */}
      <section className="px-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
            Suggested for you
          </h3>
          <button className="text-sm text-accent font-medium">
            View all
          </button>
        </div>
        <div className="space-y-3">
          {recentSchemes.map((scheme) => (
            <Card
              key={scheme.name}
              className="p-4 rounded-xl border border-border hover:border-primary/30 transition-colors cursor-pointer"
            >
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-medium text-foreground text-sm leading-snug flex-1 pr-2">
                  {scheme.name}
                </h4>
                <span className="text-xs bg-secondary text-secondary-foreground px-2 py-1 rounded-full whitespace-nowrap">
                  {scheme.tag}
                </span>
              </div>
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <span className="font-medium text-foreground">{scheme.amount}</span>
                <span>•</span>
                <span>Deadline: {scheme.deadline}</span>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Bottom Navigation */}
      <BottomNav />
    </div>
  )
}
