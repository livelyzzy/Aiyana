import {
  DashboardOutlined,
  FileDoneOutlined,
  FileTextOutlined,
  LogoutOutlined,
  ProjectOutlined,
} from '@ant-design/icons'
import { Avatar, Layout, Menu, Space, Tag, Typography } from 'antd'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../store/auth'

const { Header, Sider, Content } = Layout

export default function MainLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const items = [
    { key: '/', icon: <DashboardOutlined />, label: '工作台' },
    { key: '/tasks', icon: <ProjectOutlined />, label: '实训任务' },
    { key: '/upload', icon: <FileTextOutlined />, label: '成果上传' },
    { key: '/reports', icon: <FileDoneOutlined />, label: '报表导出' },
  ]

  const selected = location.pathname.startsWith('/submissions') ? '/upload' : location.pathname

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="dark" width={220}>
        <div style={{ color: '#fff', fontSize: 18, fontWeight: 600, padding: 20, textAlign: 'center' }}>
          AI 实训评价系统
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selected]}
          items={items}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'center',
          }}
        >
          <Space>
            <Avatar>{user?.full_name?.[0]}</Avatar>
            <Typography.Text strong>{user?.full_name}</Typography.Text>
            <Tag color={user?.role === 'teacher' ? 'blue' : 'green'}>
              {user?.role === 'teacher' ? '教师' : '学生'}
            </Tag>
            <a onClick={logout}>
              <LogoutOutlined /> 退出
            </a>
          </Space>
        </Header>
        <Content style={{ margin: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
