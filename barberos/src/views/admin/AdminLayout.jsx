import { useState } from 'react';
import {
  Scissors,
  LayoutDashboard,
  CalendarCheck2,
  Users,
  ListChecks,
  Settings,
  LogOut,
  Menu,
  X
} from 'lucide-react';
import { useStore } from '../../lib/store';

const LINKS = [
  { id: 'dashboard', label: 'داشبورد', icon: LayoutDashboard },
  { id: 'appointments', label: 'نوبت‌ها', icon: CalendarCheck2 },
  { id: 'customers', label: 'مشتریان', icon: Users },
  { id: 'services', label: 'خدمات و آرایشگران', icon: ListChecks },
  { id: 'settings', label: 'تنظیمات', icon: Settings }
];

export default function AdminLayout({ section, onSection, onExit, children }) {
  const { business } = useStore();
  const [open, setOpen] = useState(false);

  return (
    <div className="admin-shell">
      <aside className={`sidebar ${open ? 'open' : ''}`}>
        <div className="brand">
          <div className="brand-mark"><Scissors size={20} /></div>
          <div>
            {business.name}
            <small>پنل مدیریت · باربر OS</small>
          </div>
        </div>
        <nav className="sidebar-nav">
          {LINKS.map((l) => {
            const Icon = l.icon;
            return (
              <button
                key={l.id}
                className={`side-link ${section === l.id ? 'active' : ''}`}
                onClick={() => { onSection(l.id); setOpen(false); }}
              >
                <Icon size={18} /> {l.label}
              </button>
            );
          })}
        </nav>
        <div className="side-foot">
          <button className="side-link" onClick={onExit}>
            <LogOut size={18} /> خروج به سایت
          </button>
        </div>
      </aside>

      <main className="admin-main">
        <div className="admin-mobile-bar">
          <button className="icon-btn" onClick={() => setOpen(!open)} aria-label="منو">
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
          <strong>{LINKS.find((l) => l.id === section)?.label}</strong>
        </div>
        {children}
      </main>
    </div>
  );
}
