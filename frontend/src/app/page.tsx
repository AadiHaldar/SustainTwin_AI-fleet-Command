"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Activity, AlertTriangle, Cpu, Droplet, Zap } from "lucide-react"
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const telemetryData = [
  { time: "00:00", rpm: 1200, temp: 85, vibration: 12 },
  { time: "04:00", rpm: 1300, temp: 88, vibration: 14 },
  { time: "08:00", rpm: 2200, temp: 95, vibration: 28 },
  { time: "12:00", rpm: 2400, temp: 102, vibration: 45 },
  { time: "16:00", rpm: 2100, temp: 98, vibration: 35 },
  { time: "20:00", rpm: 1500, temp: 90, vibration: 18 },
  { time: "24:00", rpm: 1200, temp: 86, vibration: 15 },
]

export default function FleetCommand() {
  return (
    <div className="space-y-8 relative">
      {/* Background glowing orb for premium feel */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-emerald-500/10 rounded-full blur-[120px] -z-10 pointer-events-none"></div>

      <div className="flex justify-between items-end pb-2">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-emerald-400 to-blue-500 bg-clip-text text-transparent">Fleet Overview</h2>
          <p className="text-muted-foreground mt-1 text-sm font-medium">Real-time telemetry and AI analytics</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {/* KPI Cards */}
        <motion.initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.1 }}>
          <Card className="relative overflow-hidden bg-zinc-950/40 backdrop-blur-2xl border-white/10 shadow-[0_0_20px_rgba(16,185,129,0.05)] hover:border-emerald-500/50 hover:shadow-[0_0_30px_rgba(16,185,129,0.15)] transition-all duration-300">
            <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 blur-[40px] rounded-full"></div>
            <CardHeader className="flex flex-row items-center justify-between pb-2 z-10 relative">
              <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Active Machines</CardTitle>
              <Cpu className="h-5 w-5 text-emerald-400" />
            </CardHeader>
            <CardContent className="z-10 relative">
              <div className="text-3xl font-extrabold text-white">124 <span className="text-xl text-emerald-400/80 font-medium">/ 125</span></div>
              <div className="flex items-center gap-2 mt-2">
                <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <p className="text-xs text-emerald-400/80 font-medium tracking-wide">99.2% Availability</p>
              </div>
            </CardContent>
          </Card>
        </motion.initial>

        <motion.initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.2 }}>
          <Card className="relative overflow-hidden bg-zinc-950/40 backdrop-blur-2xl border-white/10 shadow-[0_0_20px_rgba(59,130,246,0.05)] hover:border-blue-500/50 hover:shadow-[0_0_30px_rgba(59,130,246,0.15)] transition-all duration-300">
            <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 blur-[40px] rounded-full"></div>
            <CardHeader className="flex flex-row items-center justify-between pb-2 z-10 relative">
              <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Fleet Health Score</CardTitle>
              <Activity className="h-5 w-5 text-blue-400" />
            </CardHeader>
            <CardContent className="z-10 relative">
              <div className="text-3xl font-extrabold text-white">87.4</div>
              <div className="flex items-center gap-1 mt-2 text-xs font-medium text-blue-400/80 bg-blue-500/10 w-fit px-2 py-0.5 rounded-full border border-blue-500/20">
                <Zap className="h-3 w-3" /> +2.4% vs last week
              </div>
            </CardContent>
          </Card>
        </motion.initial>

        <motion.initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.3 }}>
          <Card className="relative overflow-hidden bg-zinc-950/40 backdrop-blur-2xl border-white/10 shadow-[0_0_20px_rgba(239,68,68,0.05)] hover:border-red-500/50 hover:shadow-[0_0_30px_rgba(239,68,68,0.15)] transition-all duration-300">
            <div className="absolute top-0 right-0 w-32 h-32 bg-red-500/10 blur-[40px] rounded-full"></div>
            <CardHeader className="flex flex-row items-center justify-between pb-2 z-10 relative">
              <CardTitle className="text-xs font-semibold uppercase tracking-wider text-red-400">Predicted Failures</CardTitle>
              <AlertTriangle className="h-5 w-5 text-red-400" />
            </CardHeader>
            <CardContent className="z-10 relative">
              <div className="text-3xl font-extrabold text-white">3</div>
              <div className="flex items-center gap-2 mt-2">
                <span className="flex h-2 w-2 rounded-full bg-red-500 animate-pulse"></span>
                <p className="text-xs text-red-400/80 font-medium">Critical attention needed</p>
              </div>
            </CardContent>
          </Card>
        </motion.initial>

        <motion.initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.4 }}>
          <Card className="relative overflow-hidden bg-zinc-950/40 backdrop-blur-2xl border-white/10 shadow-[0_0_20px_rgba(45,212,191,0.05)] hover:border-teal-500/50 hover:shadow-[0_0_30px_rgba(45,212,191,0.15)] transition-all duration-300">
            <div className="absolute top-0 right-0 w-32 h-32 bg-teal-500/10 blur-[40px] rounded-full"></div>
            <CardHeader className="flex flex-row items-center justify-between pb-2 z-10 relative">
              <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Carbon Efficiency</CardTitle>
              <Droplet className="h-5 w-5 text-teal-400" />
            </CardHeader>
            <CardContent className="z-10 relative">
              <div className="text-3xl font-extrabold text-white">92<span className="text-xl text-teal-400/80 font-medium">/100</span></div>
              <p className="text-xs text-teal-400/80 mt-2 font-medium bg-teal-500/10 border border-teal-500/20 w-fit px-2 py-0.5 rounded-full">Targets Met</p>
            </CardContent>
          </Card>
        </motion.initial>
      </div>

      <div className="grid gap-6 md:grid-cols-7">
        <motion.initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }} className="col-span-4">
          <Card className="bg-zinc-950/60 backdrop-blur-2xl border-white/10 h-full shadow-2xl relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
            <CardHeader>
              <CardTitle className="text-lg font-bold">Live Telemetry Streams</CardTitle>
              <CardDescription className="text-muted-foreground font-medium">Fleet-wide aggregated RPM & Temperature</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[350px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={telemetryData} margin={{ top: 20, right: 30, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorRpm" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis dataKey="time" stroke="#666" fontSize={11} tickLine={false} axisLine={false} dy={10} />
                    <YAxis stroke="#666" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} dx={-10} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'rgba(9, 9, 11, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.5)', padding: '12px' }}
                      itemStyle={{ fontWeight: 600 }}
                    />
                    <Area type="monotone" dataKey="rpm" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorRpm)" />
                    <Area type="monotone" dataKey="temp" stroke="#ef4444" strokeWidth={3} fillOpacity={1} fill="url(#colorTemp)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.initial>

        <motion.initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5, delay: 0.2 }} className="col-span-3">
          <Card className="bg-zinc-950/60 backdrop-blur-2xl border-white/10 h-full shadow-2xl relative overflow-hidden">
             <div className="absolute top-0 right-0 p-4 opacity-[0.03] pointer-events-none">
              <Activity className="h-64 w-64" />
            </div>
            <CardHeader>
              <CardTitle className="text-lg font-bold flex items-center gap-2">
                <SparklesIcon /> LangGraph Insights
              </CardTitle>
              <CardDescription className="font-medium">Autonomous agent recommendations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 relative z-10">
              {[
                { machine: "M-104", issue: "Bearing failure imminent (82% probability). Immediate inspection required.", agent: "Health Agent", time: "Just now", risk: "Critical" },
                { machine: "M-102", issue: "Sub-optimal gear shifting leading to 14% higher fuel burn.", agent: "Carbon Agent", time: "15 min ago", risk: "Moderate" },
                { machine: "M-108", issue: "Coolant pressure dropping. Risk of overheating in next shift.", agent: "Predictive Agent", time: "1 hr ago", risk: "High" },
              ].map((alert, i) => (
                <div key={i} className="group flex flex-col p-4 border border-white/5 rounded-xl bg-gradient-to-br from-white/[0.03] to-transparent hover:bg-white/[0.06] hover:border-white/10 transition-all duration-300">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-white">{alert.machine}</span>
                      <Badge variant="outline" className={`font-semibold tracking-wide text-[10px] uppercase border px-2 py-0 ${alert.risk === "Critical" ? "border-red-500/50 text-red-400 bg-red-500/10" : alert.risk === "High" ? "border-orange-500/50 text-orange-400 bg-orange-500/10" : "border-blue-500/50 text-blue-400 bg-blue-500/10"}`}>
                        {alert.risk}
                      </Badge>
                    </div>
                    <div className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">{alert.time}</div>
                  </div>
                  <p className="text-sm text-zinc-300 leading-relaxed mb-3">{alert.issue}</p>
                  <div className="flex justify-between items-center mt-auto">
                    <p className="text-[11px] font-medium text-zinc-500 bg-zinc-900 px-2 py-1 rounded-md border border-white/5 flex items-center gap-1">
                      <BotIcon /> {alert.agent}
                    </p>
                    <button className="text-xs font-semibold text-white bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-md transition-colors">
                      View Action
                    </button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.initial>
      </div>
    </div>
  )
}

function SparklesIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-indigo-400"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>
  )
}

function BotIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>
  )
}
