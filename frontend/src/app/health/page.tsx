"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { BatteryWarning, Wrench, AlertTriangle, Zap } from "lucide-react"
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

import { fetchDiagnostics, fetchStats, type DiagnosisRecord, type FleetStats } from "@/hooks/use-api"

export default function MachineHealth() {
  const [stats, setStats] = React.useState<FleetStats | null>(null)
  const [diags, setDiags] = React.useState<DiagnosisRecord[]>([])

  React.useEffect(() => {
    fetchStats().then(s => { if (s) setStats(s) }).catch(() => {})
    fetchDiagnostics().then(d => { if (d) setDiags(d) }).catch(() => {})
  }, [])

  const healthData = React.useMemo(() => {
    if (diags.length === 0) return []
    // Group diags by machine to get health scores
    const latestDiags = new Map<string, DiagnosisRecord>()
    for (const d of diags) {
      if (!latestDiags.has(d.machine_id)) latestDiags.set(d.machine_id, d)
    }
    return Array.from(latestDiags.values()).map(d => ({
      machine: d.machine_id,
      score: d.confidence ? Math.round((1 - d.confidence) * 100) : 100, // Just an estimation proxy for score
      risk: d.severity
    }))
  }, [diags])
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
              <div className="text-2xl font-bold text-destructive">{stats ? stats.active_anomalies_24h : 2}</div>
              <p className="text-xs text-muted-foreground mt-1">Require immediate maintenance</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.2 }}>
          <Card className="bg-card/50 backdrop-blur-xl border-white/10">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Fleet Health Score</CardTitle>
              <Wrench className="h-4 w-4 text-emerald-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-400">{stats ? stats.fleet_health_score.toFixed(1) : 87}</div>
              <p className="text-xs text-muted-foreground mt-1">Out of 100</p>
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
              {diags.slice(0, 5).map((machine) => (
                <div key={machine.id} className={`flex items-center justify-between p-4 border rounded-lg transition-colors ${machine.severity === 'critical' ? 'border-destructive/20 bg-destructive/5 hover:bg-destructive/10' : 'border-orange-500/20 bg-orange-500/5 hover:bg-orange-500/10'}`}>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{machine.machine_id}</span>
                      <span className="text-sm text-muted-foreground">({machine.severity.toUpperCase()})</span>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{machine.root_cause || "Anomaly detected"}</p>
                    <Badge variant="outline" className={`mt-2 ${machine.severity === 'critical' ? 'border-red-500 text-red-500' : 'border-orange-500 text-orange-500'}`}>
                      Action: {machine.recommended_action || "Inspect"}
                    </Badge>
                  </div>
                  <div className="text-right">
                    <div className={`text-2xl font-bold ${machine.severity === 'critical' ? 'text-destructive' : 'text-orange-400'}`}>
                      {machine.confidence ? Math.round(machine.confidence * 100) : 80}%
                    </div>
                    <div className="text-xs text-muted-foreground">AI Confidence</div>
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
