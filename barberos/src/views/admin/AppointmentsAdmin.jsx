import { useState } from 'react';
import { Plus, CalendarX2 } from 'lucide-react';
import { useStore } from '../../lib/store';
import { useToast, Button, Badge, Modal, Empty } from '../../components/ui';
import { faNum, isToday, isTomorrow, jalaliLong, timeOfFa } from '../../lib/format';
import { STATUS_LABEL, STATUS_TONE } from '../../lib/status';
import BookingFlow from '../BookingFlow';

const FILTERS = [
  { id: 'today', label: 'امروز' },
  { id: 'tomorrow', label: 'فردا' },
  { id: 'upcoming', label: 'آینده' },
  { id: 'all', label: 'همه' }
];

export default function AppointmentsAdmin() {
  const { appointments, serviceById, barberById, customerById, updateAppointmentStatus } = useStore();
  const toast = useToast();
  const [filter, setFilter] = useState('today');
  const [manualOpen, setManualOpen] = useState(false);

  const now = Date.now();

  const filtered = appointments
    .filter((a) => {
      const t = new Date(a.startAt).getTime();
      if (filter === 'today') return isToday(a.startAt);
      if (filter === 'tomorrow') return isTomorrow(a.startAt);
      if (filter === 'upcoming') return t >= now;
      return true;
    })
    .sort((a, b) => new Date(a.startAt) - new Date(b.startAt));

  function act(id, status, msg) {
    updateAppointmentStatus(id, status);
    toast(msg, status === 'cancelled' || status === 'no_show' ? 'warn' : 'good');
  }

  function actionsFor(a) {
    const btns = [];
    if (a.status === 'requested') {
      btns.push(<Button key="c" size="sm" variant="success" onClick={() => act(a.id, 'confirmed', 'نوبت تأیید شد.')}>تأیید</Button>);
    }
    if (a.status === 'confirmed') {
      btns.push(<Button key="in" size="sm" variant="success" onClick={() => act(a.id, 'checked_in', 'مشتری حاضر شد.')}>حضور</Button>);
      btns.push(<Button key="ns" size="sm" variant="outline" onClick={() => act(a.id, 'no_show', 'عدم حضور ثبت شد.')}>عدم حضور</Button>);
    }
    if (a.status === 'checked_in') {
      btns.push(<Button key="st" size="sm" variant="primary" onClick={() => act(a.id, 'in_progress', 'سرویس شروع شد.')}>شروع سرویس</Button>);
    }
    if (a.status === 'in_progress') {
      btns.push(<Button key="co" size="sm" variant="success" onClick={() => act(a.id, 'completed', 'مراجعه تکمیل و ثبت شد.')}>تکمیل</Button>);
    }
    if (['requested', 'confirmed'].includes(a.status)) {
      btns.push(<Button key="x" size="sm" variant="danger" onClick={() => act(a.id, 'cancelled', 'نوبت لغو شد.')}>لغو</Button>);
    }
    return btns;
  }

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>مدیریت نوبت‌ها</h1>
          <p>{faNum(appointments.length)} نوبت در سیستم</p>
        </div>
        <Button onClick={() => setManualOpen(true)}><Plus size={16} /> رزرو دستی</Button>
      </div>

      <div className="chip-row" style={{ marginBottom: 16 }}>
        {FILTERS.map((f) => (
          <Button key={f.id} size="sm" variant={filter === f.id ? 'primary' : 'outline'} onClick={() => setFilter(f.id)}>
            {f.label}
          </Button>
        ))}
      </div>

      <div className="card">
        {filtered.length === 0 && (
          <Empty icon={<CalendarX2 size={34} />} title="نوبتی در این بازه نیست" hint="با «رزرو دستی» یک نوبت جدید بسازید" />
        )}
        {filtered.map((a) => {
          const c = customerById(a.customerId);
          return (
            <div className="list-row" key={a.id} style={{ flexWrap: 'wrap' }}>
              <div className="avatar">{c?.name?.slice(0, 1) || '؟'}</div>
              <div className="grow">
                <div className="main">
                  {c?.name || '—'}
                  <span className="muted small" style={{ marginInlineStart: 8 }} dir="ltr">{c?.mobile}</span>
                </div>
                <div className="sub">
                  {serviceById(a.serviceId)?.name} · {barberById(a.barberId)?.name} · {jalaliLong(a.startAt)} · {timeOfFa(a.startAt)}
                </div>
              </div>
              <div className="trail" style={{ flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                <Badge tone={STATUS_TONE[a.status]}>{STATUS_LABEL[a.status]}</Badge>
                <div className="action-strip">{actionsFor(a)}</div>
              </div>
            </div>
          );
        })}
      </div>

      <Modal open={manualOpen} onClose={() => setManualOpen(false)} title="رزرو دستی نوبت" width="680px">
        <BookingFlow
          status="confirmed"
          onDone={() => { setManualOpen(false); toast('نوبت با موفقیت ثبت و تأیید شد.', 'good'); }}
          onCancel={() => setManualOpen(false)}
        />
      </Modal>
    </div>
  );
}
