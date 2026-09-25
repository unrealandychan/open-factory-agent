import React, { useState, useEffect } from 'react'
import { Calendar, Plus, Trash2, Power, Clock } from 'lucide-react'
import type { Schedule, Workflow } from '../types'
import { api } from '../api'

interface ScheduleListProps {
  workflows: Workflow[]
}

export const ScheduleList: React.FC<ScheduleListProps> = ({ workflows }) => {
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [showModal, setShowModal] = useState(false)
  const [selectedWorkflow, setSelectedWorkflow] = useState('')
  const [cronExpr, setCronExpr] = useState('0 9 * * *')
  const [scheduleName, setScheduleName] = useState('')

  const loadSchedules = async () => {
    const data = await api.listSchedules()
    setSchedules(data)
  }

  useEffect(() => {
    let ignore = false
    api.listSchedules().then((data) => {
      if (!ignore) setSchedules(data)
    })
    return () => {
      ignore = true
    }
  }, [])

  const handleToggle = async (id: string, currentState: boolean) => {
    await api.toggleSchedule(id, !currentState)
    loadSchedules()
  }

  const handleDelete = async (id: string) => {
    await api.deleteSchedule(id)
    loadSchedules()
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedWorkflow || !cronExpr) return
    await api.createSchedule(selectedWorkflow, cronExpr, scheduleName)
    setShowModal(false)
    setSelectedWorkflow('')
    setScheduleName('')
    loadSchedules()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Calendar className="w-5 h-5 text-indigo-400" />
            Automated Schedules
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Trigger recurring workflows with flexible cron expressions.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>New Schedule</span>
        </button>
      </div>

      {schedules.length === 0 ? (
        <div className="text-center py-16 bg-slate-900/50 border border-slate-800/80 rounded-2xl">
          <Clock className="w-10 h-10 text-slate-600 mx-auto mb-2" />
          <p className="text-sm text-slate-400">No schedules configured.</p>
          <p className="text-xs text-slate-500 mt-1">Create a schedule to automate your workflow runs.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {schedules.map((s) => (
            <div
              key={s.id}
              className={`p-5 rounded-2xl border transition-all ${
                s.enabled
                  ? 'bg-slate-900/90 border-slate-800 hover:border-slate-700'
                  : 'bg-slate-950/60 border-slate-900 opacity-60'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-semibold text-white text-sm">{s.name || s.workflow_id}</h4>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="font-mono text-xs px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                      {s.cron_expression}
                    </span>
                    <span className="text-[11px] text-slate-400">Target: {s.workflow_id}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => handleToggle(s.id, s.enabled)}
                    className={`p-1.5 rounded-lg transition-colors ${
                      s.enabled ? 'text-emerald-400 hover:bg-emerald-950/40' : 'text-slate-500 hover:bg-slate-800'
                    }`}
                    title={s.enabled ? 'Disable' : 'Enable'}
                  >
                    <Power className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(s.id)}
                    className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-950/40 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              {s.last_run_at && (
                <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] text-slate-500">
                  Last run: {new Date(s.last_run_at).toLocaleString()}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* New Schedule Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-4">Create Cron Schedule</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Target Workflow</label>
                <select
                  value={selectedWorkflow}
                  onChange={(e) => setSelectedWorkflow(e.target.value)}
                  required
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs focus:ring-1 focus:ring-indigo-500 outline-none"
                >
                  <option value="">Select a workflow...</option>
                  {workflows.map((wf) => (
                    <option key={wf.id} value={wf.id}>
                      {wf.name} ({wf.id})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Schedule Name</label>
                <input
                  type="text"
                  placeholder="e.g. Daily Morning Digest"
                  value={scheduleName}
                  onChange={(e) => setScheduleName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs focus:ring-1 focus:ring-indigo-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Cron Expression</label>
                <input
                  type="text"
                  required
                  value={cronExpr}
                  onChange={(e) => setCronExpr(e.target.value)}
                  placeholder="0 9 * * *"
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 font-mono text-white text-xs focus:ring-1 focus:ring-indigo-500 outline-none"
                />
                <p className="text-[10px] text-slate-500 mt-1">Example: `0 9 * * *` (Every day at 9:00 AM)</p>
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                >
                  Save Schedule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
