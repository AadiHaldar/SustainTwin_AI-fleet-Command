"use client"

import * as React from "react"
import {
  Activity,
  BarChart3,
  Bot,
  Command,
  Globe2,
  LayoutDashboard,
  Leaf,
  Settings2,
  ShieldAlert,
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
} from "@/components/ui/sidebar"

const data = {
  navMain: [
    {
      title: "Fleet Command",
      url: "/",
      icon: LayoutDashboard,
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
      icon: Leaf,
    },
    {
      title: "Digital Twin",
      url: "/digital-twin",
      icon: Globe2,
    },
    {
      title: "Explainable AI",
      url: "/xai",
      icon: Bot,
    },
    {
      title: "Security SOC",
      url: "/security",
      icon: ShieldAlert,
    },
    {
      title: "Settings",
      url: "/settings",
      icon: Settings2,
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
      <SidebarContent>
        <SidebarMenu>
          {data.navMain.map((item) => (
            <SidebarMenuItem key={item.title}>
              <SidebarMenuButton asChild isActive={item.isActive} tooltip={item.title}>
                <a href={item.url}>
                  <item.icon />
                  <span>{item.title}</span>
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
