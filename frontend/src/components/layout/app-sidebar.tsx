"use client"

import * as React from "react"
import {
  Activity,
  BrainCircuit,
  Command,
  Hexagon,
  Radar,
  ShieldCheck,
  SlidersHorizontal,
  Sprout,
} from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  SidebarGroup,
} from "@/components/ui/sidebar"

const data = {
  navMain: [
    {
      title: "Fleet Command",
      url: "/",
      icon: Radar,
      isActive: true,
    },
    {
      title: "Machine Health",
      url: "/health",
      icon: Activity,
    },
    {
      title: "Sustainability",
      url: "/sustainability",
      icon: Sprout,
    },
    {
      title: "Digital Twin",
      url: "/digital-twin",
      icon: Hexagon,
    },
    {
      title: "Explainable AI",
      url: "/xai",
      icon: BrainCircuit,
    },
    {
      title: "Security SOC",
      url: "/security",
      icon: ShieldCheck,
    },
    {
      title: "Settings",
      url: "/settings",
      icon: SlidersHorizontal,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <a href="/">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <Command className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">SustainTwin</span>
                  <span className="truncate text-xs">Enterprise AI</span>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent className="px-3 py-4">
        <SidebarMenu className="space-y-2">
          {data.navMain.map((item) => (
            <SidebarMenuItem key={item.title}>
              <SidebarMenuButton asChild isActive={item.isActive} tooltip={item.title} className="h-10 px-3">
                <a href={item.url} className="flex items-center gap-3">
                  <item.icon className="h-5 w-5 shrink-0" />
                  <span className="font-medium text-[13px]">{item.title}</span>
                </a>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  )
}
