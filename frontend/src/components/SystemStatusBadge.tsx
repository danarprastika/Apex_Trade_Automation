import { useEffect, useState } from "react";

export default function SystemStatusBadge() {
  const [status, setStatus] = useState<"healthy" | "degraded" | "checking">("checking");
  const [lastCheck, setLastCheck] = useState<string>("");

  useEffect(() => {
    let mounted = true;

    const checkHealth = async () => {
      try {
        const res = await fetch("/api/health", {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        });
        if (mounted) {
          if (res.ok) {
            const data = await res.json();
            if (data.status === "healthy") {
              setStatus("healthy");
            } else {
              setStatus("degraded");
            }
          } else {
            setStatus("degraded");
          }
          setLastCheck(new Date().toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" }));
        }
      } catch {
        if (mounted) {
          setStatus("degraded");
          setLastCheck(new Date().toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" }));
        }
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const statusConfig = {
    healthy: {
      icon: "🟢",
      text: "System Online",
      className: "bg-emerald-950/50 text-emerald-400 border-emerald-800/50",
    },
    degraded: {
      icon: "🔴",
      text: "System Degraded",
      className: "bg-red-950/50 text-red-400 border-red-800/50",
    },
    checking: {
      icon: "⏳",
      text: "Checking...",
      className: "bg-slate-800/50 text-slate-400 border-slate-700/50",
    },
  };

  const config = statusConfig[status];

  return (
    <div
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium transition-all ${config.className}`}
      title={`Last checked: ${lastCheck}`}
    >
      <span className="animate-pulse">{config.icon}</span>
      <span>{config.text}</span>
    </div>
  );
}