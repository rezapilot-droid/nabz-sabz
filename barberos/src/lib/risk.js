// موتور امتیاز ریزش و چرخه‌ی عمر مشتری — مطابق BarberOS Workflow v2.0 (بخش ۷ و ۸)

const DAY = 86400000;

export function median(arr) {
  if (!arr || !arr.length) return null;
  const s = [...arr].sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}

export function mode(arr) {
  if (!arr || !arr.length) return null;
  const counts = {};
  let best = null;
  let bestCount = 0;
  for (const v of arr) {
    counts[v] = (counts[v] || 0) + 1;
    if (counts[v] > bestCount) {
      bestCount = counts[v];
      best = v;
    }
  }
  return best;
}

// متریک کامل یک مشتری؛ visits آرایه‌ی {date, serviceId, barberId, revenueRial} (صعودی)
export function customerMetrics(
  customer,
  { vipThreshold = 8, churnGraceDays = 14, churnDays = 180, shopMedian = null } = {}
) {
  const visits = [...(customer.visits || [])].sort(
    (a, b) => new Date(a.date) - new Date(b.date)
  );
  const visitCount = visits.length;
  const now = Date.now();

  let lastVisit = null;
  const intervals = [];
  let totalSpend = 0;
  const barberIds = [];
  const serviceIds = [];

  visits.forEach((v, i) => {
    const t = new Date(v.date).getTime();
    lastVisit = t;
    totalSpend += v.revenueRial || 0;
    if (v.barberId) barberIds.push(v.barberId);
    if (v.serviceId) serviceIds.push(v.serviceId);
    if (i > 0) intervals.push((t - new Date(visits[i - 1].date).getTime()) / DAY);
  });

  const m = median(intervals);
  const mean = intervals.length
    ? intervals.reduce((a, b) => a + b, 0) / intervals.length
    : null;
  const elapsed = lastVisit ? (now - lastVisit) / DAY : null;

  // Risk Score: (elapsed − m) / m ، clamp [0,1] — فقط با ≥۳ مراجعه
  let risk = null;
  let riskSource = 'insufficient-data';
  if (m != null && elapsed != null) {
    risk = Math.max(0, Math.min(1, (elapsed - m) / m));
    riskSource = 'formula';
  } else if (elapsed != null && shopMedian != null && visitCount > 0) {
    if (elapsed > 2 * shopMedian) {
      risk = 0.5;
      riskSource = 'fallback';
    }
  }

  // tier (بُعد ارزش)
  const tier = visitCount >= vipThreshold ? 'vip' : 'regular';

  // lifecycle (بُعد عمر)
  let lifecycle = 'new';
  if (visitCount >= 1) {
    if (elapsed != null && elapsed > churnDays) lifecycle = 'churned';
    else if (m != null && elapsed != null && elapsed > m + churnGraceDays) lifecycle = 'inactive';
    else if (risk != null && risk >= 0.45) lifecycle = 'at_risk';
    else lifecycle = 'active';
  }

  return {
    visitCount,
    medianInterval: m,
    meanInterval: mean,
    elapsedDays: elapsed,
    risk,
    riskSource,
    riskBand: riskBand(risk),
    tier,
    lifecycle,
    totalSpend,
    lastVisit,
    favoriteBarberId: mode(barberIds),
    favoriteServiceId: mode(serviceIds)
  };
}

export function riskBand(risk) {
  if (risk == null) return null;
  if (risk < 0.15) return 'low';
  if (risk < 0.45) return 'medium';
  if (risk < 0.65) return 'high';
  if (risk <= 0.8) return 'very-high';
  return 'critical';
}

export const RISK_BAND_LABEL = {
  low: 'کم',
  medium: 'متوسط',
  high: 'زیاد',
  'very-high': 'خیلی زیاد',
  critical: 'بحرانی'
};

export const LIFECYCLE_LABEL = {
  new: 'جدید',
  active: 'فعال',
  at_risk: 'در معرض ریزش',
  inactive: 'غیرفعال',
  churned: 'ریزش‌کرده'
};
