import { useEffect, useState } from "react";
import { api } from "@/services/api";

type BacktestResult = {
  backtest_id: string;
  total_trades: number | null;
  win_rate: number | null;
  profit_factor: number | null;
  max_drawdown: number | null;
};

export default function Backtest() {
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [strategyId, setStrategyId] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [history, setHistory] = useState<BacktestResult[]>([]);

  const run = async () => {
    setLoading(true);
    try {
      const { data } = await api.post("/v1/backtests/run", {
        strategy_id: strategyId || "EMA_CROSS_V1",
        start_date: startDate || new Date(Date.now() - 30 * 24 * 3600 * 1000).toISOString(),
        end_date: endDate || new Date().toISOString(),
        symbol,
      });
      setResult(data?.data ?? data);
    } catch (err) {
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    const { data } = await api.get("/v1/backtests/results");
    setHistory(data?.data ?? []);
  };

  useEffect(() => {
    loadHistory();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Backtesting Engine</h1>
        <p className="mt-1 text-sm text-slate-400">Run strategy simulations over historical market data.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <div className="md:col-span-4 rounded-lg border border-slate-800 bg-slate-900/60 p-4 md:col-span-1">
          <label className="mb-2 block text-sm text-slate-300">Strategy</label>
          <input value={strategyId} onChange={(e) => setStrategyId(e.target.value)} className="mb-3 w-full rounded-md border border-slate-800 bg-slate-950 p-2 text-white outline-none focus:border-slate-500" />

          <label className="mb-2 block text-sm text-slate-300">Symbol</label>
          <input value={symbol} onChange={(e) => setSymbol(e.target.value)} className="mb-3 w-full rounded-md border border-slate-800 bg-slate-950 p-2 text-white outline-none focus:border-slate-500" />

          <label className="mb-2 block text-sm text-slate-300">Start Date</label>
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="mb-3 w-full rounded-md border border-slate-800 bg-slate-950 p-2 text-white outline-none focus:border-slate-500" />

          <label className="mb-2 block text-sm text-slate-300">End Date</label>
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="mb-3 w-full rounded-md border border-slate-800 bg-slate-950 p-2 text-white outline-none focus:border-slate-500" />

          <button onClick={() => { void run(); }} disabled={loading} className="w-full rounded-md bg-white p-2 font-medium text-slate-900 hover:bg-slate-200 disabled:opacity-60">
            {loading ? "Running..." : "Run Simulation"}
          </button>
        </div>

        <div className="md:col-span-3 space-y-4">
          {result && (
            <div className="grid gap-4 md:grid-cols-4">
              <MetricCard label="Total Trades" value={result.total_trades ?? 0} />
              <MetricCard label="Win Rate" value={result.win_rate != null ? `${result.win_rate.toFixed(2)}%` : "-"} />
              <MetricCard label="Profit Factor" value={result.profit_factor ?? "-"} />
              <MetricCard label="Max Drawdown" value={result.max_drawdown != null ? `${result.max_drawdown.toFixed(2)}%` : "-"} />
            </div>
          )}

          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
            <h2 className="text-lg font-semibold text-white">Recent Runs</h2>
            <div className="mt-4 space-y-3">
              {history.length === 0 && <p className="text-sm text-slate-400">No backtests yet.</p>}
              {history.map((run) => (
                <div key={run.backtest_id} className="flex items-center justify-between rounded-md border border-slate-800 p-3">
                  <div>
                    <p className="text-sm font-medium text-white">{run.backtest_id}</p>
                    <p className="text-xs text-slate-400">Win Rate {run.win_rate ?? 0}%</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-white">PF {run.profit_factor ?? "-"}</p>
                    <p className="text-xs text-slate-400">DD {run.max_drawdown ?? "-"}%</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
    </div>
  );
}
