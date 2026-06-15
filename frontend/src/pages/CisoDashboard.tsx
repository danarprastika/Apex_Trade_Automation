import { useState, useEffect } from "react";

export default function CisoDashboard() {
  const cisoUrl = import.meta.env.VITE_CISO_DASHBOARD_URL ?? "/stream-backend/";
  const [loading, setLoading] = useState(true);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoaded(true);
      setLoading(false);
    }, 800);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="relative h-[100vh] w-full bg-slate-950 overflow-hidden">
      {loading && (
        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-4 bg-slate-900">
          <div className="relative">
            <div className="h-16 w-16 rounded-full border-4 border-slate-800 border-t-indigo-500 animate-spin"></div>
            <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-purple-500 animate-spin" style={{ animationDuration: "1.5s" }}></div>
          </div>
          <p className="text-slate-400 text-sm font-medium">Memuat AI Intelligence Center...</p>
        </div>
      )}
      <iframe
        title="CISO Dashboard"
        src={cisoUrl}
        allow="clipboard-read; clipboard-write"
        onLoad={() => {
          setLoading(false);
          setLoaded(true);
        }}
        className={`h-full w-full border-none transition-opacity duration-700 ${loaded ? "opacity-100" : "opacity-0"}`}
      />
    </div>
  );
}