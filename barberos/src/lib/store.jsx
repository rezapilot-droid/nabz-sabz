import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { buildSeed } from './seed';
import { customerMetrics, median } from './risk';
import {
  normalizeMobile,
  minutesOf,
  jalaliOf,
  todayJalali,
  isToday,
  atTehran,
  faNum,
  timeOfFa,
  jalaliStr
} from './format';
import { jalaliWeekday, j2g } from './jalali';

const KEY = 'barberos-state-v2';
const ACTIVE = ['requested', 'confirmed', 'checked_in', 'in_progress'];
const REVENUE_STATUSES = ['confirmed', 'checked_in', 'in_progress', 'completed'];

const StoreContext = createContext(null);

function load() {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (parsed && parsed.version === 2) return parsed;
    return null;
  } catch {
    return null;
  }
}

function jDateDayStart(jy, jm, jd) {
  const { gy, gm, gd } = j2g(jy, jm, jd);
  return Date.UTC(gy, gm - 1, gd) - 3.5 * 3600 * 1000;
}

function appointmentEnd(state, appt) {
  const svc = state.services.find((s) => s.id === appt.serviceId);
  const dur = svc ? svc.durationMinutes : 30;
  const buf = svc ? svc.bufferMinutes ?? state.business.scheduling.defaultBufferMinutes : 5;
  return new Date(appt.startAt).getTime() + (dur + buf) * 60000;
}

function overlaps(aStart, aEnd, bStart, bEnd) {
  return aStart < bEnd && bStart < aEnd;
}

export function AppProvider({ children }) {
  const [state, setState] = useState(() => load() || buildSeed());

  useEffect(() => {
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
    } catch {
      /* ignore quota errors */
    }
  }, [state]);

  const value = useMemo(() => {
    const { business, services, barbers, customers, appointments, messages } = state;

    /* ---------- helper lookups ---------- */
    const serviceById = (id) => services.find((s) => s.id === id);
    const barberById = (id) => barbers.find((b) => b.id === id);
    const customerById = (id) => customers.find((c) => c.id === id);

    /* ---------- derived customer intelligence ---------- */
    const shopMedian = (() => {
      const meds = customers
        .map((c) => customerMetrics(c, business.customer).medianInterval)
        .filter((v) => v != null);
      return median(meds);
    })();

    const customersEnriched = customers
      .map((customer) => ({
        customer,
        metrics: customerMetrics(customer, { ...business.customer, shopMedian })
      }))
      .sort((a, b) => {
        const order = { at_risk: 0, active: 1, new: 2, inactive: 3, churned: 4 };
        return (order[a.metrics.lifecycle] ?? 9) - (order[b.metrics.lifecycle] ?? 9);
      });

    const hasFutureBooking = (customerId) =>
      appointments.some(
        (a) => a.customerId === customerId && ACTIVE.includes(a.status) && new Date(a.startAt).getTime() > Date.now()
      );

    /* ---------- free-slot engine ---------- */
    function computeFreeSlots(barberId, durationMinutes, bufferMinutes, jy, jm, jd) {
      const barber = barberById(barberId);
      if (!barber) return [];
      const { gy, gm, gd } = j2g(jy, jm, jd);
      const weekday = jalaliWeekday(new Date(gy, gm - 1, gd));
      const wh = business.workingHours[weekday];
      if (!wh || wh.closed) return [];

      const openMin = minutesOf(wh.open);
      const closeMin = minutesOf(wh.close);
      const dayStart = jDateDayStart(jy, jm, jd);
      const gran = business.scheduling.slotGranularityMinutes || 15;
      const minLead = business.scheduling.minLeadMinutes || 30;

      const busy = appointments
        .filter((a) => a.barberId === barberId && ACTIVE.includes(a.status))
        .map((a) => [new Date(a.startAt).getTime(), appointmentEnd(state, a)]);

      const slots = [];
      const slotLen = (durationMinutes + bufferMinutes) * 60000;
      const first = dayStart + openMin * 60000;
      const last = dayStart + closeMin * 60000;

      for (let t = first; t + slotLen <= last; t += gran * 60000) {
        const end = t + slotLen;
        if (t < Date.now() + minLead * 60000) continue;
        if (busy.some(([s, e]) => overlaps(t, end, s, e))) continue;
        slots.push({
          startAt: new Date(t).toISOString(),
          endAt: new Date(end).toISOString()
        });
      }
      return slots;
    }

    function getSlots(barberId, serviceId, jy, jm, jd) {
      const svc = serviceById(serviceId);
      if (!svc) return [];
      const buf = svc.bufferMinutes ?? business.scheduling.defaultBufferMinutes;
      return computeFreeSlots(barberId, svc.durationMinutes, buf, jy, jm, jd);
    }

    /* ---------- dashboard stats ---------- */
    function dashboardStats() {
      const todayAppts = appointments
        .filter((a) => isToday(a.startAt))
        .sort((a, b) => new Date(a.startAt) - new Date(b.startAt));

      const pending = todayAppts.filter((a) => a.status === 'requested');
      const confirmedCount = todayAppts.filter((a) =>
        ['confirmed', 'checked_in', 'in_progress'].includes(a.status)
      ).length;

      const expectedRevenue = todayAppts
        .filter((a) => REVENUE_STATUSES.includes(a.status))
        .reduce((sum, a) => sum + (serviceById(a.serviceId)?.priceRial || 0), 0);

      const todayJ = todayJalali();
      const emptySlots = barbers.reduce(
        (sum, b) => sum + computeFreeSlots(b.id, 45, 5, todayJ.jy, todayJ.jm, todayJ.jd).length,
        0
      );

      const atRisk = customersEnriched.filter((e) => e.metrics.lifecycle === 'at_risk');
      const atRiskNoBooking = atRisk.filter((e) => !hasFutureBooking(e.customer.id));

      const newLast30d = customers.filter(
        (c) => Date.now() - new Date(c.createdAt).getTime() < 30 * 86400000
      );

      const topActions = [];
      if (atRiskNoBooking.length)
        topActions.push({
          id: 'at-risk',
          title: `ارسال پیشنهاد به ${faNum(atRiskNoBooking.length)} مشتری در معرض ریزش`,
          detail: 'بیشترین اثر روی بازگشت و درآمد',
          tone: 'warn'
        });
      if (pending.length)
        topActions.push({
          id: 'confirm',
          title: `تأیید ${faNum(pending.length)} نوبت در انتظار`,
          detail: 'رزروهای آنلاین که هنوز تأیید نشده‌اند',
          tone: 'info'
        });
      if (emptySlots > 0)
        topActions.push({
          id: 'slots',
          title: `پر کردن ${faNum(emptySlots)} اسلات خالی امروز`,
          detail: 'پیشنهاد به مشتریان منطبق از صف انتظار',
          tone: 'good'
        });

      return {
        todayAppts,
        pending,
        confirmedCount,
        expectedRevenue,
        emptySlots,
        atRisk,
        atRiskNoBooking,
        newLast30d,
        topActions
      };
    }

    /* ---------- actions ---------- */
    function updateBusiness(patch) {
      setState((s) => ({ ...s, business: { ...s.business, ...patch } }));
    }

    function updateScheduling(patch) {
      setState((s) => ({
        ...s,
        business: { ...s.business, scheduling: { ...s.business.scheduling, ...patch } }
      }));
    }

    function updateWorkingHours(hours) {
      setState((s) => ({ ...s, business: { ...s.business, workingHours: hours } }));
    }

    function addService(service) {
      setState((s) => ({
        ...s,
        services: [...s.services, { ...service, id: 's' + Date.now() }]
      }));
    }

    function updateService(id, patch) {
      setState((s) => ({
        ...s,
        services: s.services.map((x) => (x.id === id ? { ...x, ...patch } : x))
      }));
    }

    function removeService(id) {
      setState((s) => ({ ...s, services: s.services.filter((x) => x.id !== id) }));
    }

    function addBarber(barber) {
      setState((s) => ({
        ...s,
        barbers: [...s.barbers, { ...barber, id: 'b' + Date.now() }]
      }));
    }

    function updateBarber(id, patch) {
      setState((s) => ({
        ...s,
        barbers: s.barbers.map((x) => (x.id === id ? { ...x, ...patch } : x))
      }));
    }

    function removeBarber(id) {
      setState((s) => ({ ...s, barbers: s.barbers.filter((x) => x.id !== id) }));
    }

    function ensureCustomer({ name, mobile }) {
      const norm = normalizeMobile(mobile);
      const existing = customers.find((c) => normalizeMobile(c.mobile) === norm);
      if (existing) {
        if (name && existing.name !== name) {
          setState((s) => ({
            ...s,
            customers: s.customers.map((c) => (c.id === existing.id ? { ...c, name } : c))
          }));
        }
        return existing;
      }
      const customer = {
        id: 'c' + Date.now(),
        name,
        mobile: norm,
        createdAt: new Date().toISOString(),
        visits: []
      };
      setState((s) => ({ ...s, customers: [...s.customers, customer] }));
      return customer;
    }

    function bookAppointment({ customerId, barberId, serviceId, startAt, status = 'confirmed' }) {
      const svc = serviceById(serviceId);
      const startMs = new Date(startAt).getTime();
      const endMs = startMs + ((svc?.durationMinutes || 30) + (svc?.bufferMinutes ?? 5)) * 60000;
      const conflict = appointments.some(
        (a) => a.barberId === barberId && ACTIVE.includes(a.status) &&
          overlaps(startMs, endMs, new Date(a.startAt).getTime(), appointmentEnd(state, a))
      );
      if (conflict) return { ok: false, error: 'این بازه‌ی زمانی هم‌اکنون رزرو شده است.' };

      const appointment = {
        id: 'a' + Date.now(),
        tenantId: 'shop-001',
        customerId,
        barberId,
        serviceId,
        startAt: new Date(startAt).toISOString(),
        status,
        createdAt: new Date().toISOString(),
        source: 'manual'
      };
      setState((s) => ({ ...s, appointments: [...s.appointments, appointment] }));
      return { ok: true, appointment };
    }

    function updateAppointmentStatus(id, status) {
      setState((s) => {
        const appt = s.appointments.find((a) => a.id === id);
        if (!appt) return s;
        const next = s.appointments.map((a) => (a.id === id ? { ...a, status } : a));

        // تکمیل مراجعه → ثبت در تاریخچه‌ی مشتری (بازخورد چرخه‌ی عمر)
        if (status === 'completed') {
          const svc = s.services.find((x) => x.id === appt.serviceId);
          const customersNext = s.customers.map((c) => {
            if (c.id !== appt.customerId) return c;
            const visits = [
              ...(c.visits || []),
              {
                date: new Date().toISOString(),
                serviceId: appt.serviceId,
                barberId: appt.barberId,
                revenueRial: svc?.priceRial || 0
              }
            ];
            return { ...c, visits };
          });
          return { ...s, appointments: next, customers: customersNext };
        }
        return { ...s, appointments: next };
      });
    }

    function rescheduleAppointment(id, newStartAt) {
      setState((s) => ({
        ...s,
        appointments: s.appointments.map((a) =>
          a.id === id ? { ...a, startAt: new Date(newStartAt).toISOString() } : a
        )
      }));
    }

    function sendMessage({ to, template, text, channel = 'sms' }) {
      setState((s) => ({
        ...s,
        messages: [
          {
            id: 'm' + Date.now(),
            to,
            template,
            text,
            channel,
            status: 'sent',
            createdAt: new Date().toISOString()
          },
          ...s.messages
        ]
      }));
    }

    function resetData() {
      setState(buildSeed());
    }

    /* ---------- message templating (شبیه‌سازی SMS) ---------- */
    function buildMessage(customer, template, extra = {}) {
      const vars = {
        '{{customerName}}': customer.name,
        '{{businessName}}': business.name,
        '{{bookingUrl}}': business.bookingUrl,
        ...extra
      };
      const tpl = {
        confirm: `{{customerName}} عزیز، نوبت شما در {{businessName}} ثبت شد. 🗓 {{date}} ساعت {{time}}`,
        remind_24h: `یادآوری: فردا ساعت {{time}} نوبت شما در {{businessName}} است.`,
        rebooking: `{{customerName}} عزیز، وقت اصلاح شما نزدیک است! برای رزرو: {{bookingUrl}}`
      }[template];
      return Object.entries(vars).reduce((txt, [k, v]) => txt.replaceAll(k, String(v)), tpl || '');
    }

    function offerToCustomer(customerId) {
      const customer = customerById(customerId);
      if (!customer) return;
      const text = buildMessage(customer, 'rebooking');
      sendMessage({ to: customer.mobile, template: 'rebooking', text });
    }

    return {
      state,
      business,
      services,
      barbers,
      customers,
      appointments,
      messages,
      customersEnriched,
      serviceById,
      barberById,
      customerById,
      getSlots,
      dashboardStats: dashboardStats(),
      hasFutureBooking,
      // actions
      updateBusiness,
      updateScheduling,
      updateWorkingHours,
      addService,
      updateService,
      removeService,
      addBarber,
      updateBarber,
      removeBarber,
      ensureCustomer,
      bookAppointment,
      updateAppointmentStatus,
      rescheduleAppointment,
      sendMessage,
      offerToCustomer,
      resetData
    };
  }, [state]);

  return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>;
}

export function useStore() {
  const ctx = useContext(StoreContext);
  if (!ctx) throw new Error('useStore must be used within AppProvider');
  return ctx;
}

export { ACTIVE, REVENUE_STATUSES, timeOfFa, jalaliStr, jalaliOf };
