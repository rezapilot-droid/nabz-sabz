import { useState } from 'react';
import { Search, Crown, MessageSquareText, Users, UserRound } from 'lucide-react';
import { useStore } from '../../lib/store';
import { useToast, Button, Badge, Modal, Empty, Input } from '../../components/ui';
import { faNum, toToman, jalaliStr, normalizeMobile } from '../../lib/format';
import { LIFECYCLE_LABEL, RISK_BAND_LABEL } from '../../lib/risk';

const LIFE_TONE = { new: 'blue', active: 'green', at_risk: 'amber', inactive: 'gray', churned: 'red' };
const RISK_TONE = { low: 'green', medium: 'amber', high: 'amber', 'very-high': 'red', critical: 'red' };

export default function CustomersAdmin() {
  const { customersEnriched, serviceById, barberById, offerToCustomer, hasFutureBooking } = useStore();
  const toast = useToast();
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState(null);

  const q = query.trim();
  const list = customersEnriched.filter((e) => {
    if (!q) return true;
    return e.customer.name.includes(q) || normalizeMobile(e.customer.mobile).includes(normalizeMobile(q));
  });

  const detail = selected
    ? customersEnriched.find((e) => e.customer.id === selected)
    : null;

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>مشتریان</h1>
          <p>{faNum(customersEnriched.length)} مشتری · CRM با ارزش و چرخه‌ی عمر</p>
        </div>
      </div>

      <div style={{ maxWidth: 420, marginBottom: 16, position: 'relative' }}>
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="جستجو بر اساس نام یا شماره…"
          style={{ paddingInlineStart: 40 }}
        />
        <span style={{ position: 'absolute', top: '50%', transform: 'translateY(-50%)', insetInlineStart: 14, color: 'var(--muted-2)', pointerEvents: 'none', display: 'grid' }}>
          <Search size={16} />
        </span>
      </div>

      <div className="card">
        {list.length === 0 && <Empty icon={<Users size={34} />} title="مشتری‌ای یافت نشد" />}
        {list.map((e) => {
          const { customer, metrics } = e;
          return (
            <div className="list-row" key={customer.id} onClick={() => setSelected(customer.id)} style={{ cursor: 'pointer' }}>
              <div className="avatar">{customer.name.slice(0, 1)}</div>
              <div className="grow">
                <div className="main" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  {customer.name}
                  {metrics.tier === 'vip' && <Badge tone="gold"><Crown size={12} /> VIP</Badge>}
                </div>
                <div className="sub">
                  {faNum(metrics.visitCount)} مراجعه · میانگین فاصله {metrics.medianInterval != null ? faNum(Math.round(metrics.medianInterval)) + ' روز' : '—'} · {toToman(metrics.totalSpend)}
                </div>
              </div>
              <div className="trail">
                {metrics.riskBand && <Badge tone={RISK_TONE[metrics.riskBand]}>ریسک {RISK_BAND_LABEL[metrics.riskBand]}</Badge>}
                <Badge tone={LIFE_TONE[metrics.lifecycle]}>{LIFECYCLE_LABEL[metrics.lifecycle]}</Badge>
              </div>
            </div>
          );
        })}
      </div>

      <Modal open={!!detail} onClose={() => setSelected(null)} title={detail ? detail.customer.name : ''} width="620px">
        {detail && (
          <div>
            <div className="chip-row" style={{ marginBottom: 14 }}>
              {detail.metrics.tier === 'vip' && <Badge tone="gold"><Crown size={13} /> مشتری VIP</Badge>}
              <Badge tone={LIFE_TONE[detail.metrics.lifecycle]}>{LIFECYCLE_LABEL[detail.metrics.lifecycle]}</Badge>
              {detail.metrics.riskBand && (
                <Badge tone={RISK_TONE[detail.metrics.riskBand]}>ریسک ریزش: {RISK_BAND_LABEL[detail.metrics.riskBand]}</Badge>
              )}
              {hasFutureBooking(detail.customer.id) && <Badge tone="green">نوبت آینده دارد</Badge>}
            </div>

            <div className="grid grid-2" style={{ marginBottom: 14 }}>
              <div className="kpi"><div className="kpi-label">مجموع مراجعات</div><div className="kpi-value">{faNum(detail.metrics.visitCount)}</div></div>
              <div className="kpi"><div className="kpi-label">مجموع خرید</div><div className="kpi-value gold">{toToman(detail.metrics.totalSpend)}</div></div>
              <div className="kpi"><div className="kpi-label">فاصله‌ی معمول مراجعه</div><div className="kpi-value">{detail.metrics.medianInterval != null ? faNum(Math.round(detail.metrics.medianInterval)) + ' روز' : '—'}</div></div>
              <div className="kpi"><div className="kpi-label">آخرین مراجعه</div><div className="kpi-value" style={{ fontSize: '1.1rem' }}>{detail.metrics.elapsedDays != null ? faNum(Math.round(detail.metrics.elapsedDays)) + ' روز پیش' : '—'}</div></div>
            </div>

            <p className="label">ترجیحات (از روی تاریخچه استخراج شده)</p>
            <p className="small muted" style={{ marginTop: 0 }}>
              آرایشگر موردعلاقه: {barberById(detail.metrics.favoriteBarberId)?.name || '—'} ·
              خدمت موردعلاقه: {serviceById(detail.metrics.favoriteServiceId)?.name || '—'}
            </p>

            <div className="divider" />

            <p className="label">تاریخچه‌ی مراجعات</p>
            {detail.customer.visits.length === 0 && <p className="small muted">هنوز مراجعه‌ای ثبت نشده است.</p>}
            <div style={{ maxHeight: 220, overflow: 'auto' }}>
              {[...detail.customer.visits].reverse().map((v, i) => (
                <div className="list-row" key={i}>
                  <div className="grow">
                    <div className="main small">{serviceById(v.serviceId)?.name}</div>
                    <div className="sub">{jalaliStr(v.date)} · {barberById(v.barberId)?.name}</div>
                  </div>
                  <span className="muted small">{toToman(v.revenueRial)}</span>
                </div>
              ))}
            </div>

            <div style={{ marginTop: 16 }}>
              <Button variant="gold-soft" onClick={() => { offerToCustomer(detail.customer.id); toast('پیام پیشنهاد (شبیه‌سازی) ارسال شد.', 'good'); }}>
                <MessageSquareText size={16} /> ارسال پیام پیشنهاد رزرو
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
