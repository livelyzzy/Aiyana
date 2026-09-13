import {
  Button,
  Card,
  Col,
  Descriptions,
  Empty,
  InputNumber,
  List,
  Row,
  Space,
  Table,
  Tabs,
  Tag,
  Typography,
  message,
} from 'antd'
import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import type { EChartsOption } from 'echarts'
import {
  adjustScore,
  evaluateSubmission,
  getInspection,
  getSubmission,
  inspectSubmission,
  listRubrics,
  listScores,
} from '../api'
import Chart from '../components/Chart'
import { useAuth } from '../store/auth'
import type { InspectionResult, Rubric, Score, Submission } from '../types'

export default function SubmissionDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const [submission, setSubmission] = useState<Submission | null>(null)
  const [inspection, setInspection] = useState<InspectionResult | null>(null)
  const [rubrics, setRubrics] = useState<Rubric[]>([])
  const [scores, setScores] = useState<Score[]>([])
  const [inspecting, setInspecting] = useState(false)
  const [evaluating, setEvaluating] = useState(false)

  const load = async () => {
    if (!id) return
    const sid = Number(id)
    const [sub, rub] = await Promise.all([getSubmission(sid), listRubrics()])
    setSubmission(sub)
    setRubrics(rub)
    getInspection(sid).then(setInspection).catch(() => {})
    listScores(sid).then(setScores).catch(() => {})
  }

  useEffect(() => {
    load()
  }, [id])

  const parsed = useMemo(() => {
    try {
      return submission?.parsed_content ? JSON.parse(submission.parsed_content) : null
    } catch {
      return null
    }
  }, [submission])

  const onInspect = async () => {
    setInspecting(true)
    try {
      setInspection(await inspectSubmission(Number(id)))
      message.success('核查完成')
    } finally {
      setInspecting(false)
    }
  }

  const onEvaluate = async () => {
    setEvaluating(true)
    try {
      await evaluateSubmission(Number(id))
      setScores(await listScores(Number(id)))
      message.success('AI 评分完成')
    } finally {
      setEvaluating(false)
    }
  }

  const onAdjust = async (scoreId: number, value: number | null) => {
    await adjustScore(scoreId, { teacher_score: value ?? undefined })
    setScores(await listScores(Number(id)))
    message.success('已保存教师评分')
  }

  const radarOption = useMemo<EChartsOption>(() => {
    const nameMap = Object.fromEntries(rubrics.map((r) => [r.id, r.name]))
    return {
      radar: {
        indicator: scores.map((s) => ({ name: nameMap[s.rubric_id] || `指标${s.rubric_id}`, max: 100 })),
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              name: '评分',
              value: scores.map((s) =>
                s.teacher_score ?? s.ai_score ?? 0,
              ),
            },
          ],
        },
      ],
    }
  }, [scores, rubrics])

  const scoreColumns = [
    { title: '指标', dataIndex: 'rubric_id', render: (v: number) => rubrics.find((r) => r.id === v)?.name || v },
    { title: 'AI 评分', dataIndex: 'ai_score', render: (v: number | null) => (v == null ? '-' : v) },
    {
      title: '教师评分',
      dataIndex: 'teacher_score',
      render: (v: number | null, r: Score) =>
        user?.role === 'teacher' ? (
          <InputNumber
            min={0}
            max={100}
            value={v ?? undefined}
            onChange={(val) => onAdjust(r.id, val)}
            size="small"
            style={{ width: 100 }}
          />
        ) : v == null ? '-' : v,
    },
    { title: '评语', dataIndex: 'comment', ellipsis: true },
  ]

  const renderInspection = () => {
    if (!inspection) {
      return (
        <Empty description="尚未核查">
          <Button type="primary" loading={inspecting} onClick={onInspect}>
            开始智能核查
          </Button>
        </Empty>
      )
    }
    return (
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Card size="small" title="总体结论">
          {inspection.overall || '—'}
        </Card>
        <Row gutter={16}>
          <Col span={8}>
            <Card size="small" title="偏离项">
              <List
                dataSource={inspection.deviations}
                renderItem={(d) => (
                  <List.Item>
                    <Space direction="vertical" size={0}>
                      <b>{d.item}</b>
                      <Typography.Text type="secondary">{d.issue}</Typography.Text>
                      <Tag color={d.severity === '高' ? 'red' : d.severity === '中' ? 'orange' : 'blue'}>
                        {d.severity}
                      </Tag>
                    </Space>
                  </List.Item>
                )}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small" title="逻辑漏洞">
              <List
                dataSource={inspection.logic_issues}
                renderItem={(d) => (
                  <List.Item>
                    <Space direction="vertical" size={0}>
                      <b>{d.issue}</b>
                      <Typography.Text type="secondary">{d.reason}</Typography.Text>
                    </Space>
                  </List.Item>
                )}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small" title="缺失步骤">
              <List
                dataSource={inspection.missing_steps}
                renderItem={(d) => (
                  <List.Item>
                    <Space direction="vertical" size={0}>
                      <b>{d.step}</b>
                      <Typography.Text type="secondary">{d.reason}</Typography.Text>
                    </Space>
                  </List.Item>
                )}
              />
            </Card>
          </Col>
        </Row>
        <Button onClick={onInspect} loading={inspecting}>
          重新核查
        </Button>
      </Space>
    )
  }

  const renderEvaluation = () => {
    return (
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Space>
          <Button type="primary" onClick={onEvaluate} loading={evaluating} disabled={user?.role !== 'teacher'}>
            AI 客观评分
          </Button>
          <Typography.Text type="secondary">
            基于已配置的评价指标自动评分，教师可在表格中手动调整。
          </Typography.Text>
        </Space>
        {scores.length > 0 && <Chart option={radarOption} height={300} />}
        <Table rowKey="id" dataSource={scores} columns={scoreColumns} pagination={false} />
      </Space>
    )
  }

  const renderParsed = () => {
    if (!parsed) {
      return <Empty description="暂无解析结果" />
    }
    const fields = [
      ['摘要', parsed.summary],
      ['关键步骤', parsed.key_steps],
      ['功能点', parsed.features],
      ['界面元素', parsed.ui_elements],
      ['技术栈', parsed.technologies],
    ] as const
    return (
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Descriptions bordered column={1}>
          <Descriptions.Item label="状态">
            <Tag color={submission?.status === 'failed' ? 'error' : 'success'}>
              {submission?.status}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="文件">{submission?.file_names}</Descriptions.Item>
          {submission?.parse_error && (
            <Descriptions.Item label="错误">{submission.parse_error}</Descriptions.Item>
          )}
        </Descriptions>
        {fields.map(([label, val]) => (
          <Card key={label} size="small" title={label}>
            {Array.isArray(val) ? (
              <ul>{val.map((v, i) => <li key={i}>{String(v)}</li>)}</ul>
            ) : (
              <Typography.Paragraph>{val || '—'}</Typography.Paragraph>
            )}
          </Card>
        ))}
      </Space>
    )
  }

  return (
    <Card title={`成果详情 #${id}`}>
      <Tabs
        items={[
          { key: 'parsed', label: '解析结果', children: renderParsed() },
          { key: 'inspection', label: '智能核查', children: renderInspection() },
          { key: 'evaluation', label: '评价管理', children: renderEvaluation() },
        ]}
      />
    </Card>
  )
}
