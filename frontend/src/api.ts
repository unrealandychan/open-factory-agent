import type { Run, Schedule, Workflow } from './types'

const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1'

const FALLBACK_WORKFLOWS: Workflow[] = [
  {
    id: 'workflow-news-digest',
    name: 'AI Tech News Digest Agent',
    description: 'Scrapes RSS feeds, generates intelligent summaries, and formats daily briefs.',
    steps: [
      {
        id: 'step-fetch',
        title: 'Fetch Tech Feeds',
        type: 'script',
        order: 1,
        dependsOn: [],
        script: '#!/usr/bin/env python3\nprint("Fetching RSS feeds...")',
        outputPath: 'outputs/news/fetch_result.json',
      },
      {
        id: 'step-summarize',
        title: 'AI Synthesis & Markdown',
        type: 'script',
        order: 2,
        dependsOn: ['step-fetch'],
        script: '#!/usr/bin/env python3\nprint("Synthesizing articles...")',
        outputPath: 'outputs/news/digest.md',
      },
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'workflow-video-pipeline',
    name: 'Shorts Video Automation Pipeline',
    description: 'Generates short-form video scripts, synthesizes voiceovers, and renders output with ffmpeg.',
    steps: [
      {
        id: 'step-script',
        title: 'Draft Script Prompt',
        type: 'prompt',
        order: 1,
        dependsOn: [],
        prompt_template: 'Write a 60-second engaging script about AI.',
      },
      {
        id: 'step-render',
        title: 'FFmpeg Stitch & Render',
        type: 'command',
        order: 2,
        dependsOn: ['step-script'],
        command: 'ffmpeg -f lavfi -i color=c=blue:s=1080x1920:d=5 -vf "drawtext=text=\'AgentForge\':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2" ${OUT}/preview.mp4',
      },
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

export const api = {
  async listWorkflows(): Promise<Workflow[]> {
    try {
      const res = await fetch(`${API_BASE}/workflows`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      return data.workflows || []
    } catch {
      // Fallback for standalone demo / GitHub Pages
      return FALLBACK_WORKFLOWS
    }
  },

  async createWorkflow(payload: Partial<Workflow>): Promise<Workflow> {
    const res = await fetch(`${API_BASE}/workflows`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) throw new Error(`Failed to create workflow: ${res.statusText}`)
    return res.json()
  },

  async deleteWorkflow(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/workflows/${id}`, { method: 'DELETE' })
    if (!res.ok && res.status !== 404) throw new Error(`Failed to delete workflow`)
  },

  async triggerRun(workflowId: string, targetStepId?: string, parameters: Record<string, any> = {}): Promise<Run> {
    try {
      const res = await fetch(`${API_BASE}/runs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow_id: workflowId,
          target_step_id: targetStepId,
          parameters,
        }),
      })
      if (!res.ok) throw new Error(`Trigger failed: ${res.statusText}`)
      return res.json()
    } catch {
      // Mock run for static GitHub Pages preview
      return {
        id: `mock-run-${Date.now().toString(36)}`,
        workflow_id: workflowId,
        status: 'running',
        parameters,
        step_runs: [
          { step_id: 'step-1', title: 'Running preview task', status: 'running', started_at: new Date().toISOString() },
        ],
        logs: [
          { timestamp: new Date().toISOString(), level: 'INFO', message: `Triggered workflow ${workflowId} in demo mode.` },
          { timestamp: new Date().toISOString(), level: 'INFO', message: 'Step completed successfully.' },
        ],
        started_at: new Date().toISOString(),
      }
    }
  },

  async listRuns(): Promise<Run[]> {
    try {
      const res = await fetch(`${API_BASE}/runs`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      return data.runs || []
    } catch {
      return []
    }
  },

  async getRun(runId: string): Promise<Run | null> {
    try {
      const res = await fetch(`${API_BASE}/runs/${runId}`)
      if (!res.ok) return null
      return res.json()
    } catch {
      return null
    }
  },

  async cancelRun(runId: string): Promise<void> {
    await fetch(`${API_BASE}/runs/${runId}/cancel`, { method: 'POST' })
  },

  async listSchedules(): Promise<Schedule[]> {
    try {
      const res = await fetch(`${API_BASE}/schedules`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      return data.schedules || []
    } catch {
      return []
    }
  },

  async createSchedule(workflowId: string, cronExpr: string, name: string): Promise<Schedule> {
    const res = await fetch(`${API_BASE}/schedules`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        workflow_id: workflowId,
        cron_expression: cronExpr,
        name,
      }),
    })
    return res.json()
  },

  async toggleSchedule(scheduleId: string, enabled: boolean): Promise<Schedule> {
    const res = await fetch(`${API_BASE}/schedules/${scheduleId}/toggle?enabled=${enabled}`, {
      method: 'PATCH',
    })
    return res.json()
  },

  async deleteSchedule(scheduleId: string): Promise<void> {
    await fetch(`${API_BASE}/schedules/${scheduleId}`, { method: 'DELETE' })
  },
}
