import { useState } from 'react';
import { Scissors } from 'lucide-react';
import { useStore } from './lib/store';
import Home from './views/Home';
import BookingFlow from './views/BookingFlow';
import MyAppointments from './views/MyAppointments';
import AdminLayout from './views/admin/AdminLayout';
import Dashboard from './views/admin/Dashboard';
import AppointmentsAdmin from './views/admin/AppointmentsAdmin';
import CustomersAdmin from './views/admin/CustomersAdmin';
import ServicesBarbers from './views/admin/ServicesBarbers';
import SettingsAdmin from './views/admin/SettingsAdmin';

export default function App() {
  const { business } = useStore();
  const [view, setView] = useState('home');
  const [adminSection, setAdminSection] = useState('dashboard');

  function go(v) {
    setView(v);
    window.scrollTo({ top: 0 });
  }

  if (view === 'admin') {
    const sections = {
      dashboard: <Dashboard onNavigate={setAdminSection} />,
      appointments: <AppointmentsAdmin />,
      customers: <CustomersAdmin />,
      services: <ServicesBarbers />,
      settings: <SettingsAdmin />
    };
    return (
      <AdminLayout section={adminSection} onSection={setAdminSection} onExit={() => go('home')}>
        {sections[adminSection]}
      </AdminLayout>
    );
  }

  return (
    <>
      <header className="topbar">
        <div className="brand" onClick={() => go('home')}>
          <div className="brand-mark"><Scissors size={20} /></div>
          <div>
            {business.name}
            <small>باربر OS</small>
          </div>
        </div>
        <nav className="topbar-nav">
          <button className="btn btn-ghost btn-sm" onClick={() => go('booking')}>رزرو نوبت</button>
          <button className="btn btn-ghost btn-sm" onClick={() => go('my')}>نوبت‌های من</button>
          <button className="btn btn-gold-soft btn-sm" onClick={() => go('admin')}>پنل مدیریت</button>
        </nav>
      </header>

      {view === 'home' && (
        <Home onCustomer={() => go('booking')} onAdmin={() => go('admin')} onMy={() => go('my')} />
      )}
      {view === 'booking' && (
        <BookingFlow status="requested" onDone={() => go('home')} onCancel={() => go('home')} />
      )}
      {view === 'my' && <MyAppointments onBack={() => go('home')} />}
    </>
  );
}
