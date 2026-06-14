import axios from "axios";
import { useAuthStore } from "@/store/authStore";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const runBacktest = async (payload: {
  strategy_id: string;
  start_date: string;
  end_date: string;
  symbol?: string;
  timeframe?: string;
}) => {
  const { data } = await api.post("/api/v1/backtests/run", payload);
  return data;
};

export const getBacktestResults = async () => {
  const { data } = await api.get("/api/v1/backtests/results");
  return data;
};

