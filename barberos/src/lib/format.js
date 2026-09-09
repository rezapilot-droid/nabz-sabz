import { g2j, JALALI_MONTHS, WEEKDAYS } from './jalali';

const FA_DIGITS = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];

export function faNum(input) {
  return String(input).replace(/[0-9]/g, (d) => FA_DIGITS[Number(d)]);
}

export function group(num) {
  return String(num).replace(/\B(?=(\d{3})+(?!\d))/g, '،');
}

// ریال → تومان با جداکننده هزارگان و ارقام فارسی
export function toToman(rial) {
  const toman = Math.round((rial || 0) / 10);
  return faNum(group(toman)) + ' تومان';
}

function pad2(n) {
  return String(n).padStart(2, '0');
}

// اجزای مدنی تاریخ در منطقه‌ی تهران (مستقل از تایم‌زون سرور)
function tehranCivil(iso) {
  const d = new Date(iso);
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Tehran',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(d);
  const [gy, gm, gd] = parts.split('-').map(Number);
  return { gy, gm, gd };
}

export function jalaliOf(iso) {
  const { gy, gm, gd } = tehranCivil(iso);
  return g2j(gy, gm, gd);
}

export function timeOf(iso) {
  const d = new Date(iso);
  return new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Asia/Tehran',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  }).format(d);
}

export function timeOfFa(iso) {
  return faNum(timeOf(iso));
}

export function jalaliStr(iso) {
  const { jy, jm, jd } = jalaliOf(iso);
  return faNum(`${jy}/${pad2(jm)}/${pad2(jd)}`);
}

export function jalaliLong(iso) {
  const { jy, jm, jd } = jalaliOf(iso);
  const { gy, gm, gd } = tehranCivil(iso);
  const weekday = new Date(Date.UTC(gy, gm - 1, gd)).getUTCDay();
  const iranianDow = (weekday + 1) % 7;
  return `${WEEKDAYS[iranianDow]} ${faNum(jd)} ${JALALI_MONTHS[jm - 1]} ${faNum(jy)}`;
}

// «امروز» به وقت تهران (میلادی برای مقایسه‌ی روز)
export function todayTehran() {
  return tehranCivil(Date.now());
}

export function todayJalali() {
  const { gy, gm, gd } = tehranCivil(Date.now());
  return g2j(gy, gm, gd);
}

// آیا تاریخ (ISO) در روزِ امروزِ تهران است؟
export function isToday(iso) {
  const { gy, gm, gd } = tehranCivil(iso);
  const t = todayTehran();
  return gy === t.gy && gm === t.gm && gd === t.gd;
}

// آیا تاریخ (ISO) در روزِ فرداِ تهران است؟
export function isTomorrow(iso) {
  return startOfTehranDay(iso) === startOfTehranDay(Date.now() + 86400000);
}

// شروع روز (به وقت تهران) برای مقایسه‌های روزانه
export function startOfTehranDay(iso) {
  const { gy, gm, gd } = tehranCivil(iso);
  return Date.UTC(gy, gm - 1, gd) - 3.5 * 3600 * 1000;
}

// ساخت timestamp میلادی (ISO) از ساعت محلی تهران
export function atTehran(gy, gm, gd, hh, mm = 0) {
  const utc = Date.UTC(gy, gm - 1, gd, hh, mm, 0, 0);
  return new Date(utc - 3.5 * 3600 * 1000).toISOString();
}

// نرمال‌سازی شماره موبایل ایران
export function normalizeMobile(input) {
  let m = String(input || '').replace(/[^\d]/g, '');
  if (m.startsWith('98')) m = '0' + m.slice(2);
  if (m.startsWith('+98')) m = '0' + m.slice(3);
  return m;
}

export function minutesOf(hhmm) {
  const [h, m] = hhmm.split(':').map(Number);
  return h * 60 + (m || 0);
}
