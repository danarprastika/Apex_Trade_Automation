import { useEffect, useState } from "react";
import { api } from "@/services/api";

type AIModel = {
  id: string;
  name: string;
  version: string;
  architecture: string;
  target_asset: string;
  accuracy_score: number | null;
  is_active: boolean;
};

type Prediction = {
  id: string;
  model_id: string;
  symbol: string;
  predicted_direction: string;
  confidence_score: number;
  actual_direction: string | null;
  is_correct: boolean | null;
  created_at: string | null;
};

export default function Intelligence() {
  const [models, setModels] = useState<AIModel[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    const [modelsRes, predsRes] = await Promise.all([
      api.get("/api/v1/ai/models"),
      api.get("/api/v1/ai/predictions"),
    ]);
    setModels(modelsRes.data?.data ?? []);
    setPredictions(predsRes.data?.data ?? []);
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, []);

  const activeModel = models.find((m) => m.is_active);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white">AI Intelligence</h1>
          <p className="mt-1 text-sm text-slate-400">Model management and prediction history</p>
        </div>
        <button onClick={load} className="rounded-md bg-white px-3 py-1.5 text-sm font-medium text-slate-900 hover:bg-slate-200">
          Refresh
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
          <p className="text-sm text-slate-400">Total Models</p>
          <p className="mt-2 text-3xl font-semibold text-white">{models.length}</p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
          <p className="text-sm text-slate-400">Active Model Accuracy</p>
          <p className="mt-2 text-3xl font-semibold text-white">
            {activeModel ? `${(activeModel.accuracy_score ?? 0).toFixed(2)}%` : "-"}
          </p>
          {activeModel && <p className="mt-1 text-xs text-slate-400">{activeModel.name}</p>}
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
          <p className="text-sm text-slate-400">Predictions Logged</p>
          <p className="mt-2 text-3xl font-semibold text-white">{predictions.length}</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
          <h2 className="text-lg font-semibold text-white">AI Models</h2>
          <div className="mt-4 space-y-3">
            {models.length === 0 && <p className="text-sm text-slate-400">No models registered.</p>}
            {models.map((model) => (
              <div key={model.id} className="flex items-center justify-between rounded-md border border-slate-800 p-3">
                <div>
                  <p className="text-sm font-medium text-white">{model.name}</p>
                  <p className="text-xs text-slate-400">
                    {model.architecture} • {model.target_asset} • v{model.version}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-white">{model.accuracy_score ? `${model.accuracy_score.toFixed(2)}%` : "-"}</p>
                  <p className="text-xs text-slate-400">{model.is_active ? "Active" : "Inactive"}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
          <h2 className="text-lg font-semibold text-white">Recent Predictions</h2>
          <div className="mt-4 space-y-3">
            {predictions.length === 0 && <p className="text-sm text-slate-400">No predictions yet.</p>}
            {predictions.slice(0, 20).map((pred) => (
              <div key={pred.id} className="flex items-center justify-between rounded-md border border-slate-800 p-3">
                <div>
                  <p className="text-sm font-medium text-white">
                    {pred.symbol} •{" "}
                    <span className={pred.predicted_direction === "BULLISH" ? "text-green-400" : "text-red-400"}>
                      {pred.predicted_direction}
                    </span>
                  </p>
                  <p className="text-xs text-slate-400">
                    Confidence {(pred.confidence_score * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-white">
                    {pred.is_correct === null ? "Pending" : pred.is_correct ? "Correct" : "Wrong"}
                  </p>
                  <p className="text-xs text-slate-400">
                    {pred.created_at ? new Date(pred.created_at).toLocaleString() : "-"}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {loading && <p className="text-sm text-slate-400">Loading...</p>}
    </div>
  );
}
