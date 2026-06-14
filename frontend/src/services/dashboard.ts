import { api } from '@/services/api'

export const getDashboardSummary = async () => {
  const { data } = await api.get('/dashboard/summary')
  return data
}

export const getPortfolio = async () => {
  const { data } = await api.get('/portfolio')
  return data
}
