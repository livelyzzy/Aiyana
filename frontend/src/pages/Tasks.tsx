import { Button, Card, Form, Input, Modal, Space, Table, Tag, Typography, message } from 'antd'
import { useEffect, useState } from 'react'
import { createTask, listTasks } from '../api'
import { useAuth } from '../store/auth'
import type { TrainingTask } from '../types'

export default function Tasks() {
  const { user } = useAuth()
  const [tasks, setTasks] = useState<TrainingTask[]>([])
  const [open, setOpen] = useState(false)
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)

  const load = () => listTasks().then(setTasks)
  useEffect(() => {
    load()
  }, [])

  const onCreate = async () => {
    const values = await form.validateFields()
    setLoading(true)
    try {
      await createTask(values)
      message.success('任务已创建')
      setOpen(false)
      form.resetFields()
      load()
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    { title: '任务名称', dataIndex: 'title' },
    { title: '课程', dataIndex: 'course_name' },
    {
      title: '截止时间',
      dataIndex: 'deadline',
      render: (v: string | null) => (v ? new Date(v).toLocaleString() : '-'),
    },
    {
      title: '验收要求',
      dataIndex: 'requirements',
      ellipsis: true,
      render: (v: string) => (
        <Typography.Text type="secondary">{v || '-'}</Typography.Text>
      ),
    },
  ]

  return (
    <Card
      title="实训任务"
      extra={
        user?.role === 'teacher' && (
          <Button type="primary" onClick={() => setOpen(true)}>
            发布任务
          </Button>
        )
      }
    >
      <Table rowKey="id" dataSource={tasks} columns={columns} pagination={false} />

      <Modal
        title="发布实训任务"
        open={open}
        onOk={onCreate}
        onCancel={() => setOpen(false)}
        confirmLoading={loading}
        width={640}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="任务名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="course_name" label="课程名称" initialValue="软件实训">
            <Input />
          </Form.Item>
          <Form.Item name="description" label="任务说明">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="requirements" label="验收要求" rules={[{ required: true }]}>
            <Input.TextArea rows={4} placeholder="列出明确的验收标准，供 AI 核查比对" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
