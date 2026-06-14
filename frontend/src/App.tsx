import { Navigate, Route } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import DashboardLayout from "@/layouts/DashboardLayout";
import Login from "@/pages/Login";
import DashboardPage from "@/pages/Dashboard";
import Portfolio from "@/pages/Portfolio";
import Settings from "@/pages/Settings";
import Trading from "@/pages/Trading";
import Intelligence from "@/pages/Intelligence";

// Dashboard / protected section.
function ProtectedRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return (
    <Route element={<DashboardLayout />}>
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/portfolio" element={<Portfolio />} />
      <Route path="/trading" element={<Trading />} />
      <Route path="/intelligence" element={<Intelligence />} />
      <Route path="/settings" element={<Settings />} />
    </Route>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<ProtectedRoute />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
