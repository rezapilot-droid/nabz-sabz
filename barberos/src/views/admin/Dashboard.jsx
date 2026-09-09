import {
  CalendarCheck2,
  Wallet,
  Clock4,
  Hourglass,
  AlertTriangle,
  UserPlus,
  MessageSquareText,
  ChevronLeft,
  Sparkles
} from 'lucide-react';
import { useStore } from '../../lib/store';
import { useToast, Button, Badge, Card } from '../../components/ui';
import { faNum, toToman, timeOfFa } from '../../lib/format';
import { STATUS_LABEL, STATUS_TONE } from '../../lib/status';
import { RISK_BAND_LABEL } from '../../lib/risk';

export default function Dashboard({ onNavigate }) {
  const { dashboardStats, serviceById, barberById, customerById, offerToCustomer, messages } = useStore();
  const toast = useToast();

  const d = dashboardStats;

  const kpis = [
    { label: 'نوبت‌های امروز', value: faNum(d.todayAppts.length), icon: CalendarCheck2, sub: `${faNum(d.confirmedCount)} تأیید شده` },
    { label: 'درآمد مورد انتظار', value: toToman(d.expectedRevenue), icon: Wallet, gold: true, sub: 'امروز' },
    { label: 'اسلات خالی امروز', value: faNum(d.emptySlots), icon: Clock4, sub: 'از همین حالا' },
    { label: 'در انتظار تأیید', value: faNum(d.pending.length), icon: Hourglass, sub: 'رزرو آنلاین' },
    { label: 'در معرض ریزش', value: faNum(d.atRisk.length), icon: AlertTriangle, sub: 'نیازمند اقدام' },
    { label: 'مشتری جدید (۳۰ روز)', value: faNum(d.newLast30d.length), icon: UserPlus, sub: 'رشد' }
  ];

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>داشبورد مدیریت</h1>
          <p>نمای کلی امروز و پیشنهادهای عملی هوشمند</p>
        </div>
      </div>

      <div className="grid grid-3" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))' }}>
        {kpis.map((k) => {
          const Icon = k.icon;
          return (
            <div className="kpi" key={k.label}>
              <div className="kpi-label"><Icon size={15} /> {k.label}</div>
              <div className={`kpi-value ${k.gold ? 'gold' : ''}`}>{k.value}</div>
              <div className="kpi-sub">{k.sub}</div>
            </div>
          );
        })}
      </div>

      <div className="section-gap">
        <Card title="پیشنهادهای هوشمند (Top Actions)" icon={<Sparkles size={17} />}>
          <div className="card-pad grid">
            {d.topActions.length === 0 && (
              <p className="muted small" style={{ margin: 0 }}>همه‌چیز مرتب است؛ اقدام فوری لازم نیست.</p>
            )}
            {d.topActions.map((a) => (
              <div className="list-row" key={a.id} style={{ borderBottom: 'none' }}>
                <div className="grow">
                  <div className="main">{a.title}</div>
                  <div className="sub">{a.detail}</div>
                </div>
                <Button
                  size="sm"
                  variant={a.tone === 'warn' ? 'gold-soft' : 'outline'}
                  onClick={() => onNavigate(a.id === 'at-risk' ? 'customers' : 'appointments')}
                >
                  بررسی <ChevronLeft size={15} />
                </Button>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="section-gap grid grid-2">
        <Card title="برنامه امروز" icon={<CalendarCheck2 size={17} />}>
          {d.todayAppts.length === 0 && (
            <p className="muted small" style={{ padding: 16 }}>نوبتی برای امروز ثبت نشده است.</p>
          )}
          {d.todayAppts.map((a) => (
            <div className="list-row" key={a.id}>
              <div className="avatar">{customerById(a.customerId)?.name?.slice(0, 1) || '؟'}</div>
              <div className="grow">
                <div className="main">{customerById(a.customerId)?.name}</div>
                <div className="sub">{serviceById(a.serviceId)?.name} · {barberById(a.barberId)?.name}</div>
              </div>
              <div className="trail">
                <span className="muted small">{timeOfFa(a.startAt)}</span>
                <Badge tone={STATUS_TONE[a.status]}>{STATUS_LABEL[a.status]}</Badge>
              </div>
            </div>
          ))}
        </Card>

        <Card title="مشتریان در معرض ریزش" icon={<AlertTriangle size={17} />}
          actions={<Button size="sm" variant="ghost" onClick={() => onNavigate('customers')}>همه</Button>}>
          {d.atRiskNoBooking.length === 0 && (
            <p className="muted small" style={{ padding: 16 }}>مشتری در معرض ریزشی بدون نوبت وجود ندارد. 🎉</p>
          )}
          {d.atRiskNoBooking.slice(0, 6).map((e) => (
            <div className="list-row" key={e.customer.id}>
              <div className="grow">
                <div className="main">{e.customer.name}</div>
                <div className="sub">
                  ریسک {RISK_BAND_LABEL[e.metrics.riskBand]} · آخرین مراجعه {faNum(Math.round(e.metrics.elapsedDays))} روز پیش
                </div>
              </div>
              <Button size="sm" variant="gold-soft" onClick={() => { offerToCustomer(e.customer.id); toast('پیام پیشنهاد (شبیه‌سازی) ارسال شد.', 'good'); }}>
                <MessageSquareText size={14} /> ارسال پیشنهاد
              </Button>
            </div>
          ))}
        </Card>
      </div>

      <div className="section-gap">
        <Card title="آخرین پیام‌های ارسال‌شده (شبیه‌سازی SMS)" icon={<MessageSquareText size={17} />}>
          {messages.length === 0 && (
            <p className="muted small" style={{ padding: 16 }}>هنوز پیامی ارسال نشده است.</p>
          )}
          {messages.slice(0, 6).map((m) => (
            <div className="list-row" key={m.id}>
              <div className="grow">
                <div className="main small">{m.text}</div>
                <div className="sub" dir="ltr" style={{ textAlign: 'right' }}>{m.to} · {m.template}</div>
              </div>
              <Badge tone="green">sent</Badge>
            </div>
          ))}
        </Card>
      </div>
    </div>
  );
}
