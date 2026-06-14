"use client"

import * as React from "react"
import { usePathname } from "next/navigation"
import Link from "next/link"
import {
  Activity,
  BrainCircuit,
  Command,
  Hexagon,
  Radar,
  ShieldCheck,
  SlidersHorizontal,
  Sprout,
  Wifi,
  WifiOff,
  LogOut
} from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  SidebarFooter,
} from "@/components/ui/sidebar"
import { useWebSocket, type ConnectionStatus } from "@/hooks/use-websocket"

const navItems = [
  { title: "Fleet Command", url: "/", icon: Radar },
  { title: "Machine Health", url: "/health", icon: Activity },
  { title: "Sustainability", url: "/sustainability", icon: Sprout },
  { title: "Digital Twin", url: "/digital-twin", icon: Hexagon },
  { title: "Explainable AI", url: "/xai", icon: BrainCircuit },
  { title: "Security SOC", url: "/security", icon: ShieldCheck },
  { title: "Settings", url: "/settings", icon: SlidersHorizontal },
]

function ConnectionDot({ status }: { status: ConnectionStatus }) {
  if (status === "connected") {
    return (
      <div className="flex items-center gap-2 px-3 py-2 text-xs">
        <span className="relative flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
        </span>
        <span className="text-emerald-400 font-medium">Live</span>
      </div>
    )
  }
  if (status === "connecting") {
    return (
      <div className="flex items-center gap-2 px-3 py-2 text-xs">
        <span className="relative flex h-2.5 w-2.5">
          <span className="animate-pulse relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500" />
        </span>
        <span className="text-amber-400 font-medium">Connecting...</span>
      </div>
    )
  }
  return (
    <div className="flex items-center gap-2 px-3 py-2 text-xs">
      <span className="relative flex h-2.5 w-2.5">
        <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-zinc-600" />
      </span>
      <span className="text-zinc-500 font-medium">Offline</span>
    </div>
  )
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const pathname = usePathname()
  const { status } = useWebSocket()

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link href="/">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <Command className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">SustainTwin</span>
                  <span className="truncate text-xs">Enterprise AI</span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent className="px-3 py-4">
        <SidebarMenu className="space-y-2">
          {navItems.map((item) => (
            <SidebarMenuItem key={item.title}>
              <SidebarMenuButton
                asChild
                isActive={pathname === item.url}
                tooltip={item.title}
                className="h-10 px-3"
              >
                <Link href={item.url} className="flex items-center gap-3">
                  <item.icon className="h-5 w-5 shrink-0" />
                  <span className="font-medium text-[13px]">{item.title}</span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarContent>
      <SidebarFooter className="p-3 space-y-2">
        <ConnectionDot status={status} />
        <button 
          onClick={() => {
            localStorage.removeItem("sustaintwin_token")
            localStorage.removeItem("sustaintwin_role")
            window.location.href = "/login"
          }}
          className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100 transition-colors"
        >
          <LogOut className="h-4 w-4" />
          <span>Sign Out</span>
        </button>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
