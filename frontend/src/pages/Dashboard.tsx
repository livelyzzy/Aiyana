import { Card, Col, Row, Statistic, Typography } from 'antd'
import { useEffect, useState } from 'react'
import { listSubmissions, listTasks } from '../api'
import { useAuth } from '../store/auth'

export default function Dashboard() {
  const { user } = useAuth()
  const [taskCount, setTaskCount] = useState(0)
  const [submissionCount, setSubmissionCount] = useState(0)

  useEffect(() => {
    listTasks().then((t) => setTaskCount(t.length))
    listSubmissions().then((s) => setSubmissionCount(s.length))
  }, [])

  return (
    <div>
      <Typography.Title level={4}>欢迎，{user?.full_name}</Typography.Title>
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic title="实训任务数" value={taskCount} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="成果提交数" value={submissionCount} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="当前角色" value={user?.role === 'teacher' ? '教师' : '学生'} />
          </Card>
        </Col>
      </Row>
      <Card style={{ marginTop: 24 }}>
        <Typography.Title level={5}>功能导航</Typography.Title>
        <ul>
          <li>实训任务：教师发布任务与验收要求。</li>
          <li>成果上传：学生上传 Word / PDF / 图片等成果，系统自动解析。</li>
          <li>智能核查：AI 自动比对要求、识别逻辑漏洞与缺失步骤。</li>
          <li>报表导出：生成学生单份报告或班级统计（Excel / PDF，含图表）。</li>
        </ul>
      </Card>
    </div>
  )
}
