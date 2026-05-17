"use client"

import { createContext, useContext, useState, ReactNode } from "react"
import companies from "@/data/companies.json"

export type Company = (typeof companies)[number]

interface ProfileContextValue {
  active: Company
  setActive: (company: Company) => void
  companies: Company[]
}

const ProfileContext = createContext<ProfileContextValue | null>(null)

export function ProfileProvider({ children }: { children: ReactNode }) {
  const [active, setActive] = useState<Company>(companies[0])

  return (
    <ProfileContext.Provider value={{ active, setActive, companies }}>
      {children}
    </ProfileContext.Provider>
  )
}

export function useProfile() {
  const ctx = useContext(ProfileContext)
  if (!ctx) throw new Error("useProfile must be used inside ProfileProvider")
  return ctx
}
