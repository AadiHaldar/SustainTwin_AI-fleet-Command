const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface LoginResponse {
  access_token: string
  token_type: string
  role: string
}

interface TelemetryReading {
  id: number
  machine_id: string
  timestamp: string
  sensor_data: Record<string, number>
  failure_risk: number
  is_anomaly: boolean
}

interface DiagnosisRecord {
  id: number
  machine_id: string
  timestamp: string
  severity: string
  root_cause: string | null
  confidence: number | null
  recommended_action: string | null
  urgency: string | null
  shap_values: Record<string, number> | null
  carbon_delta_kg: number
  sustainability_recommendation: string | null
}

interface MachineRecord {
  id: string
  machine_type: string
  status: string
}

function getToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem("sustaintwin_token")
}

function authHeaders(): HeadersInit {
  const token = getToken()
  const headers: HeadersInit = { "Content-Type": "application/json" }
  if (token) headers["Authorization"] = `Bearer ${token}`
  return headers
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const body = new URLSearchParams({ username, password })
  const res = await fetch(`${API_BASE}/api/v1/auth/token`, {
    method: "POST",
    body,
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  })
  if (!res.ok) throw new Error(`Login failed: ${res.status}`)
  const data: LoginResponse = await res.json()
  localStorage.setItem("sustaintwin_token", data.access_token)
  localStorage.setItem("sustaintwin_role", data.role)
  return data
}

export async function fetchTelemetry(): Promise<TelemetryReading[]> {
  const res = await fetch(`${API_BASE}/api/v1/telemetry`, {
    headers: authHeaders(),
  })
  if (!res.ok) return []
  return res.json()
}

export async function fetchMachineTelemetry(machineId: string): Promise<TelemetryReading[]> {
  const res = await fetch(`${API_BASE}/api/v1/telemetry/${machineId}`, {
    headers: authHeaders(),
  })
  if (!res.ok) return []
  return res.json()
}

export async function fetchDiagnostics(): Promise<DiagnosisRecord[]> {
  const res = await fetch(`${API_BASE}/api/v1/diagnostics`, {
    headers: authHeaders(),
  })
  if (!res.ok) return []
  return res.json()
}

export async function fetchMachineDiagnostics(machineId: string): Promise<DiagnosisRecord[]> {
  const res = await fetch(`${API_BASE}/api/v1/diagnostics/${machineId}`, {
    headers: authHeaders(),
  })
  if (!res.ok) return []
  return res.json()
}

export async function fetchHealthCheck(): Promise<{ status: string; database: string }> {
  const res = await fetch(`${API_BASE}/health/database`)
  if (!res.ok) return { status: "error", database: "unknown" }
  return res.json()
}

export interface FleetStats {
  total_machines: number
  active_anomalies_24h: number
  avg_confidence: number
  total_carbon_saved_kg: number
  anomaly_rate_percent: number
  fleet_health_score: number
}

export async function fetchStats(): Promise<FleetStats | null> {
  const res = await fetch(`${API_BASE}/api/v1/stats`, {
    headers: authHeaders(),
  })
  if (!res.ok) return null
  return res.json()
}

export async function fetchMachines(): Promise<MachineRecord[]> {
  // Extract machines from latest telemetry as a workaround if machines endpoint doesn't exist
  // Or if it does exist, we can use it. Since the audit mentioned no fetchMachines API call,
  // we can use fetchTelemetry to get the latest reading for each machine.
  const telemetry = await fetchTelemetry()
  return telemetry.map(t => ({
    id: t.machine_id,
    machine_type: "Unknown", // Or we can deduce from ID
    status: "Active"
  }))
}

export function useApi() {
  return {
    get: async (endpoint: string) => {
      const res = await fetch(`${API_BASE}/api/v1${endpoint}`, { headers: authHeaders() });
      if (!res.ok) throw new Error(`GET ${endpoint} failed`);
      return res.json();
    },
    post: async (endpoint: string, body: any) => {
      const res = await fetch(`${API_BASE}/api/v1${endpoint}`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`POST ${endpoint} failed`);
      return res.json();
    }
  }
}

export type { LoginResponse, TelemetryReading, DiagnosisRecord, MachineRecord }
