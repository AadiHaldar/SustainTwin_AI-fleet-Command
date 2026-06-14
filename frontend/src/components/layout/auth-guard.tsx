"use client"

import * as React from "react"
import { useRouter, usePathname } from "next/navigation"

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const [isAuthenticated, setIsAuthenticated] = React.useState<boolean | null>(null)

  React.useEffect(() => {
    const token = localStorage.getItem("sustaintwin_token")
    if (!token && pathname !== "/login") {
      router.push("/login")
    } else {
      setIsAuthenticated(true)
    }
  }, [pathname, router])

  if (pathname === "/login") {
    return <>{children}</>
  }

  if (isAuthenticated === null) {
    return <div className="min-h-screen bg-zinc-950 flex items-center justify-center text-zinc-500">Loading...</div>
  }

  return <>{children}</>
}
