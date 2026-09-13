import { Button, Card, Col, Form, Radio, Row, Select, Table, Tag, message } from 'antd'
import { useEffect, useState } from 'react'
import { exportReport, listReports, listSubmissions, listTasks } from '../api'
import type { Submission, TrainingTask } from '../types'

function download(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

type ReportType = 'student' | 'class'

export default function Reports() {
  const [tasks, setTasks] = useState<TrainingTask[]>([])
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [history, setHistory] = useState<any[]>([])
  const [reportType, setReportType] = useState<ReportType>('class')
  const [taskId, setTaskId] = useState<number>()
  const [submissionId, setSubmissionId] = useState<number>()
  const [format, setFormat] = useState<'xlsx' | 'pdf'>('xlsx')
  const [loading, setLoading] = useState(false)

  const loadHistory = () => listReports().then(setHistory)

  useEffect(() => {
    listTasks().then(setTasks)
    loadHistory()
  }, [])

  useEffect(() => {
    if (taskId) listSubmissions(taskId).then(setSubmissions)
    else setSubmissions([])
  }, [taskId])

  const doExport = async () => {
    if (reportType === 'student' && submissionId == null) return message.warning('请选择学生成果')
    if (reportType === 'class' && taskId == null) return message.warning('请选择任务')
    setLoading(true)
    try {
      const payload =
        reportType === 'student'
          ? { submission_id: submissionId!, format }
          : { task_id: taskId!, format }
      const blob = await exportReport(payload)
      download(blob, `report_${Date.now()}.${format}`)
      message.success('报表已导出')
      loadHistory()
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    {
      title: '类型',
      dataIndex: 'report_type',
      render: (v: string) => (v === 'student' ? '学生报告' : '班级统计'),
    },
    { title: '对象', dataIndex: 'target' },
    { title: '格式', dataIndex: 'format', render: (v: string) => <Tag>{v.toUpperCase()}</Tag> },
    { title: '文件名', dataIndex: 'file_path' },
  ]

  return (
    <Row gutter={16}>
      <Col span={10}>
        <Card title="导出报表">
          <Form layout="vertical">
            <Form.Item label="报告类型">
              <Radio.Group
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                options={[
                  { label: '课程班级统计', value: 'class' },
                  { label: '学生单份报告', value: 'student' },
                ]}
              />
            </Form.Item>
            <Form.Item label="选择任务">
              <Select
                placeholder="选择实训任务"
                value={taskId}
                onChange={setTaskId}
                allowClear
                options={tasks.map((t) => ({ label: t.title, value: t.id }))}
              />
            </Form.Item>
            {reportType === 'student' && (
              <Form.Item label="选择学生成果">
                <Select
                  placeholder="选择具体成果"
                  value={submissionId}
                  onChange={setSubmissionId}
                  options={submissions.map((s) => ({
                    label: `#${s.id} ${s.file_names}`,
                    value: s.id,
                  }))}
                />
              </Form.Item>
            )}
            <Form.Item label="导出格式">
              <Radio.Group
                value={format}
                onChange={(e) => setFormat(e.target.value)}
                options={[
                  { label: 'Excel', value: 'xlsx' },
                  { label: 'PDF', value: 'pdf' },
                ]}
              />
            </Form.Item>
            <Button type="primary" onClick={doExport} loading={loading}>
              生成并下载
            </Button>
          </Form>
        </Card>
      </Col>
      <Col span={14}>
        <Card title="导出历史">
          <Table rowKey="id" dataSource={history} columns={columns} pagination={false} />
        </Card>
      </Col>
    </Row>
  )
}
