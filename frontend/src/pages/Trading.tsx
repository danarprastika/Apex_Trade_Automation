import { useQuery } from "@tanstack/react-query";
import { CandlestickChart } from "@/components/charts/CandlestickChart";
import { api } from "@/services/api";

type CandlePoint = [number, number, number, number, number];

const candlesQuery = (symbol: string) => ({
    queryKey: ["candles", symbol],
    queryFn: async () => {
      const { data, status } = await api.get(`/v1/market/candles/${symbol}`);
      if (status !== 200) throw new Error("Failed to load candles");
      return (data?.data ?? []) as CandlePoint[];
    },
  });

export default function Trading() {
  const symbol = "BTCUSDT";
  const { data, isLoading, refetch } = useQuery(candlesQuery(symbol));

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white">Trading Terminal</h1>
          <p className="mt-1 text-sm text-slate-400">
            Live candlestick visualization for {symbol}
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="rounded-md bg-white px-3 py-1.5 text-sm font-medium text-slate-900 hover:bg-slate-200"
        >
          Refresh
        </button>
      </div>
      <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
        {isLoading ? (
          <p className="text-sm text-slate-400">Loading chart...</p>
        ) : (
          <CandlestickChart data={data ?? []} />
        )}
      </div>
    </div>
  );
}
