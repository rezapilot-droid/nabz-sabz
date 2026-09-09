import { useState } from 'react';
import { Save, RotateCcw, Store, Clock4, SlidersHorizontal } from 'lucide-react';
import { useStore } from '../../lib/store';
import { useToast, Button, Card, Field, Input } from '../../components/ui';
import { WEEKDAYS } from '../../lib/jalali';
import { faNum } from '../../lib/format';

export default function SettingsAdmin() {
  const { business, updateBusiness, updateScheduling, updateWorkingHours, resetData } = useStore();
  const toast = useToast();

  const [info, setInfo] = useState({ name: business.name, city: business.city, phone: business.phone, slogan: business.slogan || '' });
  const [hours, setHours] = useState(business.workingHours);
  const [sched, setSched] = useState(business.scheduling);
  const [cust, setCust] = useState(business.customer);

  function saveHours() {
    const cleaned = Object.fromEntries(
      Object.entries(hours).map(([k, v]) => [k, v.closed ? { closed: true } : { open: v.open || '09:00', close: v.close || '21:00' }])
    );
    updateWorkingHours(cleaned);
    toast('ساعات کاری ذخیره شد.', 'good');
  }

  function toggleClosed(day) {
    setHours((h) => {
      const cur = h[day];
      const next = cur?.closed ? { open: '09:00', close: '21:00' } : { ...cur, closed: true };
      return { ...h, [day]: next };
    });
  }

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>تنظیمات آرایشگاه</h1>
          <p>این بخش همان «پیکربندی» در BarberOS Workflow است — بدون کدنویسی تغییر می‌کند.</p>
        </div>
      </div>

      <div className="grid grid-2">
        <Card title="اطلاعات کسب‌وکار" icon={<Store size={17} />}>
          <div className="card-pad">
            <Field label="نام آرایشگاه"><Input value={info.name} onChange={(e) => setInfo({ ...info, name: e.target.value })} /></Field>
            <Field label="شعار"><Input value={info.slogan} onChange={(e) => setInfo({ ...info, slogan: e.target.value })} /></Field>
            <div className="grid grid-2">
              <Field label="شهر"><Input value={info.city} onChange={(e) => setInfo({ ...info, city: e.target.value })} /></Field>
              <Field label="تلفن"><Input value={info.phone} onChange={(e) => setInfo({ ...info, phone: e.target.value })} dir="ltr" style={{ textAlign: 'left' }} /></Field>
            </div>
            <Button onClick={() => { updateBusiness(info); toast('اطلاعات ذخیره شد.', 'good'); }}><Save size={16} /> ذخیره</Button>
          </div>
        </Card>

        <Card title="ساعات کاری" icon={<Clock4 size={17} />}>
          <div className="card-pad">
            {[0, 1, 2, 3, 4, 5, 6].map((d) => (
              <div key={d} className="list-row" style={{ padding: '8px 0' }}>
                <div className="grow" style={{ minWidth: 90 }}>
                  <span className="main small">{WEEKDAYS[d]}</span>
                </div>
                {hours[d]?.closed ? (
                  <Badge tone="red">تعطیل</Badge>
                ) : (
                  <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                    <Input type="time" value={hours[d]?.open || '09:00'} onChange={(e) => setHours({ ...hours, [d]: { ...hours[d], open: e.target.value } })} style={{ width: 100, padding: 6 }} />
                    <span className="muted">تا</span>
                    <Input type="time" value={hours[d]?.close || '21:00'} onChange={(e) => setHours({ ...hours, [d]: { ...hours[d], close: e.target.value } })} style={{ width: 100, padding: 6 }} />
                  </div>
                )}
                <Button size="sm" variant="ghost" onClick={() => toggleClosed(d)}>
                  {hours[d]?.closed ? 'باز کردن' : 'تعطیل'}
                </Button>
              </div>
            ))}
            <Button className="btn-block" onClick={saveHours}><Save size={16} /> ذخیره ساعات</Button>
          </div>
        </Card>

        <Card title="سیاست رزرو" icon={<SlidersHorizontal size={17} />}>
          <div className="card-pad">
            <div className="grid grid-2">
              <Field label="دانه‌بندی slot (دقیقه)"><Input type="number" value={sched.slotGranularityMinutes} onChange={(e) => setSched({ ...sched, slotGranularityMinutes: +e.target.value })} /></Field>
              <Field label="بافر پیش‌فرض (دقیقه)"><Input type="number" value={sched.defaultBufferMinutes} onChange={(e) => setSched({ ...sched, defaultBufferMinutes: +e.target.value })} /></Field>
              <Field label="حداقل فاصله تا رزرو (دقیقه)"><Input type="number" value={sched.minLeadMinutes} onChange={(e) => setSched({ ...sched, minLeadMinutes: +e.target.value })} /></Field>
              <Field label="حداکثر افق رزرو (روز)"><Input type="number" value={sched.maxAdvanceDays} onChange={(e) => setSched({ ...sched, maxAdvanceDays: +e.target.value })} /></Field>
            </div>
            <Button onClick={() => { updateScheduling(sched); toast('سیاست رزرو ذخیره شد.', 'good'); }}><Save size={16} /> ذخیره</Button>
          </div>
        </Card>

        <Card title="سیاست مشتری" icon={<SlidersHorizontal size={17} />}>
          <div className="card-pad">
            <div className="grid grid-2">
              <Field label="آستانه VIP (تعداد مراجعه)"><Input type="number" value={cust.vipVisitThreshold} onChange={(e) => setCust({ ...cust, vipVisitThreshold: +e.target.value })} /></Field>
              <Field label="روز تا ریزش کامل (churn)"><Input type="number" value={cust.churnDays} onChange={(e) => setCust({ ...cust, churnDays: +e.target.value })} /></Field>
              <Field label="مهلت پس از عادت (غیرفعال)"><Input type="number" value={cust.churnGraceDays} onChange={(e) => setCust({ ...cust, churnGraceDays: +e.target.value })} /></Field>
            </div>
            <Button onClick={() => { updateBusiness({ customer: cust }); toast('سیاست مشتری ذخیره شد.', 'good'); }}><Save size={16} /> ذخیره</Button>

            <div className="divider" />
            <p className="label" style={{ color: 'var(--red)' }}>بازنشانی داده</p>
            <p className="hint" style={{ marginTop: 0 }}>همه‌ی داده‌ها به حالت نمونه اولیه برمی‌گردد.</p>
            <Button variant="danger" onClick={() => { resetData(); toast('داده‌ها بازنشانی شد.', 'warn'); }}>
              <RotateCcw size={15} /> بازنشانی داده‌ی نمونه
            </Button>
          </div>
        </Card>
      </div>

      <p className="hint" style={{ marginTop: 16 }}>
        یادآوری: {faNum(sched.slotGranularityMinutes)} دقیقه دانه‌بندی · بافر {faNum(sched.defaultBufferMinutes)} دقیقه · رزرو حداقل {faNum(sched.minLeadMinutes)} دقیقه قبل
      </p>
    </div>
  );
}
