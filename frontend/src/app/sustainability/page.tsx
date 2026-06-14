"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Leaf, Wind, Zap, Factory } from "lucide-react"
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis, PieChart, Pie, Cell } from "recharts"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { fetchDiagnostics, fetchStats, type DiagnosisRecord, type FleetStats } from "@/hooks/use-api"

const emissionsData = [
  { time: "Mon", co2: 4000, target: 4500 },
  { time: "Tue", co2: 3000, target: 4500 },
  { time: "Wed", co2: 2000, target: 4500 },
  { time: "Thu", co2: 2780, target: 4500 },
  { time: "Fri", co2: 1890, target: 4500 },
  { time: "Sat", co2: 2390, target: 4500 },
  { time: "Sun", co2: 3490, target: 4500 },
]

const carbonSources = [
  { name: "Excavators", value: 400 },
  { name: "Haul Trucks", value: 300 },
  { name: "Loaders", value: 300 },
  { name: "Generators", value: 200 },
]
const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#6366f1']

export default function SustainabilityDashboard() {
  const [stats, setStats] = React.useState<FleetStats | null>(null)
  const [diags, setDiags] = React.useState<DiagnosisRecord[]>([])

  React.useEffect(() => {
    fetchStats().then(s => { if (s) setStats(s) }).catch(() => {})
    fetchDiagnostics().then(d => { if (d) setDiags(d) }).catch(() => {})
  }, [])

  // Get top 2 unique sustainability recommendations
  const recommendations = React.useMemo(() => {
    const recs: { text: string; carbon: number }[] = []
    const seen = new Set()
    for (const d of diags) {
      if (d.sustainability_recommendation && d.carbon_delta_kg > 0) {
        if (!seen.has(d.sustainability_recommendation)) {
          seen.add(d.sustainability_recommendation)
          recs.push({ text: d.sustainability_recommendation, carbon: d.carbon_delta_kg })
        }
      }
      if (recs.length >= 2) break
    }
    return recs
  }, [diags])

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Sustainability Intelligence</h2>
          <p className="text-muted-foreground">Carbon footprint tracking and Agent-driven emission reductions.</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.1 }}>
          <Card className="bg-card/50 backdrop-blur-xl border-white/10 hover:border-white/20 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Emissions</CardTitle>
              <Wind className="h-4 w-4 text-emerald-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-400">
                {stats ? Math.round(stats.total_carbon_saved_kg).toLocaleString() : "19,550"} kg
              </div>
              <p className="text-xs text-muted-foreground mt-1">Total optimization savings</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.2 }}>
          <Card className="bg-card/50 backdrop-blur-xl border-white/10 hover:border-white/20 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Carbon Budget</CardTitle>
              <Leaf className="h-4 w-4 text-teal-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-teal-400">68% Used</div>
              <p className="text-xs text-muted-foreground mt-1">On track to meet Q3 goal</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.3 }}>
          <Card className="bg-card/50 backdrop-blur-xl border-white/10 hover:border-white/20 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Fuel Optimization</CardTitle>
              <Zap className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-400">8.4 L/hr</div>
              <p className="text-xs text-muted-foreground mt-1">Average fleet consumption</p>
            </CardContent>
          </Card>
        </motion.div>
        
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.4 }}>
          <Card className="bg-card/50 backdrop-blur-xl border-white/10 hover:border-white/20 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Active Sites</CardTitle>
              <Factory className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-400">4</div>
              <p className="text-xs text-muted-foreground mt-1">Across 2 regions</p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <div className="grid gap-6 md:grid-cols-7">
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }} className="col-span-4">
          <Card className="bg-card/50 backdrop-blur-xl border-white/10 h-full">
            <CardHeader>
              <CardTitle>CO₂ Emissions vs Target (Weekly)</CardTitle>
              <CardDescription>Actual emissions plotted against carbon budget caps</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={emissionsData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorCo2" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="time" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                    <Area type="monotone" dataKey="co2" stroke="#10b981" fillOpacity={1} fill="url(#colorCo2)" />
                    <Area type="monotone" dataKey="target" stroke="#f43f5e" fillOpacity={0} strokeDasharray="5 5" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5, delay: 0.2 }} className="col-span-3">
          <Card className="bg-card/50 backdrop-blur-xl border-white/10 h-full">
            <CardHeader>
              <CardTitle>Carbon Agent Recommendations</CardTitle>
              <CardDescription>AI-driven strategies to cut emissions</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {recommendations.length > 0 ? (
                recommendations.map((rec, i) => (
                  <div key={i} className={`flex items-center justify-between p-4 border rounded-lg ${i === 0 ? 'border-emerald-500/20 bg-emerald-500/5' : 'border-blue-500/20 bg-blue-500/5'}`}>
                    <div>
                      <h4 className="font-semibold">{i === 0 ? "Priority Optimization" : "Secondary Action"}</h4>
                      <p className="text-sm text-muted-foreground mt-1">{rec.text}</p>
                      <Badge variant="outline" className={`mt-2 ${i === 0 ? 'border-emerald-500 text-emerald-500' : 'border-blue-500 text-blue-500'}`}>Save {Math.round(rec.carbon)} kg CO₂</Badge>
                    </div>
                    <Badge>Execute</Badge>
                  </div>
                ))
              ) : (
                <div className="text-sm text-zinc-400 italic py-4">No active recommendations. Analyzing telemetry...</div>
              )}
              
              <div className="pt-4 flex justify-center">
                <ResponsiveContainer width="100%" height={120}>
                  <PieChart>
                    <Pie data={carbonSources} cx="50%" cy="50%" innerRadius={40} outerRadius={60} paddingAngle={5} dataKey="value">
                      {carbonSources.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
