// داده‌ی نمونه (Seed) — یک آرایشگاه نمونه با مشتریان، تاریخچه‌ی مراجعه و نوبت‌های فعال
// تاریخ‌ها نسبت به «امروز» (به وقت تهران) تولید می‌شوند تا داشبورد همیشه زنده باشد.

import { todayTehran, atTehran } from './format';

const DAY = 86400000;

export const SERVICES = [
  { id: 's1', name: 'کوتاهی مو', durationMinutes: 45, bufferMinutes: 5, priceRial: 4500000 },
  { id: 's2', name: 'اصلاح ریش و صورت', durationMinutes: 30, bufferMinutes: 5, priceRial: 3200000 },
  { id: 's3', name: 'پکیج کوتاهی + اصلاح', durationMinutes: 60, bufferMinutes: 10, priceRial: 6500000 },
  { id: 's4', name: 'رنگ و مش', durationMinutes: 75, bufferMinutes: 10, priceRial: 9000000 },
  { id: 's5', name: 'شستشو و فرم‌دهی', durationMinutes: 25, bufferMinutes: 5, priceRial: 2800000 }
];

export const BARBERS = [
  { id: 'b1', name: 'آرمان راد', skills: ['s1', 's2', 's3', 's4', 's5'] },
  { id: 'b2', name: 'سینا کاظمی', skills: ['s1', 's2', 's3'] },
  { id: 'b3', name: 'مهدی توکلی', skills: ['s1', 's3', 's4', 's5'] }
];

const SERVICE_PRICE = Object.fromEntries(SERVICES.map((s) => [s.id, s.priceRial]));

const DEFAULT_HOURS = {
  0: { open: '09:00', close: '21:00' }, // شنبه
  1: { open: '09:00', close: '21:00' },
  2: { open: '09:00', close: '21:00' },
  3: { open: '09:00', close: '21:00' },
  4: { open: '09:00', close: '21:00' },
  5: { open: '09:00', close: '22:00' }, // پنجشنبه
  6: { closed: true } // جمعه
};

export const DEFAULT_BUSINESS = {
  id: 'shop-001',
  name: 'رویال باربر',
  city: 'تهران',
  phone: '021-12345678',
  slogan: 'اصلاح و استایل، با نظم و حرفه‌ای',
  workingHours: DEFAULT_HOURS,
  scheduling: {
    slotGranularityMinutes: 15,
    defaultBufferMinutes: 5,
    minLeadMinutes: 30,
    maxAdvanceDays: 30,
    minNoticeCancellationHours: 3,
    noShowGraceMinutes: 15
  },
  customer: {
    vipVisitThreshold: 8,
    churnGraceDays: 14,
    churnDays: 180
  },
  payment: { mode: 'pay_at_visit' }
};

// ساخت تاریخچه‌ی مراجعه با الگوی مشخص
function history({ n, interval, lastAgo, barberIds, serviceIds }) {
  const visits = [];
  const now = Date.now();
  const last = now - lastAgo * DAY;
  for (let i = n - 1; i >= 0; i -= 1) {
    const t = last - i * interval * DAY;
    const serviceId = serviceIds[i % serviceIds.length];
    const barberId = barberIds[i % barberIds.length];
    visits.push({
      date: new Date(t).toISOString(),
      serviceId,
      barberId,
      revenueRial: SERVICE_PRICE[serviceId]
    });
  }
  return visits;
}

function makeCustomers() {
  const rows = [
    // id, name, mobile, الگوی مراجعه
    ['c1', 'امیرحسین نادری', '09121112233', { n: 12, interval: 21, lastAgo: 8, barberIds: ['b1', 'b1', 'b2'], serviceIds: ['s3', 's1', 's3'] }],
    ['c2', 'رضا محمدی', '09122223344', { n: 5, interval: 20, lastAgo: 30, barberIds: ['b2'], serviceIds: ['s1', 's2'] }],
    ['c3', 'محمد کریمی', '09123334455', { n: 6, interval: 25, lastAgo: 12, barberIds: ['b3', 'b1'], serviceIds: ['s1', 's3'] }],
    ['c4', 'حسین شریفی', '09124445566', { n: 4, interval: 18, lastAgo: 45, barberIds: ['b3'], serviceIds: ['s4', 's1'] }],
    ['c5', 'علی رستمی', '09351117788', { n: 5, interval: 20, lastAgo: 60, barberIds: ['b1', 'b2'], serviceIds: ['s2', 's1'] }],
    ['c6', 'بهرام قاسمی', '09125558899', { n: 4, interval: 25, lastAgo: 220, barberIds: ['b2'], serviceIds: ['s1'] }],
    ['c7', 'سینا احمدی', '09901234567', { n: 1, interval: 0, lastAgo: 3, barberIds: ['b2'], serviceIds: ['s1'] }],
    ['c8', 'نوید صالحی', '09912345678', { n: 1, interval: 0, lastAgo: 1, barberIds: ['b2'], serviceIds: ['s2'] }],
    ['c9', 'پارسا رحیمی', '09126661122', { n: 3, interval: 28, lastAgo: 20, barberIds: ['b1'], serviceIds: ['s1', 's5'] }],
    ['c10', 'کیان مرادی', '09127772233', { n: 8, interval: 22, lastAgo: 26, barberIds: ['b3', 'b2'], serviceIds: ['s3', 's1'] }],
    ['c11', 'آرش قنبری', '09128883344', { n: 7, interval: 24, lastAgo: 5, barberIds: ['b3', 'b1'], serviceIds: ['s1', 's3'] }],
    ['c12', 'سامان جعفری', '09129994455', { n: 10, interval: 19, lastAgo: 9, barberIds: ['b1'], serviceIds: ['s3', 's1'] }],
    ['c13', 'مصطفی رضوی', '09121117766', { n: 4, interval: 15, lastAgo: 2, barberIds: ['b1', 'b2'], serviceIds: ['s1', 's2'] }],
    ['c14', 'فرهاد نادری', '09122228877', { n: 3, interval: 30, lastAgo: 6, barberIds: ['b3'], serviceIds: ['s5', 's1'] }]
  ];

  return rows.map(([id, name, mobile, h]) => {
    const visits = history(h);
    const createdAt = visits.length ? visits[0].date : new Date().toISOString();
    return { id, name, mobile, createdAt, visits };
  });
}

function makeAppointments() {
  const { gy, gm, gd } = todayTehran();
  const T = (hh, mm = 0) => atTehran(gy, gm, gd, hh, mm);
  const Tp1 = (hh, mm = 0) => atTehran(gy, gm, gd + 1, hh, mm);

  // [barberId, time, customerId, serviceId, status]
  const today = [
    ['b1', [9, 30], 'c2', 's3', 'confirmed'],
    ['b1', [11, 0], 'c1', 's3', 'confirmed'],
    ['b1', [13, 0], 'c10', 's1', 'requested'],
    ['b1', [16, 0], 'c5', 's3', 'confirmed'],
    ['b2', [8, 30], 'c13', 's1', 'completed'],
    ['b2', [10, 0], 'c3', 's1', 'confirmed'],
    ['b2', [10, 45], 'c9', 's2', 'checked_in'],
    ['b2', [12, 0], 'c7', 's1', 'confirmed'],
    ['b2', [14, 30], 'c8', 's2', 'requested'],
    ['b3', [8, 30], 'c14', 's5', 'completed'],
    ['b3', [9, 0], 'c11', 's1', 'in_progress'],
    ['b3', [11, 30], 'c12', 's3', 'confirmed'],
    ['b3', [15, 0], 'c4', 's4', 'confirmed']
  ];

  const tomorrow = [
    ['b1', [10, 0], 'c2', 's3', 'confirmed'],
    ['b1', [11, 30], 'c9', 's1', 'confirmed'],
    ['b2', [10, 0], 'c1', 's3', 'confirmed'],
    ['b2', [12, 30], 'c6', 's1', 'confirmed'],
    ['b3', [11, 0], 'c11', 's1', 'confirmed'],
    ['b3', [15, 0], 'c10', 's2', 'confirmed']
  ];

  let idc = 1;
  const build = (rows, dayFn) =>
    rows.map(([barberId, [hh, mm], customerId, serviceId, status]) => ({
      id: 'a' + idc++,
      tenantId: 'shop-001',
      customerId,
      barberId,
      serviceId,
      startAt: dayFn(hh, mm),
      status,
      createdAt: new Date().toISOString(),
      source: status === 'requested' ? 'online' : 'mixed'
    }));

  return [...build(today, T), ...build(tomorrow, Tp1)];
}

export function buildSeed() {
  return {
    version: 2,
    business: DEFAULT_BUSINESS,
    services: SERVICES,
    barbers: BARBERS,
    customers: makeCustomers(),
    appointments: makeAppointments(),
    messages: []
  };
}
