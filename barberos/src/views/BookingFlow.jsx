import { useState } from 'react';
import {
  Scissors,
  ChevronRight,
  ChevronLeft,
  CheckCircle2,
  CalendarDays,
  Clock,
  UserRound
} from 'lucide-react';
import { useStore } from '../lib/store';
import { useToast, Button, Badge, Field, Input } from '../components/ui';
import {
  faNum,
  toToman,
  normalizeMobile,
  jalaliLong,
  timeOfFa,
  todayJalali
} from '../lib/format';
import {
  JALALI_MONTHS,
  WEEKDAYS_SHORT,
  jalaliMonthLength,
  jalaliWeekday,
  fromJalali
} from '../lib/jalali';

const STEP_LABELS = ['خدمت', 'آرایشگر', 'تاریخ', 'ساعت', 'اطلاعات'];

function Calendar({ value, onChange, month, setMonth, today }) {
  const len = jalaliMonthLength(month.jy, month.jm);
  const firstDow = jalaliWeekday(fromJalali(month.jy, month.jm, 1));

  const isPast = (jy, jm, jd) =>
    jy < today.jy ||
    (jy === today.jy && jm < today.jm) ||
    (jy === today.jy && jm === today.jm && jd < today.jd);

  const prevDisabled = month.jy < today.jy || (month.jy === today.jy && month.jm <= today.jm);

  const nextMonth = () => {
    let { jy, jm } = month;
    jm += 1;
    if (jm > 12) {
      jm = 1;
      jy += 1;
    }
    setMonth({ jy, jm });
  };
  const prevMonth = () => {
    if (prevDisabled) return;
    let { jy, jm } = month;
    jm -= 1;
    if (jm < 1) {
      jm = 12;
      jy -= 1;
    }
    setMonth({ jy, jm });
  };

  const cells = [];
  for (let i = 0; i < firstDow; i += 1) cells.push(<div key={'e' + i} />);
  for (let jd = 1; jd <= len; jd += 1) {
    const past = isPast(month.jy, month.jm, jd);
    const friday = jalaliWeekday(fromJalali(month.jy, month.jm, jd)) === 6;
    const selected =
      value && value.jy === month.jy && value.jm === month.jm && value.jd === jd;
    const isToday = today.jy === month.jy && today.jm === month.jm && today.jd === jd;
    cells.push(
      <div
        key={jd}
        className={`day-cell ${past || friday ? 'muted' : ''} ${selected ? 'selected' : ''} ${isToday ? 'today' : ''}`}
        onClick={() => {
          if (past || friday) return;
          onChange({ jy: month.jy, jm: month.jm, jd });
        }}
      >
        {faNum(jd)}
      </div>
    );
  }

  return (
    <div>
      <div className="cal-head">
        <button className="icon-btn" onClick={prevMonth} disabled={prevDisabled} style={{ opacity: prevDisabled ? 0.3 : 1 }}>
          <ChevronRight size={18} />
        </button>
        <h4>
          {JALALI_MONTHS[month.jm - 1]} {faNum(month.jy)}
        </h4>
        <button className="icon-btn" onClick={nextMonth}>
          <ChevronLeft size={18} />
        </button>
      </div>
      <div className="cal-grid">
        {WEEKDAYS_SHORT.map((w) => (
          <div key={w} className="cal-wd">{w}</div>
        ))}
        {cells}
      </div>
      <p className="hint" style={{ marginTop: 10 }}>روزهای جمعه و روزهای گذشته قابل رزرو نیستند.</p>
    </div>
  );
}

export default function BookingFlow({ status = 'requested', onDone, onCancel }) {
  const { services, barbers, business, serviceById, barberById, getSlots, ensureCustomer, bookAppointment } = useStore();
  const toast = useToast();

  const todayJ = todayJalali();
  const [step, setStep] = useState(0);
  const [serviceId, setServiceId] = useState(null);
  const [barberId, setBarberId] = useState(null);
  const [month, setMonth] = useState({ jy: todayJ.jy, jm: todayJ.jm });
  const [date, setDate] = useState(null);
  const [slotStart, setSlotStart] = useState(null);
  const [name, setName] = useState('');
  const [mobile, setMobile] = useState('');
  const [done, setDone] = useState(null);

  const service = serviceById(serviceId);
  const barber = barberById(barberId);
  const eligibleBarbers = barbers.filter((b) => b.skills.includes(serviceId));

  const slots = date ? getSlots(barberId, serviceId, date.jy, date.jm, date.jd) : [];

  function go(s) {
    setStep(s);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function submit() {
    if (!name.trim()) return toast('نام و نام خانوادگی را وارد کنید.', 'warn');
    const norm = normalizeMobile(mobile);
    if (norm.length < 10 || norm.length > 11) return toast('شماره موبایل معتبر وارد کنید.', 'warn');
    const customer = ensureCustomer({ name: name.trim(), mobile: norm });
    const res = bookAppointment({
      customerId: customer.id,
      barberId,
      serviceId,
      startAt: slotStart,
      status
    });
    if (!res.ok) {
      toast(res.error, 'warn');
      return;
    }
    setDone(res.appointment);
    setStep(5);
  }

  const waitingForConfirm = status === 'requested';

  return (
    <div className="container" style={{ maxWidth: 760 }}>
      {!done && (
        <>
          <div className="page-head">
            <div>
              <h1>رزرو نوبت</h1>
              <p>در {business.name} — {business.city}</p>
            </div>
            <Button variant="ghost" onClick={onCancel}>انصراف</Button>
          </div>

          <div className="steps">
            {STEP_LABELS.map((l, i) => (
              <div key={l} className={`step-dot ${i < step ? 'done' : ''} ${i === step ? 'active' : ''}`} />
            ))}
          </div>

          {step === 0 && (
            <div className="grid grid-2">
              {services.map((s) => (
                <div
                  key={s.id}
                  className={`pick-card ${serviceId === s.id ? 'selected' : ''}`}
                  onClick={() => { setServiceId(s.id); setBarberId(null); go(1); }}
                >
                  <div className="t">{s.name}</div>
                  <div className="d"><Clock size={13} style={{ verticalAlign: -2 }} /> {faNum(s.durationMinutes)} دقیقه</div>
                  <div className="price">{toToman(s.priceRial)}</div>
                </div>
              ))}
            </div>
          )}

          {step === 1 && (
            <div className="grid grid-2">
              {eligibleBarbers.map((b) => (
                <div
                  key={b.id}
                  className={`pick-card ${barberId === b.id ? 'selected' : ''}`}
                  onClick={() => { setBarberId(b.id); go(2); }}
                >
                  <div className="t">{b.name}</div>
                  <div className="d">{faNum(b.skills.length)} خدمت در دسترس</div>
                  <div className="chip-row" style={{ marginTop: 4 }}>
                    <Badge tone="gray">آرایشگر</Badge>
                  </div>
                </div>
              ))}
            </div>
          )}

          {step === 2 && (
              <Calendar
                value={date}
                onChange={(d) => { setDate(d); setSlotStart(null); }}
                month={month}
                setMonth={setMonth}
                today={todayJ}
              />
          )}

          {step === 3 && (
            <>
              <div className="summary">
                <div className="summary-row"><span className="k">تاریخ</span><span className="v">{date && `${JALALI_MONTHS[date.jm - 1]} ${faNum(date.jd)} ${faNum(date.jy)}`}</span></div>
                <div className="summary-row"><span className="k">آرایشگر</span><span className="v">{barber?.name}</span></div>
              </div>
              {slots.length === 0 ? (
                <div className="empty">
                  <CalendarDays size={34} />
                  <p className="empty-title">این روز ظرفیت آزاد ندارد</p>
                  <p className="empty-hint">روز دیگری را انتخاب کنید.</p>
                </div>
              ) : (
                <>
                  <p className="label" style={{ marginBottom: 10 }}>ساعت مورد نظر را انتخاب کنید:</p>
                  <div className="slot-grid">
                    {slots.map((s) => (
                      <button
                        key={s.startAt}
                        className={`slot-btn ${slotStart === s.startAt ? 'selected' : ''}`}
                        onClick={() => setSlotStart(s.startAt)}
                      >
                        {timeOfFa(s.startAt)}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </>
          )}

          {step === 4 && (
            <>
              <div className="summary">
                <div className="summary-row"><span className="k">خدمت</span><span className="v">{service?.name} — {toToman(service?.priceRial)}</span></div>
                <div className="summary-row"><span className="k">آرایشگر</span><span className="v">{barber?.name}</span></div>
                <div className="summary-row"><span className="k">تاریخ و ساعت</span><span className="v">{jalaliLong(slotStart)} — {timeOfFa(slotStart)}</span></div>
              </div>
              <Field label="نام و نام خانوادگی">
                <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="مثلاً علی رضایی" />
              </Field>
              <Field label="شماره موبایل" hint="برای پیامک تأیید و یادآوری استفاده می‌شود">
                <Input
                  value={mobile}
                  onChange={(e) => setMobile(e.target.value)}
                  placeholder="09xxxxxxxxx"
                  inputMode="tel"
                  dir="ltr"
                  style={{ textAlign: 'left' }}
                />
              </Field>
              <div style={{ display: 'flex', gap: 10, marginTop: 8 }}>
                <Button variant="outline" onClick={() => go(3)}>بازگشت</Button>
                <Button className="btn-block" onClick={submit}>
                  <CheckCircle2 size={17} /> ثبت نهایی نوبت
                </Button>
              </div>
            </>
          )}
        </>
      )}

      {done && (
        <div className="success-hero">
          <div className="ring"><CheckCircle2 size={34} /></div>
          <h2>نوبت شما ثبت شد 🎉</h2>
          <div className="summary" style={{ textAlign: 'right', marginTop: 20 }}>
            <div className="summary-row"><span className="k">خدمت</span><span className="v">{serviceById(done.serviceId)?.name}</span></div>
            <div className="summary-row"><span className="k">آرایشگر</span><span className="v">{barberById(done.barberId)?.name}</span></div>
            <div className="summary-row"><span className="k">تاریخ</span><span className="v">{jalaliLong(done.startAt)}</span></div>
            <div className="summary-row"><span className="k">ساعت</span><span className="v">{timeOfFa(done.startAt)}</span></div>
          </div>
          {waitingForConfirm ? (
            <p className="muted" style={{ maxWidth: 420, margin: '18px auto' }}>
              نوبت شما در <strong>انتظار تأیید</strong> آرایشگاه است؛ پس از تأیید، پیامک تأیید و یادآوری برای شما ارسال می‌شود.
            </p>
          ) : (
            <p className="muted" style={{ maxWidth: 420, margin: '18px auto' }}>
              نوبت شما <strong>تأیید</strong> شد؛ پیامک یادآوری پیش از نوبت ارسال خواهد شد.
            </p>
          )}
          <Button onClick={onDone}>بازگشت به صفحه اصلی</Button>
        </div>
      )}

      {!done && step > 0 && step < 4 && (
        <div style={{ marginTop: 24, display: 'flex', gap: 10 }}>
          <Button variant="ghost" onClick={() => go(step - 1)}>بازگشت</Button>
        </div>
      )}
      {!done && step === 2 && date && (
        <div style={{ marginTop: 20 }}>
          <Button className="btn-block" disabled={!date} onClick={() => go(3)}>انتخاب ساعت</Button>
        </div>
      )}
      {!done && step === 3 && slotStart && (
        <div style={{ marginTop: 20 }}>
          <Button className="btn-block" onClick={() => go(4)}>ادامه — اطلاعات تماس</Button>
        </div>
      )}
    </div>
  );
}
