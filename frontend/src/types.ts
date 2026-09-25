export type StepType = 'script' | 'prompt' | 'http' | 'command'

export type RunStatus = 'pending' | 'running' | 'success' | 'failed' | 'cancelled'

export interface StepField {
  id: string
  label: string
  field_type?: string
  placeholder?: string
  default_value?: string
  required?: boolean
}

export interface StepOutput {
  label: string
  filename: string
  file_type?: string
  path?: string
}

export interface Step {
  id: string
  title: string
  type: StepType
  description?: string
  order: number
  dependsOn: string[]
  script?: string
  command?: string
  http_url?: string
  http_method?: string
  http_headers?: Record<string, string>
  prompt_template?: string
  fields?: StepField[]
  outputs?: StepOutput[]
  outputPath?: string
}

export interface Workflow {
  id: string
  name: string
  description?: string
  steps: Step[]
  created_at: string
  updated_at: string
}

export interface LogEntry {
  timestamp: string
  level: string
  message: string
  step_id?: string
}

export interface StepRun {
  step_id: string
  title: string
  status: RunStatus
  started_at?: string
  finished_at?: string
  exit_code?: number
  error_message?: string
  output_files?: string[]
}

export interface Run {
  id: string
  workflow_id: string
  status: RunStatus
  target_step_id?: string
  parameters: Record<string, any>
  step_runs: StepRun[]
  logs: LogEntry[]
  started_at: string
  finished_at?: string
  error_message?: string
}

export interface Schedule {
  id: string
  workflow_id: string
  cron_expression: string
  name: string
  enabled: boolean
  parameters: Record<string, any>
  last_run_at?: string
  created_at: string
}
