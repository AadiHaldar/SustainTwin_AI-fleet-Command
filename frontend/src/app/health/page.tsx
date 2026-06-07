"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { BatteryWarning, Wrench, AlertTriangle, Zap } from "lucide-react"
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const healthData = [
  { machine: "M-101", score: 98, hours: 1200 },
  { machine: "M-102", score: 75, hours: 3400 },
  { machine: "M-103", score: 92, hours: 2100 },
  { machine: "M-104", score: 45, hours: 4800 },
  { machine: "M-105", score: 88, hours: 1500 },
  { machine: "M-106", score: 96, hours: 900 },
  { machine: "M-107", score: 62, hours: 4100 },
]

export default function MachineHealth() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Machine Health</h2>
          <p className="text-muted-foreground">Individual asset condition and RUL predictions.</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.1 }}>
          <Card className="bg-card/50 backdrop-blur-xl border-white/10">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Critical Assets</CardTitle>
              <AlertTriangle className="h-4 w-4 text-destructive" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-destructive">2</div>
              <p className="text-xs text-muted-foreground mt-1">Require immediate maintenance</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.2 }}>
          <Card className="bg-card/50 backdrop-blur-xl border-white/10">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Scheduled Maintenance</CardTitle>
              <Wrench className="h-4 w-4 text-orange-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-400">8</div>
              <p className="text-xs text-muted-foreground mt-1">Within next 7 days</p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }}>
          <Card className="bg-card/50 backdrop-blur-xl border-white/10 h-full">
            <CardHeader>
              <CardTitle>Health Score by Machine</CardTitle>
              <CardDescription>Real-time LangGraph agent scoring</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={healthData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <XAxis dataKey="machine" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                    <Bar dataKey="score" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5, delay: 0.2 }}>
          <Card className="bg-card/50 backdrop-blur-xl border-white/10 h-full">
            <CardHeader>
              <CardTitle>Needs Attention</CardTitle>
              <CardDescription>Machines with low RUL (Remaining Useful Life)</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { id: "M-104", type: "Excavator", score: 45, issue: "Bearing wear (SHAP feature: vibration)", action: "Replace Part" },
                { id: "M-107", type: "Haul Truck", score: 62, issue: "Coolant leak (SHAP feature: temp)", action: "Inspect Engine" },
              ].map((machine) => (
                <div key={machine.id} className="flex items-center justify-between p-4 border border-destructive/20 rounded-lg bg-destructive/5 hover:bg-destructive/10 transition-colors">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{machine.id}</span>
                      <span className="text-sm text-muted-foreground">({machine.type})</span>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{machine.issue}</p>
                    <Badge variant="outline" className="mt-2 border-orange-500 text-orange-500 hover:bg-orange-500 hover:text-white cursor-pointer">
                      Action: {machine.action}
                    </Badge>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-destructive">{machine.score}</div>
                    <div className="text-xs text-muted-foreground">Score</div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
