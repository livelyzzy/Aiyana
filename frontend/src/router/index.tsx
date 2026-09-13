import { Navigate, createBrowserRouter } from 'react-router-dom'
import MainLayout from '../layouts/MainLayout'
import Dashboard from '../pages/Dashboard'
import Login from '../pages/Login'
import Reports from '../pages/Reports'
import SubmissionDetail from '../pages/SubmissionDetail'
import Tasks from '../pages/Tasks'
import Upload from '../pages/Upload'
import { useAuth } from '../store/auth'

function RequireAuth({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth()
  if (loading) return null
  if (!user) return <Navigate to="/login" replace />
  return children
}

export const router = createBrowserRouter([
  { path: '/login', element: <Login /> },
  {
    path: '/',
    element: (
      <RequireAuth>
        <MainLayout />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'tasks', element: <Tasks /> },
      { path: 'upload', element: <Upload /> },
      { path: 'submissions/:id', element: <SubmissionDetail /> },
      { path: 'reports', element: <Reports /> },
    ],
  },
])
