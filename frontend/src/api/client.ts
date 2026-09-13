import axios from 'axios'
import { message } from 'antd'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const TOKEN_KEY = 'aiyana_token'

export const client = axios.create({ baseURL })

client.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (resp) => resp,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    if (status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      if (location.pathname !== '/login') location.href = '/login'
    } else {
      message.error(typeof detail === 'string' ? detail : '请求失败，请稍后重试')
    }
    return Promise.reject(error)
  },
)
