import React, { useEffect, useRef, useState } from 'react'
import { AlertCircle, CheckCircle2, Clock, Loader2, Square, Terminal, XCircle } from 'lucide-react'
import type { LogEntry, Run, RunStatus } from '../types'
import { api } from '../api'

interface RunMonitorProps {
  runId: string | null
  onBack: () => void
}

export const RunMonitor: React.FC<RunMonitorProps> = ({ runId, onBack }) => {
  const [run, setRun] = useState<Run | null>(null)
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [autoScroll, setAutoScroll] = useState<boolean>(true)
  const logContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!runId) return

    let isMounted = true
    let sse: EventSource | null = null

    const fetchRunData = async () => {
      const data = await api.getRun(runId)
      if (data && isMounted) {
        setRun(data)
        setLogs(data.logs || [])
      }
    }

    fetchRunData()

    // Try connecting to SSE live streaming
    try {
      sse = new EventSource(`/api/v1/runs/${runId}/stream`)
      sse.addEventListener('log', (e) => {
        try {
          const entry = JSON.parse(e.data)
          if (isMounted) setLogs((prev) => [...prev, entry])
        } catch {}
      })
      sse.addEventListener('step_status', () => {
        fetchRunData()
      })
      sse.addEventListener('status', (e) => {
        try {
          const updated = JSON.parse(e.data)
          if (isMounted && updated) setRun(updated)
        } catch {}
      })
    } catch {
      // Polling fallback
      const interval = setInterval(fetchRunData, 2000)
      return () => clearInterval(interval)
    }

    return () => {
      isMounted = false
      if (sse) sse.close()
    }
  }, [runId])

  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  const handleCancel = async () => {
    if (!runId) return
    await api.cancelRun(runId)
    const updated = await api.getRun(runId)
    if (updated) setRun(updated)
  }

  const getStatusBadge = (status: RunStatus) => {
    switch (status) {
      case 'running':
        return (
          <span className="flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-950 text-cyan-400 border border-cyan-800 animate-pulse">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            <span>RUNNING</span>
          </span>
        )
      case 'success':
        return (
          <span className="flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>SUCCESS</span>
          </span>
        )
      case 'failed':
        return (
          <span className="flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-950 text-rose-400 border border-rose-800">
            <XCircle className="w-3.5 h-3.5" />
            <span>FAILED</span>
          </span>
        )
      case 'cancelled':
        return (
          <span className="flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-950 text-amber-400 border border-amber-800">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>CANCELLED</span>
          </span>
        )
      default:
        return (
          <span className="flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-400">
            <Clock className="w-3.5 h-3.5" />
            <span>PENDING</span>
          </span>
        )
    }
  }

  if (!runId) {
    return (
      <div className="text-center py-20 bg-slate-900/50 border border-slate-800/80 rounded-2xl">
        <Terminal className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <h4 className="text-lg font-medium text-slate-300">No Run Selected</h4>
        <p className="text-sm text-slate-500 mt-1">Select an active run or execute a workflow to view live logs.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Run Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h2 className="text-xl font-bold text-white font-mono">{runId}</h2>
            {run && getStatusBadge(run.status)}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Target Workflow: <span className="font-mono text-indigo-400">{run?.workflow_id}</span>
            {run?.started_at && ` • Started: ${new Date(run.started_at).toLocaleTimeString()}`}
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {run?.status === 'running' && (
            <button
              onClick={handleCancel}
              className="flex items-center space-x-2 px-3 py-2 rounded-xl bg-rose-600/80 hover:bg-rose-600 text-white text-xs font-semibold shadow-md transition-colors"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
              <span>Cancel Run</span>
            </button>
          )}
          <button
            onClick={onBack}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-colors"
          >
            Back to List
          </button>
        </div>
      </div>

      {/* Steps Pipeline Status */}
      {run?.step_runs && run.step_runs.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          {run.step_runs.map((sr, idx) => (
            <div
              key={sr.step_id}
              className="bg-slate-900/90 border border-slate-800/80 rounded-xl p-3.5 flex items-center justify-between"
            >
              <div className="truncate mr-2">
                <div className="text-[10px] text-slate-500 font-mono">Step {idx + 1}</div>
                <div className="text-xs font-semibold text-slate-200 truncate">{sr.title}</div>
              </div>
              {getStatusBadge(sr.status)}
            </div>
          ))}
        </div>
      )}

      {/* Live Console Output */}
      <div className="bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
        <div className="bg-slate-900/90 px-4 py-3 border-b border-slate-800 flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2 text-slate-400 font-mono">
            <Terminal className="w-4 h-4 text-indigo-400" />
            <span>Terminal Output ({logs.length} lines)</span>
          </div>
          <label className="flex items-center space-x-2 cursor-pointer text-slate-400 hover:text-slate-200">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-0"
            />
            <span className="text-[11px]">Auto-scroll</span>
          </label>
        </div>

        <div
          ref={logContainerRef}
          className="p-4 h-[420px] overflow-y-auto font-mono text-xs space-y-1 bg-black/40 text-slate-300"
        >
          {logs.length === 0 ? (
            <div className="text-slate-600 italic py-6 text-center">Waiting for output logs...</div>
          ) : (
            logs.map((log, idx) => (
              <div key={idx} className="flex items-start space-x-2 leading-relaxed">
                <span className="text-slate-600 text-[10px] select-none shrink-0 font-mono">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <span
                  className={`px-1 py-0.2 rounded text-[10px] font-bold shrink-0 ${
                    log.level === 'ERROR'
                      ? 'bg-rose-950/80 text-rose-400'
                      : log.level === 'WARN'
                      ? 'bg-amber-950/80 text-amber-400'
                      : 'bg-indigo-950/80 text-indigo-300'
                  }`}
                >
                  {log.level}
                </span>
                <span className="break-all text-slate-200">{log.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
