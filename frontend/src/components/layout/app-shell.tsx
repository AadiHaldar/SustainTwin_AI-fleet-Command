"use client"

import * as React from "react"
import { usePathname } from "next/navigation"
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/layout/app-sidebar"

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  if (pathname === "/login") {
    return <main className="flex-1">{children}</main>
  }

  return (
    <SidebarProvider>
      <AppSidebar />
      <main className="flex-1 flex flex-col min-h-screen overflow-y-auto bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4 backdrop-blur-md sticky top-0 z-10">
          <SidebarTrigger className="-ml-1" />
          <div className="w-full flex justify-between items-center px-4">
            <h1 className="text-xl font-semibold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">Fleet Command Center</h1>
            <div className="flex items-center gap-4">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </span>
              <span className="text-sm text-emerald-400 font-medium">System Nominal</span>
            </div>
          </div>
        </header>
        <div className="p-6">
          {children}
        </div>
      </main>
    </SidebarProvider>
  )
}
