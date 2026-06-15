import { Outlet, useLocation } from "react-router-dom";
import { TopNav } from "@/components/TopNav";
import { Sidebar } from "@/components/Sidebar";
const DashboardLayout = () => {
  const location = useLocation();
  const isCisoDashboard = location.pathname.startsWith("/ciso-dashboard");

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {!isCisoDashboard && <TopNav />}
      <div className="flex">
        {!isCisoDashboard && <Sidebar />}
        <main className={`flex-1 ${isCisoDashboard ? "p-0" : "p-6"}`}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};
export default DashboardLayout;
