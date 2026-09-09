import { useState } from 'react';
import { Search, CalendarX2, CalendarClock, Crown } from 'lucide-react';
import { useStore, ACTIVE } from '../lib/store';
import { useToast, Button, Badge, Field, Input, Empty } from '../components/ui';
import { normalizeMobile, faNum, jalaliLong, timeOfFa, toToman } from '../lib/format';
import { LIFECYCLE_LABEL } from '../lib/risk';
import { STATUS_LABEL, STATUS_TONE } from '../lib/status';

export default function MyAppointments({ onBack }) {
  const { customers, appointments, serviceById, barberById, updateAppointmentStatus, customersEnriched } = useStore();
  const toast = useToast();
  const [query, setQuery] = useState('');
  const [looked, setLooked] = useState(false);

  const norm = normalizeMobile(query);
  const customer = norm.length >= 10 ? customers.find((c) => normalizeMobile(c.mobile) === norm) : null;
  const enriched = customer ? customersEnriched.find((e) => e.customer.id === customer.id) : null;

  const mine = customer
    ? appointments
        .filter((a) => a.customerId === customer.id)
        .sort((a, b) => new Date(b.startAt) - new Date(a.startAt))
    : [];

  const upcoming = mine.filter((a) => ACTIVE.includes(a.status));
  const past = mine.filter((a) => !ACTIVE.includes(a.status));

  function cancel(id) {
    updateAppointmentStatus(id, 'cancelled');
    toast('نوبت لغو شد.', 'warn');
  }

  return (
    <div className="container" style={{ maxWidth: 760 }}>
      <div className="page-head">
        <div>
          <h1>نوبت‌های من</h1>
          <p>با شماره موبایل، نوبت‌های خود را ببینید و مدیریت کنید.</p>
        </div>
        <Button variant="ghost" onClick={onBack}>بازگشت</Button>
      </div>

      <div style={{ display: 'flex', gap: 10 }}>
        <div style={{ flex: 1 }}>
          <Field label="شماره موبایل">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="09xxxxxxxxx"
              inputMode="tel"
              dir="ltr"
              style={{ textAlign: 'left' }}
            />
          </Field>
        </div>
        <Button style={{ alignSelf: 'flex-end', marginBottom: 14 }} onClick={() => setLooked(true)}>
          <Search size={16} /> جستجو
        </Button>
      </div>

      {!looked && (
        <Empty icon={<CalendarClock size={36} />} title="شماره موبایل خود را وارد کنید" hint="برای مشاهده‌ی نوبت‌ها جستجو کنید" />
      )}

      {looked && !customer && (
        <Empty icon={<CalendarX2 size={36} />} title="مشتری‌ای با این شماره یافت نشد" hint="شماره را بررسی کنید یا ابتدا نوبت رزرو کنید" />
      )}

      {customer && enriched && (
        <>
          <div className="card card-pad" style={{ marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
              <div className="avatar">{customer.name.slice(0, 1)}</div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <strong>{customer.name}</strong>
                  {enriched.metrics.tier === 'vip' && (
                    <Badge tone="gold"><Crown size={12} /> VIP</Badge>
                  )}
                  <Badge tone={enriched.metrics.lifecycle === 'at_risk' ? 'amber' : 'green'}>
                    {LIFECYCLE_LABEL[enriched.metrics.lifecycle]}
                  </Badge>
                </div>
                <div className="muted small">
                  {faNum(enriched.metrics.visitCount)} مراجعه · {toToman(enriched.metrics.totalSpend)} مجموع خرید
                </div>
              </div>
            </div>
          </div>

          <h3 style={{ margin: '0 0 10px' }}>نوبت‌های آینده</h3>
          {upcoming.length === 0 && <p className="muted small">نوبت فعالی ندارید.</p>}
          <div className="grid">
            {upcoming.map((a) => (
              <div className="card card-pad" key={a.id}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
                  <strong>{serviceById(a.serviceId)?.name}</strong>
                  <Badge tone={STATUS_TONE[a.status]}>{STATUS_LABEL[a.status]}</Badge>
                </div>
                <div className="muted small" style={{ marginTop: 4 }}>
                  {barberById(a.barberId)?.name} · {jalaliLong(a.startAt)} · ساعت {timeOfFa(a.startAt)}
                </div>
                {(a.status === 'requested' || a.status === 'confirmed') && (
                  <Button variant="danger" size="sm" style={{ marginTop: 10 }} onClick={() => cancel(a.id)}>
                    لغو نوبت
                  </Button>
                )}
              </div>
            ))}
          </div>

          {past.length > 0 && (
            <>
              <h3 style={{ margin: '22px 0 10px' }}>تاریخچه</h3>
              <div className="card">
                {past.map((a) => (
                  <div className="list-row" key={a.id}>
                    <div className="grow">
                      <div className="main">{serviceById(a.serviceId)?.name}</div>
                      <div className="sub">{jalaliLong(a.startAt)} · {timeOfFa(a.startAt)}</div>
                    </div>
                    <Badge tone={STATUS_TONE[a.status]}>{STATUS_LABEL[a.status]}</Badge>
                  </div>
                ))}
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}
