"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { Lock, User } from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { login } from "@/hooks/use-api"

export default function LoginPage() {
  const router = useRouter()
  const [username, setUsername] = React.useState("")
  const [password, setPassword] = React.useState("")
  const [error, setError] = React.useState("")
  const [loading, setLoading] = React.useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      await login(username, password)
      router.push("/")
    } catch (err) {
      setError("Invalid username or password")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-zinc-950">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] bg-emerald-500/20 rounded-full blur-[120px] pointer-events-none"></div>
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md z-10 px-4"
      >
        <Card className="bg-zinc-900/60 backdrop-blur-2xl border-white/10 shadow-2xl">
          <CardHeader className="space-y-1 pb-8 text-center">
            <CardTitle className="text-3xl font-bold tracking-tight bg-gradient-to-r from-emerald-400 to-blue-500 bg-clip-text text-transparent">
              SustainTwin AI
            </CardTitle>
            <CardDescription className="text-zinc-400 font-medium">
              Authenticate to access fleet command
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-4">
                <div className="relative">
                  <User className="absolute left-3 top-3 h-5 w-5 text-zinc-500" />
                  <Input
                    placeholder="Username"
                    className="pl-10 bg-zinc-950/50 border-white/10 focus-visible:ring-emerald-500"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                  />
                </div>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-5 w-5 text-zinc-500" />
                  <Input
                    type="password"
                    placeholder="Password"
                    className="pl-10 bg-zinc-950/50 border-white/10 focus-visible:ring-emerald-500"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
              </div>

              {error && (
                <motion.p
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="text-sm font-medium text-red-500 text-center"
                >
                  {error}
                </motion.p>
              )}

              <Button
                type="submit"
                className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold transition-colors"
                disabled={loading}
              >
                {loading ? "Authenticating..." : "Sign In"}
              </Button>

              <div className="text-center text-xs text-zinc-500 pt-4">
                Demo accounts: engineer / admin (password: engineer123 / admin123)
              </div>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
