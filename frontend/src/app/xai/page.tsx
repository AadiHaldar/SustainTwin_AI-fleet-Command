"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Bot, Sparkles, BrainCircuit } from "lucide-react"
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const shapData = [
  { feature: "Vibration Level", impact: 0.82 },
  { feature: "Engine Temp", impact: 0.65 },
  { feature: "Operating Hours", impact: 0.45 },
  { feature: "RPM Variance", impact: 0.32 },
  { feature: "Coolant Pressure", impact: 0.15 },
]

export default function ExplainableAIDashboard() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Explainable AI (XAI)</h2>
          <p className="text-muted-foreground">Demystifying machine learning predictions with SHAP and Gemini.</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }}>
          <Card className="bg-card/50 backdrop-blur-xl border-white/10 h-full">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>SHAP Feature Importance</CardTitle>
                <CardDescription>Machine M-104 - High Failure Risk (82%)</CardDescription>
              </div>
              <BrainCircuit className="h-6 w-6 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={shapData} layout="vertical" margin={{ top: 10, right: 30, left: 40, bottom: 0 }}>
                    <XAxis type="number" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis dataKey="feature" type="category" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} width={100} />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                    <Bar dataKey="impact" fill="#a855f7" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5, delay: 0.2 }}>
          <Card className="bg-gradient-to-br from-indigo-900/40 to-purple-900/40 backdrop-blur-xl border-purple-500/30 h-full relative overflow-hidden">
            <div className="absolute top-0 right-0 p-6 opacity-20 pointer-events-none">
              <Bot className="h-32 w-32" />
            </div>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-indigo-400" />
                <CardTitle>Gemini AI Reasoning</CardTitle>
              </div>
              <CardDescription className="text-indigo-200/70">Natural language explanation for M-104</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 rounded-lg bg-black/40 border border-white/5 backdrop-blur-md">
                <p className="text-sm leading-relaxed text-zinc-300">
                  <span className="text-indigo-300 font-semibold">Diagnosis: </span>
                  Machine M-104 is exhibiting an 82% probability of imminent failure. The primary driver of this prediction is an abnormally high <span className="text-purple-400">Vibration Level</span>, which is 3.2 standard deviations above the fleet average.
                </p>
              </div>
              <div className="p-4 rounded-lg bg-black/40 border border-white/5 backdrop-blur-md">
                <p className="text-sm leading-relaxed text-zinc-300">
                  <span className="text-indigo-300 font-semibold">Root Cause Analysis: </span>
                  The combination of elevated <span className="text-purple-400">Engine Temp</span> alongside high vibrations strongly suggests significant bearing wear or misalignment in the primary drivetrain.
                </p>
              </div>
              <div className="p-4 rounded-lg bg-indigo-500/10 border border-indigo-500/20 backdrop-blur-md">
                <p className="text-sm leading-relaxed text-zinc-300">
                  <span className="text-indigo-300 font-semibold">Recommended Action: </span>
                  Immediately halt operation of M-104. Dispatch field technician to inspect the main bearing assembly. Continuing operation will likely result in catastrophic engine failure within 4 operating hours.
                </p>
              </div>
              <div className="pt-2 flex gap-3">
                <Badge className="bg-indigo-500 hover:bg-indigo-600 cursor-pointer text-white">Generate Full Report</Badge>
                <Badge variant="outline" className="border-indigo-500/50 text-indigo-300 hover:bg-indigo-500/10 cursor-pointer">Dispatch Technician</Badge>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
