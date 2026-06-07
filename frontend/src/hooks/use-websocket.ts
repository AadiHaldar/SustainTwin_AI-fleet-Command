"use client"

import { useEffect, useRef, useState, useCallback } from "react"

export type ConnectionStatus = "connecting" | "connected" | "disconnected"

interface UseWebSocketOptions {
  url: string
  onMessage?: (data: unknown) => void
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

export function useWebSocket({
  url,
  onMessage,
  reconnectInterval = 3000,
  maxReconnectAttempts = 10,
}: UseWebSocketOptions) {
  const [status, setStatus] = useState<ConnectionStatus>("disconnected")
  const [lastMessage, setLastMessage] = useState<unknown>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectCountRef = useRef(0)
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    setStatus("connecting")
    const ws = new WebSocket(url)

    ws.onopen = () => {
      setStatus("connected")
      reconnectCountRef.current = 0
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setLastMessage(data)
        onMessage?.(data)
      } catch {
        setLastMessage(event.data)
      }
    }

    ws.onclose = () => {
      setStatus("disconnected")
      wsRef.current = null

      if (reconnectCountRef.current < maxReconnectAttempts) {
        reconnectCountRef.current += 1
        const delay = reconnectInterval * Math.min(reconnectCountRef.current, 5)
        reconnectTimerRef.current = setTimeout(connect, delay)
      }
    }

    ws.onerror = () => {
      ws.close()
    }

    wsRef.current = ws
  }, [url, onMessage, reconnectInterval, maxReconnectAttempts])

  useEffect(() => {
    connect()
    return () => {
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current)
      wsRef.current?.close()
    }
  }, [connect])

  return { status, lastMessage }
}
