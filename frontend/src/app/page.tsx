"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Activity, AlertTriangle, BatteryWarning, Cpu, Droplet, Thermometer } from "lucide-react"
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
    <div className="space-y-6">
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {/* KPI Cards */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.1 }}>
          <Card className="bg-card/50 backdrop-blur-xl border-white/10 hover:border-white/20 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Active Machines</CardTitle>
              <Cpu className="h-4 w-4 text-emerald-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-400">124 / 125</div>
              <p className="text-xs text-muted-foreground mt-1">99.2% availability</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.2 }}>
          <Card className="bg-card/50 backdrop-blur-xl border-white/10 hover:border-white/20 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Fleet Health Score</CardTitle>
              <Activity className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-400">87.4</div>
              <p className="text-xs text-muted-foreground mt-1">+2.4% from last week</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.3 }}>
          <Card className="bg-card/50 backdrop-blur-xl border-destructive/20 hover:border-destructive/40 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-destructive">Predicted Failures</CardTitle>
              <AlertTriangle className="h-4 w-4 text-destructive" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-destructive">3</div>
              <p className="text-xs text-muted-foreground mt-1">Next 48 hours</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.4 }}>
          <Card className="bg-card/50 backdrop-blur-xl border-white/10 hover:border-white/20 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Sustainability Score</CardTitle>
              <Droplet className="h-4 w-4 text-teal-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-teal-400">92/100</div>
              <p className="text-xs text-muted-foreground mt-1">Carbon efficiency nominal</p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <div className="grid gap-6 md:grid-cols-7">
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }} className="col-span-4">
          <Card className="bg-card/50 backdrop-blur-xl border-white/10 h-full">
            <CardHeader>
              <CardTitle>Fleet Telemetry Streams</CardTitle>
              <CardDescription>Live RPM and Temperature aggregated averages</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={telemetryData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorRpm" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="time" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                    />
                    <Area type="monotone" dataKey="rpm" stroke="#3b82f6" fillOpacity={1} fill="url(#colorRpm)" />
                    <Area type="monotone" dataKey="temp" stroke="#f43f5e" fillOpacity={1} fill="url(#colorTemp)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5, delay: 0.2 }} className="col-span-3">
          <Card className="bg-card/50 backdrop-blur-xl border-white/10 h-full">
            <CardHeader>
              <CardTitle>Critical Alerts (LangGraph)</CardTitle>
              <CardDescription>Agent-generated actionable insights</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { machine: "M-104", issue: "High Vibration Detected", agent: "Health Agent", time: "2 min ago", risk: "Critical" },
                { machine: "M-102", issue: "Fuel Inefficiency Pattern", agent: "Carbon Agent", time: "15 min ago", risk: "Moderate" },
                { machine: "M-108", issue: "Overheating Risk in 4hrs", agent: "Predictive Agent", time: "1 hr ago", risk: "High" },
              ].map((alert, i) => (
                <div key={i} className="flex items-center justify-between p-4 border border-white/5 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{alert.machine}</span>
                      <Badge variant="outline" className={alert.risk === "Critical" ? "border-destructive text-destructive" : alert.risk === "High" ? "border-orange-500 text-orange-500" : "border-blue-400 text-blue-400"}>
                        {alert.risk}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{alert.issue}</p>
                    <p className="text-xs text-muted-foreground/60">Generated by: {alert.agent}</p>
                  </div>
                  <div className="text-xs text-muted-foreground">{alert.time}</div>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
