import { Outlet } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import TopNav from "@/components/TopNav";
import Sidebar from "@/components/Sidebar";
const DashboardLayout = () => {
  const token = useAuthStore((s) => s.token);
// Redirecting non-authenticated users away from private routes is handled by the login page flow.
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <TopNav />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
export default DashboardLayout;
