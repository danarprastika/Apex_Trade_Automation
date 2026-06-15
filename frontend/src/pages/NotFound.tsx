import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex min-h-[80vh] flex-col items-center justify-center bg-slate-950 text-slate-100">
      <div className="text-center space-y-6 max-w-md">
        <div className="relative mx-auto h-32 w-32">
          <div className="absolute inset-0 rounded-full bg-gradient-to-br from-indigo-500/20 to-purple-500/20 blur-xl"></div>
          <div className="relative flex h-full w-full items-center justify-center rounded-full bg-slate-800/80">
            <span className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-indigo-400 to-purple-400">
              404
            </span>
          </div>
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold text-white">Halaman Tidak Ditemukan</h1>
          <p className="text-slate-400">
            URL yang Anda akses tidak tersedia atau telah dipindahkan.
          </p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Link
            to="/dashboard"
            className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white transition-all hover:bg-indigo-500 hover:scale-105"
          >
            Kembali ke Dashboard
          </Link>
          <button
            onClick={() => window.history.back()}
            className="inline-flex items-center justify-center rounded-lg border border-slate-700 bg-slate-800/50 px-5 py-2.5 text-sm font-medium text-slate-300 transition-all hover:bg-slate-700/50 hover:text-white"
          >
            Kembali
          </button>
        </div>
      </div>
    </div>
  );
}