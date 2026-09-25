import React from 'react'
import { Play, Copy, Trash2, Code, Terminal, Globe, ChevronRight } from 'lucide-react'
import type { Workflow, Step } from '../types'

interface WorkflowCardProps {
  workflow: Workflow
  onTrigger: (wfId: string) => void
  onTriggerStep: (wfId: string, stepId: string) => void
  onDuplicate: (wfId: string) => void
  onDelete: (wfId: string) => void
  onViewDetails: (wf: Workflow) => void
}

export const WorkflowCard: React.FC<WorkflowCardProps> = ({
  workflow,
  onTrigger,
  onTriggerStep,
  onDuplicate,
  onDelete,
  onViewDetails,
}) => {
  const getStepIcon = (type: string) => {
    switch (type) {
      case 'script':
        return <Code className="w-3.5 h-3.5 text-cyan-400" />
      case 'command':
        return <Terminal className="w-3.5 h-3.5 text-amber-400" />
      case 'http':
        return <Globe className="w-3.5 h-3.5 text-emerald-400" />
      default:
        return <Code className="w-3.5 h-3.5 text-indigo-400" />
    }
  }

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all shadow-lg hover:shadow-indigo-500/5 flex flex-col justify-between">
      <div>
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="cursor-pointer" onClick={() => onViewDetails(workflow)}>
            <h3 className="font-bold text-lg text-white hover:text-indigo-400 transition-colors flex items-center gap-2">
              {workflow.name}
            </h3>
            <p className="text-sm text-slate-400 mt-1 line-clamp-2">
              {workflow.description || 'No description provided.'}
            </p>
          </div>
          <div className="flex items-center space-x-1">
            <button
              onClick={() => onDuplicate(workflow.id)}
              title="Duplicate"
              className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
            >
              <Copy className="w-4 h-4" />
            </button>
            <button
              onClick={() => onDelete(workflow.id)}
              title="Delete"
              className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-950/40 rounded-lg transition-colors"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Steps pipeline preview */}
        <div className="my-4">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
            Execution Steps ({workflow.steps?.length || 0})
          </div>
          <div className="space-y-1.5">
            {workflow.steps?.map((step: Step, idx: number) => (
              <div
                key={step.id}
                className="flex items-center justify-between px-3 py-2 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs"
              >
                <div className="flex items-center space-x-2.5 truncate">
                  <span className="w-5 h-5 rounded-md bg-slate-800 flex items-center justify-center font-mono text-[10px] text-slate-400">
                    {idx + 1}
                  </span>
                  {getStepIcon(step.type)}
                  <span className="font-medium text-slate-300 truncate">{step.title}</span>
                </div>
                <button
                  onClick={() => onTriggerStep(workflow.id, step.id)}
                  className="text-[11px] px-2 py-0.5 rounded-md bg-slate-800 hover:bg-indigo-600/80 text-slate-300 hover:text-white transition-colors"
                >
                  Run Step
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between">
        <button
          onClick={() => onViewDetails(workflow)}
          className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium transition-colors"
        >
          View Details <ChevronRight className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={() => onTrigger(workflow.id)}
          className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>Execute All</span>
        </button>
      </div>
    </div>
  )
}
