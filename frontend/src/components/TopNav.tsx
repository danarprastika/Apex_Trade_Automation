import { Link } from "react-router-dom";
import SystemStatusBadge from "./SystemStatusBadge";

const NAV = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/portfolio', label: 'Portfolio' },
  { to: '/ciso-dashboard', label: 'AI Intelligence Center' },
  { to: '/settings', label: 'Settings' },
];

export function TopNav() {
  return (
    <header className="h-14 border-b border-slate-800 bg-slate-900/60 backdrop-blur supports-[backdrop-filter]:bg-slate-900/60">
      <div className="mx-auto flex h-full max-w-7xl items-center justify-between px-4">
        <Link to="/" className="text-lg font-bold tracking-tight text-white">
          APEX
        </Link>
        <nav className="flex items-center gap-6 text-sm text-slate-300">
          {NAV.map((item) => (
            <Link key={item.to} to={item.to} className="hover:text-white transition-colors">
              {item.label}
            </Link>
          ))}
        </nav>
        <SystemStatusBadge />
      </div>
    </header>
  );
}