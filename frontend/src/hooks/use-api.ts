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

export type { LoginResponse, TelemetryReading, DiagnosisRecord, MachineRecord }
