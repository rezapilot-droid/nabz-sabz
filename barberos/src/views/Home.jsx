import { Scissors, CalendarCheck2, UserRound, ShieldCheck, BellRing, BarChart3, Sparkles } from 'lucide-react';
import { useStore } from '../lib/store';

export default function Home({ onCustomer, onAdmin, onMy }) {
  const { business } = useStore();

  return (
    <div>
      <div className="hero">
        <h1>
          <em>{business.name}</em> — آرایشگاه مردانه‌ی هوشمند
        </h1>
        <p>
          رزرو آنلاین نوبت، یادآوری خودکار و مدیریت کامل آرایشگاه؛ از انتخاب خدمت و آرایشگر تا
          تقویم شمسی و پنل مدیریت.
        </p>
        <div className="role-cards">
          <div className="role-card" onClick={onCustomer}>
            <div className="role-icon">
              <Scissors size={26} />
            </div>
            <h3>رزرو نوبت</h3>
            <p>خدمت و آرایشگر را انتخاب کنید و در چند ثانیه نوبت بگیرید.</p>
          </div>
          <div className="role-card" onClick={onAdmin}>
            <div className="role-icon">
              <ShieldCheck size={26} />
            </div>
            <h3>پنل مدیریت</h3>
            <p>داشبورد، نوبت‌ها، مشتریان، خدمات و تنظیمات آرایشگاه.</p>
          </div>
        </div>
        <p style={{ marginTop: 18 }}>
          <button className="btn btn-ghost" onClick={onMy}>
            <UserRound size={16} /> نوبت‌های من
          </button>
        </p>
      </div>

      <div className="feature-strip">
        <div className="f">
          <CalendarCheck2 size={22} />
          <p>رزرو آنلاین با تقویم شمسی</p>
        </div>
        <div className="f">
          <BellRing size={22} />
          <p>یادآوری خودکار نوبت</p>
        </div>
        <div className="f">
          <BarChart3 size={22} />
          <p>گزارش و تحلیل هوشمند</p>
        </div>
        <div className="f">
          <Sparkles size={22} />
          <p>تشخیص مشتری در معرض ریزش</p>
        </div>
      </div>
    </div>
  );
}
