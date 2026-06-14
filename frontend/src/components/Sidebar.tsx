import { Link, useLocation } from 'react-router-dom'

const NAV = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/portfolio', label: 'Portfolio' },
  { to: '/trading', label: 'Trading' },
  { to: '/intelligence', label: 'Intelligence' },
  { to: '/settings', label: 'Settings' },
]

export function Sidebar() {
  const location = useLocation()
  return (
    <aside className="hidden w-56 flex-col border-r border-slate-800 bg-slate-900/40 md:flex">
      <nav className="flex-1 space-y-1 p-3">
        {NAV.map((item) => {
          const active = location.pathname === item.to || location.pathname.startsWith(`${item.to}/`)
          return (
            <Link
              key={item.to}
              to={item.to}
              className={`block rounded-md px-3 py-2 text-sm font-medium ${
                active ? 'bg-slate-800 text-white' : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
              }`}
            >
              {item.label}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
