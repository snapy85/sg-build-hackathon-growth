"use client"

import { TrendingUp, Clock, Star } from "lucide-react"
import { BottomNav } from "@/components/bottom-nav"
import { Card } from "@/components/ui/card"
import { useProfile } from "@/lib/profile-context"

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

export default function DashboardPage() {
  const { active } = useProfile()
  const name = active.user_provided.trading_name

  return (
    <div className="min-h-full bg-white pb-24">
      {/* Logo */}
      <div className="flex justify-center pt-12 pb-2">
        <span className="text-xl font-black tracking-tight text-foreground">
          Funding<span className="text-accent">Fit</span>
        </span>
      </div>

      {/* Header */}
      <header className="px-6 pt-6 pb-8">
        <p className="text-2xl font-normal text-foreground mb-1">Good morning,</p>
        <h1 className="text-2xl font-semibold text-foreground tracking-tight">
          {name}.
        </h1>
      </header>

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

      {/* Suggested Schemes */}
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

      <BottomNav />
    </div>
  )
}
