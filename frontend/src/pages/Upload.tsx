import { InboxOutlined } from '@ant-design/icons'
import {
  Button,
  Card,
  Form,
  Input,
  Select,
  Table,
  Tag,
  Upload as AntUpload,
  message,
} from 'antd'
import type { UploadFile } from 'antd'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listSubmissions, listTasks, uploadSubmission } from '../api'
import type { Submission, TrainingTask } from '../types'

const statusMap: Record<string, { color: string; text: string }> = {
  uploaded: { color: 'default', text: '已上传' },
  parsing: { color: 'processing', text: '解析中' },
  parsed: { color: 'success', text: '已解析' },
  inspected: { color: 'geekblue', text: '已核查' },
  evaluated: { color: 'purple', text: '已评价' },
  failed: { color: 'error', text: '解析失败' },
}

export default function Upload() {
  const [tasks, setTasks] = useState<TrainingTask[]>([])
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [taskId, setTaskId] = useState<number>()
  const [groupName, setGroupName] = useState('')
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const load = () => listSubmissions(taskId).then(setSubmissions)

  useEffect(() => {
    listTasks().then(setTasks)
  }, [])

  useEffect(() => {
    load()
  }, [taskId])

  const onUpload = async () => {
    if (!taskId) return message.warning('请选择任务')
    if (!fileList.length) return message.warning('请选择文件')
    setLoading(true)
    try {
      const sub = await uploadSubmission(
        taskId,
        fileList.map((f) => (f.originFileObj ?? f) as File),
        groupName || undefined,
      )
      message.success('上传成功，正在解析')
      setFileList([])
      setGroupName('')
      load()
      navigate(`/submissions/${sub.id}`)
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 70 },
    { title: '文件', dataIndex: 'file_names', ellipsis: true },
    {
      title: '状态',
      dataIndex: 'status',
      render: (s: string) => {
        const m = statusMap[s] || { color: 'default', text: s }
        return <Tag color={m.color}>{m.text}</Tag>
      },
    },
    {
      title: '操作',
      render: (_: unknown, r: Submission) => (
        <Button type="link" onClick={() => navigate(`/submissions/${r.id}`)}>
          查看 / 核查评价
        </Button>
      ),
    },
  ]

  return (
    <Card title="成果上传">
      <Form layout="inline" style={{ marginBottom: 16 }}>
        <Form.Item label="任务">
          <Select
            style={{ width: 260 }}
            placeholder="选择实训任务"
            value={taskId}
            onChange={setTaskId}
            options={tasks.map((t) => ({ label: t.title, value: t.id }))}
          />
        </Form.Item>
        <Form.Item label="小组">
          <Input
            placeholder="可选"
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
            style={{ width: 160 }}
          />
        </Form.Item>
      </Form>

      <AntUpload.Dragger
        multiple
        beforeUpload={(file) => {
          setFileList((prev) => [...prev, file])
          return false
        }}
        onRemove={(file) => {
          setFileList((prev) => prev.filter((f) => f.uid !== file.uid))
        }}
        fileList={fileList}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p>点击或拖拽文件到此处上传（Word / PDF / 图片 / 代码）</p>
      </AntUpload.Dragger>

      <Button type="primary" onClick={onUpload} loading={loading} style={{ marginTop: 16 }}>
        提交成果
      </Button>

      <Table
        rowKey="id"
        style={{ marginTop: 24 }}
        dataSource={submissions}
        columns={columns}
        pagination={false}
      />
    </Card>
  )
}
