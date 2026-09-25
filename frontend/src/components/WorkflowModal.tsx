import React, { useState } from 'react'
import { Plus, Trash2, X } from 'lucide-react'
import type { Step, Workflow } from '../types'

interface WorkflowModalProps {
  workflow?: Workflow | null
  onClose: () => void
  onSave: (wf: Partial<Workflow>) => void
}

export const WorkflowModal: React.FC<WorkflowModalProps> = ({ workflow, onClose, onSave }) => {
  const [name, setName] = useState(workflow?.name || '')
  const [description, setDescription] = useState(workflow?.description || '')
  const [steps, setSteps] = useState<Step[]>(() => {
    if (workflow?.steps && workflow.steps.length > 0) {
      return workflow.steps
    }
    return [
      {
        id: 'step-init',
        title: 'New Step',
        type: 'script',
        order: 1,
        dependsOn: [],
        script: '#!/usr/bin/env python3\nprint("Executing Step...")',
      },
    ]
  })

  const handleAddStep = () => {
    const newStep: Step = {
      id: `step-${steps.length + 1}`,
      title: `Step ${steps.length + 1}`,
      type: 'script',
      order: steps.length + 1,
      dependsOn: steps.length > 0 ? [steps[steps.length - 1].id] : [],
      script: '#!/usr/bin/env python3\nprint("Hello World")',
    }
    setSteps([...steps, newStep])
  }

  const handleRemoveStep = (index: number) => {
    setSteps(steps.filter((_, idx) => idx !== index))
  }

  const handleUpdateStep = (index: number, updates: Partial<Step>) => {
    setSteps(
      steps.map((s, idx) => {
        if (idx === index) {
          return { ...s, ...updates }
        }
        return s
      })
    )
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    onSave({
      id: workflow?.id,
      name,
      description,
      steps,
    })
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-2xl w-full max-h-[90vh] flex flex-col shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <h3 className="text-lg font-bold text-white">
            {workflow ? 'Edit Workflow' : 'Create New Workflow'}
          </h3>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto py-4 space-y-4 pr-1">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Workflow Name</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. RSS Article Collector"
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Description</label>
            <textarea
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the objective and behavior of this workflow..."
              className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-semibold text-slate-300">Execution Steps ({steps.length})</label>
              <button
                type="button"
                onClick={handleAddStep}
                className="flex items-center space-x-1 text-xs text-indigo-400 hover:text-indigo-300 font-medium"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Step</span>
              </button>
            </div>

            <div className="space-y-3">
              {steps.map((step, idx) => (
                <div key={step.id} className="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800/80 space-y-2.5">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center space-x-2 flex-1">
                      <span className="w-5 h-5 rounded-md bg-slate-800 text-slate-400 font-mono text-[10px] flex items-center justify-center">
                        {idx + 1}
                      </span>
                      <input
                        type="text"
                        value={step.title}
                        onChange={(e) => handleUpdateStep(idx, { title: e.target.value })}
                        className="bg-transparent border-b border-slate-700 text-xs font-medium text-white px-1 py-0.5 outline-none flex-1"
                      />
                    </div>
                    <select
                      value={step.type}
                      onChange={(e) => handleUpdateStep(idx, { type: e.target.value as any })}
                      className="bg-slate-900 border border-slate-800 rounded-lg text-[11px] text-slate-300 px-2 py-1 outline-none"
                    >
                      <option value="script">Python Script</option>
                      <option value="command">Shell Command</option>
                      <option value="http">HTTP Request</option>
                    </select>
                    {steps.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveStep(idx)}
                        className="p-1 text-slate-500 hover:text-rose-400"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>

                  {step.type === 'script' && (
                    <div>
                      <textarea
                        rows={4}
                        value={step.script || ''}
                        onChange={(e) => handleUpdateStep(idx, { script: e.target.value })}
                        placeholder="#!/usr/bin/env python3"
                        className="w-full font-mono text-xs px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 outline-none"
                      />
                    </div>
                  )}

                  {step.type === 'command' && (
                    <div>
                      <input
                        type="text"
                        value={step.command || ''}
                        onChange={(e) => handleUpdateStep(idx, { command: e.target.value })}
                        placeholder="e.g. curl -sS https://example.com"
                        className="w-full font-mono text-xs px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 outline-none"
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end space-x-2 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30"
            >
              Save Workflow
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
