"use client";

import { useEffect, useState, useMemo } from "react";
import { useWebSocket } from "@/hooks/use-websocket";
import { useApi } from "@/hooks/use-api";
import { 
  ComposedChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Activity, Gauge, Zap, Thermometer, Droplets, Waves } from "lucide-react";

export default function DigitalTwinPage() {
  const [machineId, setMachineId] = useState("M-100");
  const [history, setHistory] = useState<any[]>([]);
  
  const { isConnected, lastMessage } = useWebSocket();
  const api = useApi();

  // Fetch history on mount / machine change
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await api.get(`/twin/${machineId}/history?limit=30`);
        // Reverse so chronological left to right
        setHistory(data || []);
      } catch (err) {
        console.error("Failed to fetch twin history", err);
      }
    };
    fetchHistory();
  }, [machineId]);

  // Handle incoming live data
  useEffect(() => {
    if (lastMessage?.type === "telemetry_sync" && lastMessage.machine_id === machineId) {
      const ts = new Date(lastMessage.timestamp).toLocaleTimeString();
      const tr = lastMessage.twin_result;
      if (!tr) return;

      const newPoint = {
        timestamp: ts,
        divergence_score: tr.divergence_score,
        twin_anomaly: tr.twin_anomaly,
        residuals: tr.residuals,
        predicted: tr.predicted,
        actual: tr.actual,
        kalman_state: tr.kalman_state,
      };

      setHistory(prev => {
        const next = [...prev, newPoint];
        if (next.length > 30) next.shift(); // Keep last 30
        return next;
      });
    }
  }, [lastMessage, machineId]);

  // Format data for charts
  const chartData = useMemo(() => {
    return history.map(h => ({
      time: typeof h.timestamp === 'string' && h.timestamp.includes('T') 
            ? new Date(h.timestamp).toLocaleTimeString() 
            : h.timestamp,
      act_temp: h.actual?.engine_temperature,
      pred_temp: h.predicted?.engine_temperature,
      act_vib: h.actual?.vibration_level,
      pred_vib: h.predicted?.vibration_level,
      act_oil: h.actual?.oil_pressure,
      pred_oil: h.predicted?.oil_pressure,
      act_fuel: h.actual?.fuel_consumption,
      pred_fuel: h.predicted?.fuel_consumption,
    }));
  }, [history]);

  const latest = history[history.length - 1];
  const score = latest?.divergence_score || 0;
  
  const getScoreColor = (s: number) => {
    if (s >= 4.0) return "text-red-500";
    if (s >= 2.0) return "text-amber-500";
    return "text-emerald-500";
  };

  const getScoreStatus = (s: number) => {
    if (s >= 4.0) return "Critical Divergence";
    if (s >= 2.0) return "Divergence Warning";
    return "Twin Synchronized";
  };

  // Helper for sub-charts
  const renderChart = (title: string, actKey: string, predKey: string, color: string, Icon: any) => (
    <Card className="bg-background/40 backdrop-blur-sm border-zinc-800">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2 text-zinc-400">
          <Icon className="w-4 h-4" /> {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="h-[200px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
            <XAxis dataKey="time" stroke="#666" fontSize={10} tick={{fill: '#666'}} />
            <YAxis stroke="#666" fontSize={10} tick={{fill: '#666'}} domain={['auto', 'auto']} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', color: '#fff' }}
              itemStyle={{ color: '#fff' }}
            />
            <Legend wrapperStyle={{ fontSize: '12px' }} />
            <Line type="monotone" dataKey={actKey} name="Actual" stroke={color} strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey={predKey} name="Twin Predicted" stroke={color} strokeWidth={2} strokeDasharray="5 5" dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            Digital Twin — Live Divergence Monitor
          </h1>
          <p className="text-zinc-400">Comparing physical sensor readings against the twin's behavior model in real-time</p>
        </div>
        
        <div className="flex items-center gap-2 bg-zinc-900/50 p-1 rounded-lg border border-zinc-800">
          <Select value={machineId} onValueChange={setMachineId}>
            <SelectTrigger className="w-[180px] bg-transparent border-0 focus:ring-0">
              <SelectValue placeholder="Select Machine" />
            </SelectTrigger>
            <SelectContent>
              {["M-100", "M-101", "M-102", "M-103", "M-104"].map(id => (
                <SelectItem key={id} value={id}>{id}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Panel: Charts (Takes up 2/3) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {renderChart("Engine Temperature (°C)", "act_temp", "pred_temp", "#f87171", Thermometer)}
            {renderChart("Vibration Level", "act_vib", "pred_vib", "#fbbf24", Waves)}
            {renderChart("Oil Pressure (psi)", "act_oil", "pred_oil", "#60a5fa", Droplets)}
            {renderChart("Fuel Consumption (L/h)", "act_fuel", "pred_fuel", "#34d399", Zap)}
          </div>
        </div>

        {/* Right Panel: Gauge & Kalman State */}
        <div className="space-y-4">
          <Card className="bg-background/40 backdrop-blur-sm border-zinc-800">
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-zinc-400 font-medium">Twin Divergence Score</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center justify-center pt-4 pb-8">
              <div className="relative flex items-center justify-center w-48 h-48">
                {/* Simple CSS radial gauge approximation */}
                <div className={`absolute w-full h-full rounded-full border-8 border-t-transparent border-l-transparent ${score >= 4 ? 'border-red-500/50' : score >= 2 ? 'border-amber-500/50' : 'border-emerald-500/50'} rotate-45 transition-all duration-500`}></div>
                <div className={`absolute w-[90%] h-[90%] rounded-full border-4 border-b-transparent border-r-transparent ${score >= 4 ? 'border-red-400' : score >= 2 ? 'border-amber-400' : 'border-emerald-400'} -rotate-45 transition-all duration-500`}></div>
                
                <div className="flex flex-col items-center justify-center">
                  <span className={`text-5xl font-bold ${getScoreColor(score)}`}>
                    {score.toFixed(2)}
                  </span>
                  <span className="text-xs text-zinc-500 mt-1 uppercase tracking-wider">Score</span>
                </div>
              </div>
              <div className={`mt-6 text-lg font-semibold px-4 py-1 rounded-full bg-opacity-20 ${getScoreColor(score)} bg-current`}>
                {getScoreStatus(score)}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-background/40 backdrop-blur-sm border-zinc-800">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Activity className="w-4 h-4 text-emerald-400" />
                Estimated True State (Kalman Filtered)
              </CardTitle>
              <CardDescription>Smoothed robust state ignoring sensor noise</CardDescription>
            </CardHeader>
            <CardContent>
              {latest?.kalman_state ? (
                <div className="space-y-3">
                  {Object.entries(latest.kalman_state).map(([k, v]: [string, any]) => (
                    <div key={k} className="flex justify-between items-center bg-zinc-900/50 p-2 rounded">
                      <span className="text-sm text-zinc-400 capitalize">{k.replace('_', ' ')}</span>
                      <span className="font-mono text-emerald-400">{v?.toFixed(2) || '0.00'}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-zinc-500 text-sm py-4 text-center">Waiting for telemetry...</div>
              )}
            </CardContent>
          </Card>

          <Card className="bg-background/40 backdrop-blur-sm border-zinc-800">
            <CardHeader className="pb-3">
              <CardTitle className="text-base text-zinc-400">Current Residuals</CardTitle>
            </CardHeader>
            <CardContent>
              {latest?.residuals ? (
                <div className="space-y-2">
                  {Object.entries(latest.residuals).map(([k, v]: [string, any]) => (
                    <div key={k} className="flex justify-between text-sm">
                      <span className="text-zinc-500 capitalize">{k.replace('_', ' ')}</span>
                      <span className={`font-mono ${Math.abs(v) > (k==='engine_temperature'? 5 : 2) ? 'text-red-400' : 'text-zinc-300'}`}>
                        {v > 0 ? '+' : ''}{v?.toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-zinc-500 text-sm text-center">No residuals</div>
              )}
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  );
}
