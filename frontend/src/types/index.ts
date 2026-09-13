export interface User {
  id: number
  username: string
  full_name: string
  role: 'teacher' | 'student'
  email?: string | null
}

export interface TrainingTask {
  id: number
  title: string
  course_name: string
  description: string
  requirements: string
  teacher_id: number
  deadline?: string | null
  created_at: string
}

export interface Submission {
  id: number
  task_id: number
  student_id: number
  group_name?: string | null
  status: string
  file_names: string
  parsed_content?: string | null
  parse_error?: string | null
  created_at: string
}

export interface Rubric {
  id: number
  task_id?: number | null
  name: string
  description: string
  weight: number
}

export interface Score {
  id: number
  submission_id: number
  rubric_id: number
  ai_score?: number | null
  teacher_score?: number | null
  comment?: string | null
}

export interface InspectionResult {
  deviations: { item: string; issue: string; severity: string }[]
  logic_issues: { issue: string; reason: string }[]
  missing_steps: { step: string; reason: string }[]
  overall: string
}

export interface EvaluationResult {
  submission_id: number
  total_score: number
  items: Score[]
}
