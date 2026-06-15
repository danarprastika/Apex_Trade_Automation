import { type FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "@/services/api";

export default function Register() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    if (password !== confirmPassword) {
      setError("Konfirmasi password tidak sama.");
      return;
    }

    setLoading(true);

    try {
      await api.post(
        "/api/v1/register",
        JSON.stringify({ email: email.trim(), password }),
        {
          headers: { "Content-Type": "application/json" },
        }
      );

      setSuccess("Registrasi berhasil. Mengalihkan ke halaman login...");
      setTimeout(() => navigate("/login", { replace: true }), 900);
    } catch (err) {
      const message = extractErrorMessage(err, "Registrasi gagal. Periksa kembali email dan password.");
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 p-4">
      <form onSubmit={onSubmit} className="w-full max-w-sm rounded-lg border border-slate-800 bg-slate-900 p-6 shadow-lg">
        <h1 className="mb-2 text-center text-2xl font-semibold text-white">Buat Akun APEX</h1>
        <p className="mb-6 text-center text-sm text-slate-400">Daftar untuk mengakses dashboard utama.</p>

        {error ? <p className="mb-4 rounded-md border border-red-800 bg-red-950/40 p-3 text-sm text-red-300">{error}</p> : null}
        {success ? <p className="mb-4 rounded-md border border-green-800 bg-green-950/40 p-3 text-sm text-green-300">{success}</p> : null}

        <label className="mb-2 block text-sm text-slate-300">Email</label>
        <input
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
          type="email"
          className="mb-4 w-full rounded-md border border-slate-800 bg-slate-950 p-2 text-white outline-none focus:border-slate-500"
          placeholder="you@example.com"
        />

        <label className="mb-2 block text-sm text-slate-300">Password</label>
        <input
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
          minLength={8}
          type="password"
          className="mb-4 w-full rounded-md border border-slate-800 bg-slate-950 p-2 text-white outline-none focus:border-slate-500"
          placeholder="Minimal 8 karakter"
        />

        <label className="mb-2 block text-sm text-slate-300">Konfirmasi Password</label>
        <input
          value={confirmPassword}
          onChange={(event) => setConfirmPassword(event.target.value)}
          required
          minLength={8}
          type="password"
          className="mb-6 w-full rounded-md border border-slate-800 bg-slate-950 p-2 text-white outline-none focus:border-slate-500"
          placeholder="Ulangi password"
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-white p-2 font-medium text-slate-900 hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Mendaftar..." : "Register"}
        </button>

        <p className="mt-5 text-center text-sm text-slate-400">
          Sudah punya akun?{" "}
          <Link to="/login" className="font-medium text-white hover:text-slate-300">
            Login
          </Link>
        </p>
      </form>
    </div>
  );
}

function extractErrorMessage(err: unknown, fallback: string) {
  const response = err as { response?: { data?: { detail?: string } }; message?: string } | undefined;
  const detail = response?.response?.data?.detail;

  if (typeof detail === "string") return detail;
  if (typeof response?.message === "string") return response.message;
  return fallback;
}
