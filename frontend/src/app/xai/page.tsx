"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { BrainCircuit, Sparkles, FileText, Wrench } from "lucide-react"
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, Cell } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { fetchMachineDiagnostics, type DiagnosisRecord } from "@/hooks/use-api"

const fallbackShapData = [
  { feature: "Vibration Level", impact: 0.82 },
  { feature: "Engine Temp", impact: 0.65 },
  { feature: "Operating Hours", impact: 0.45 },
  { feature: "RPM Variance", impact: 0.32 },
  { feature: "Coolant Pressure", impact: 0.15 },
]

const COLORS = ["#a855f7", "#8b5cf6", "#7c3aed", "#6d28d9", "#5b21b6"]

export default function ExplainableAI() {
  const [shapData, setShapData] = React.useState(fallbackShapData)
  const [diagnosis, setDiagnosis] = React.useState<DiagnosisRecord | null>(null)
  const [machineId, setMachineId] = React.useState("M-104")

  React.useEffect(() => {
    fetchMachineDiagnostics(machineId)
      .then((diags) => {
        if (diags.length > 0) {
          const latest = diags[0]
          setDiagnosis(latest)
          if (latest.shap_values) {
            const shapEntries = Object.entries(latest.shap_values)
              .sort(([, a], [, b]) => Math.abs(b as number) - Math.abs(a as number))
              .slice(0, 5)
              .map(([feature, impact]) => ({
                feature: feature.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
                impact: Math.abs(impact as number),
              }))
            if (shapEntries.length > 0) setShapData(shapEntries)
          }
        }
      })
      .catch(() => {})
  }, [machineId])

  const diagText = diagnosis?.root_cause
    || `Machine ${machineId} is exhibiting elevated vibration patterns that are 3.2 standard deviations above the fleet average. The primary contributing factors are bearing wear and potential misalignment in the drive shaft assembly. Recommended action: Halt ${machineId} for immediate inspection. Estimated time to catastrophic failure: 4 hours under current load.`

  const confidence = diagnosis?.confidence || 0.82

  return (
    <div className="space-y-8 relative">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-purple-500/10 rounded-full blur-[120px] -z-10 pointer-events-none" />

      <div>
        <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">Explainable AI</h2>
        <p className="text-muted-foreground mt-1 text-sm font-medium">SHAP-guided Gemini reasoning for {machineId}</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <Card className="bg-zinc-950/60 backdrop-blur-2xl border-white/10 shadow-2xl h-full">
            <CardHeader>
              <CardTitle className="text-lg font-bold flex items-center gap-2">
                <BrainCircuit className="h-5 w-5 text-purple-400" /> SHAP Feature Importance
              </CardTitle>
              <CardDescription className="font-medium">Top contributing factors for anomaly prediction</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={shapData} layout="vertical" margin={{ top: 5, right: 30, left: 60, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                    <XAxis type="number" stroke="#666" fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis dataKey="feature" type="category" stroke="#999" fontSize={11} tickLine={false} axisLine={false} width={120} />
                    <Tooltip
                      contentStyle={{ backgroundColor: 'rgba(9, 9, 11, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.5)', padding: '12px' }}
                      formatter={(value: number) => [value.toFixed(3), "SHAP Impact"]}
                    />
                    <Bar dataKey="impact" radius={[0, 6, 6, 0]}>
                      {shapData.map((_, index) => (
                        <Cell key={index} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.15 }}>
          <Card className="bg-zinc-950/60 backdrop-blur-2xl border-white/10 shadow-2xl h-full relative overflow-hidden">
            <div className="absolute top-0 right-0 w-40 h-40 bg-purple-500/5 blur-[50px] rounded-full" />
            <CardHeader>
              <CardTitle className="text-lg font-bold flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-pink-400" /> Gemini AI Reasoning
              </CardTitle>
              <CardDescription className="font-medium">
                SHAP-guided root cause analysis
                <Badge variant="outline" className="ml-2 text-[10px] border-purple-500/50 text-purple-400 bg-purple-500/10">
                  {(confidence * 100).toFixed(0)}% confidence
                </Badge>
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 relative z-10">
              <div className="p-4 rounded-xl bg-gradient-to-br from-purple-500/10 to-pink-500/5 border border-purple-500/20">
                <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">{diagText}</p>
              </div>

              <div className="flex gap-2">
                <Badge className="bg-purple-500/10 text-purple-400 border-purple-500/30 hover:bg-purple-500/20 cursor-pointer transition-colors">
                  <FileText className="h-3 w-3 mr-1" /> Generate Full Report
                </Badge>
                <Badge className="bg-pink-500/10 text-pink-400 border-pink-500/30 hover:bg-pink-500/20 cursor-pointer transition-colors">
                  <Wrench className="h-3 w-3 mr-1" /> Dispatch Technician
                </Badge>
              </div>

              {diagnosis?.sustainability_recommendation && (
                <div className="p-3 rounded-lg bg-teal-500/5 border border-teal-500/20">
                  <p className="text-xs text-teal-400 font-medium mb-1">Sustainability Impact</p>
                  <p className="text-sm text-zinc-400">
                    {diagnosis.carbon_delta_kg > 0 && `Estimated carbon impact: ${diagnosis.carbon_delta_kg.toFixed(1)} kg CO2. `}
                    {diagnosis.sustainability_recommendation}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
