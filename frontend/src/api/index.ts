import { client } from './client'
import type {
  EvaluationResult,
  InspectionResult,
  Rubric,
  Score,
  Submission,
  TrainingTask,
  User,
} from '../types'

// ---- 认证 ----
export const login = (username: string, password: string) =>
  client
    .post<{ access_token: string }>('/auth/login', new URLSearchParams({ username, password }))
    .then((r) => r.data)

export const getMe = () => client.get<User>('/users/me').then((r) => r.data)

// ---- 用户 ----
export const listUsers = () => client.get<User[]>('/users').then((r) => r.data)
export const createUser = (data: Partial<User> & { password: string }) =>
  client.post<User>('/users', data).then((r) => r.data)

// ---- 实训任务 ----
export const listTasks = () => client.get<TrainingTask[]>('/tasks').then((r) => r.data)
export const createTask = (data: Partial<TrainingTask>) =>
  client.post<TrainingTask>('/tasks', data).then((r) => r.data)

// ---- 实训成果 ----
export const uploadSubmission = (taskId: number, files: File[], groupName?: string) => {
  const form = new FormData()
  form.append('task_id', String(taskId))
  if (groupName) form.append('group_name', groupName)
  files.forEach((f) => form.append('files', f))
  return client.post<Submission>('/submissions', form).then((r) => r.data)
}
export const listSubmissions = (taskId?: number) =>
  client.get<Submission[]>('/submissions', { params: { task_id: taskId } }).then((r) => r.data)
export const getSubmission = (id: number) =>
  client.get<Submission>(`/submissions/${id}`).then((r) => r.data)
export const reparseSubmission = (id: number) =>
  client.post<Submission>(`/submissions/${id}/parse`).then((r) => r.data)

// ---- 智能核查 ----
export const inspectSubmission = (id: number) =>
  client.post<InspectionResult>(`/submissions/${id}/inspect`).then((r) => r.data)
export const getInspection = (id: number) =>
  client.get<InspectionResult>(`/submissions/${id}/inspection`).then((r) => r.data)

// ---- 评价 ----
export const listRubrics = (taskId?: number) =>
  client.get<Rubric[]>('/rubrics', { params: { task_id: taskId } }).then((r) => r.data)
export const createRubric = (data: Partial<Rubric>) =>
  client.post<Rubric>('/rubrics', data).then((r) => r.data)
export const deleteRubric = (id: number) => client.delete(`/rubrics/${id}`)
export const evaluateSubmission = (id: number) =>
  client.post<EvaluationResult>(`/submissions/${id}/evaluate`).then((r) => r.data)
export const listScores = (id: number) =>
  client.get<Score[]>(`/submissions/${id}/scores`).then((r) => r.data)
export const adjustScore = (scoreId: number, data: { teacher_score?: number; comment?: string }) =>
  client.put<Score>(`/scores/${scoreId}`, data).then((r) => r.data)

// ---- 报表 ----
export const exportReport = (data: { submission_id?: number; task_id?: number; format: 'xlsx' | 'pdf' }) =>
  client.post('/reports/export', data, { responseType: 'blob' }).then((r) => r.data)
export const listReports = () =>
  client.get<{ id: number; report_type: string; target: string; format: string; file_path: string }[]>(
    '/reports',
  ).then((r) => r.data)
