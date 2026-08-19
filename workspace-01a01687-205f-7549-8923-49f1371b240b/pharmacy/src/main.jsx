import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  ArrowLeft, BadgeCheck, Bell, Bot, Check, ChevronLeft, CircleUserRound,
  Clock3, Heart, HeartPulse, Headphones, Menu, MessageCircle, Minus,
  PackageCheck, PhoneCall, Pill, Plus, Search, ShieldCheck, ShoppingBag,
  Sparkles, Star, Stethoscope, Truck, Upload, UserRound, Video, X, Zap,
  MapPin, Send, FileText, Leaf, Navigation, TimerReset, ScanLine,
  ClipboardCheck, AlertCircle
} from 'lucide-react';
import '@fontsource/vazirmatn/300.css';
import '@fontsource/vazirmatn/400.css';
import '@fontsource/vazirmatn/500.css';
import '@fontsource/vazirmatn/600.css';
import '@fontsource/vazirmatn/700.css';
import '@fontsource/vazirmatn/800.css';
import './styles.css';

const categories = [
  { id: 'vitamin', title: 'مکمل و ویتامین', subtitle: '+۴۸۰ محصول', icon: Pill, tone: 'amber' },
  { id: 'skin', title: 'پوست و مو', subtitle: '+۶۳۰ محصول', icon: Sparkles, tone: 'rose' },
  { id: 'mom', title: 'مادر و کودک', subtitle: '+۳۲۰ محصول', icon: Heart, tone: 'violet' },
  { id: 'medical', title: 'تجهیزات پزشکی', subtitle: '+۲۴۰ محصول', icon: HeartPulse, tone: 'cyan' },
  { id: 'hygiene', title: 'بهداشت شخصی', subtitle: '+۵۱۰ محصول', icon: Leaf, tone: 'green' },
  { id: 'rx', title: 'نسخه آنلاین', subtitle: 'آپلود و بررسی', icon: FileText, tone: 'blue' },
];

const products = [
  { id: 1, name: 'کپسول امگا ۳ پریمیوم', brand: 'یوروویتال', category: 'vitamin', price: 286000, oldPrice: 325000, discount: 12, rating: 4.8, reviews: 124, color: '#f2b84b', type: 'bottle', label: 'Omega 3', sub: '60 CAPSULES', badge: 'پرفروش' },
  { id: 2, name: 'سرم آبرسان هیالورونیک', brand: 'لافارر', category: 'skin', price: 418000, oldPrice: 475000, discount: 15, rating: 4.9, reviews: 89, color: '#54b7c7', type: 'dropper', label: 'HYDRA', sub: 'HYALURONIC ACID', badge: 'پیشنهاد ویژه' },
  { id: 3, name: 'قرص مولتی ویتامین بانوان', brand: 'ویتاپرا', category: 'vitamin', price: 342000, oldPrice: null, discount: 0, rating: 4.7, reviews: 76, color: '#db6f8d', type: 'box', label: 'VITA WOMEN', sub: '30 TABLETS', badge: 'محبوب' },
  { id: 4, name: 'ضد آفتاب فیوژن واتر SPF50', brand: 'سان‌سیف', category: 'skin', price: 395000, oldPrice: 460000, discount: 14, rating: 4.8, reviews: 203, color: '#ed9160', type: 'tube', label: 'SUN SAFE', sub: 'SPF 50+', badge: 'پرفروش' },
  { id: 5, name: 'دستگاه فشار خون دیجیتال', brand: 'زنیت‌مد', category: 'medical', price: 2180000, oldPrice: 2380000, discount: 8, rating: 4.6, reviews: 42, color: '#3b8ca8', type: 'device', label: 'ZENITH', sub: 'HEALTH MONITOR', badge: 'ارسال رایگان' },
  { id: 6, name: 'شامپو تقویت‌کننده مو', brand: 'سریتا', category: 'skin', price: 257000, oldPrice: null, discount: 0, rating: 4.7, reviews: 98, color: '#64a781', type: 'bottle', label: 'CERITA', sub: 'HAIR CARE', badge: 'جدید' },
  { id: 7, name: 'قطره ویتامین D3 کودک', brand: 'ویواکیدز', category: 'mom', price: 168000, oldPrice: 184000, discount: 9, rating: 4.9, reviews: 137, color: '#937bc8', type: 'dropper', label: 'D3 KIDS', sub: '400 IU', badge: 'انتخاب مادران' },
  { id: 8, name: 'مسواک برقی پاکت‌پرو', brand: 'اورال‌کلین', category: 'hygiene', price: 1240000, oldPrice: 1390000, discount: 11, rating: 4.5, reviews: 31, color: '#4fa8dd', type: 'device', label: 'ORAL+', sub: 'SONIC CLEAN', badge: 'هوشمند' },
];

const toFa = (value) => new Intl.NumberFormat('fa-IR').format(value);

function ProductVisual({ product, small = false }) {
  return (
    <div className={`product-visual ${small ? 'small' : ''}`} style={{'--product': product.color}}>
      <span className="visual-glow" /><span className="visual-shadow" />
      {product.type === 'dropper' && <span className="dropper-cap" />}
      <div className={`product-pack ${product.type}`}>
        {product.type === 'tube' && <span className="tube-cap" />}
        {product.type === 'device' && <span className="device-screen"><HeartPulse size={small ? 14 : 22} /></span>}
        <span className="pack-cross">+</span><strong>{product.label}</strong><small>{product.sub}</small><i />
      </div>
    </div>
  );
}

function App() {
  const [cart, setCart] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [activeCategory, setActiveCategory] = useState('all');
  const [showAll, setShowAll] = useState(false);
  const [search, setSearch] = useState('');
  const [cartOpen, setCartOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [consultOpen, setConsultOpen] = useState(false);
  const [rxOpen, setRxOpen] = useState(false);
  const [locationOpen, setLocationOpen] = useState(false);
  const [quickView, setQuickView] = useState(null);
  const [toast, setToast] = useState('');
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState([
    { from: 'bot', text: 'سلام! من دستیار سلامت نبض‌سبز هستم. برای انتخاب نوع مشاوره راهنمایی‌تان می‌کنم 🌿' }
  ]);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(''), 2600);
    return () => clearTimeout(t);
  }, [toast]);

  useEffect(() => {
    const close = (e) => { if (e.key === 'Escape') { setCartOpen(false); setConsultOpen(false); setRxOpen(false); setQuickView(null); setLocationOpen(false); }};
    window.addEventListener('keydown', close);
    return () => window.removeEventListener('keydown', close);
  }, []);

  const filtered = useMemo(() => products.filter(p => {
    const catMatch = activeCategory === 'all' || p.category === activeCategory;
    const searchMatch = !search.trim() || `${p.name} ${p.brand} ${p.label}`.toLowerCase().includes(search.trim().toLowerCase());
    return catMatch && searchMatch;
  }), [activeCategory, search]);

  const cartCount = cart.reduce((sum, item) => sum + item.qty, 0);
  const cartTotal = cart.reduce((sum, item) => sum + item.price * item.qty, 0);

  function addToCart(product) {
    setCart(prev => {
      const found = prev.find(x => x.id === product.id);
      return found ? prev.map(x => x.id === product.id ? {...x, qty: x.qty + 1} : x) : [...prev, {...product, qty: 1}];
    });
    setToast(`«${product.name}» به سبد خرید اضافه شد`);
  }
  function changeQty(id, d) { setCart(prev => prev.map(x => x.id === id ? {...x, qty: x.qty + d} : x).filter(x => x.qty > 0)); }
  function toggleFav(id) { setFavorites(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]); }
  function sendMessage(text = chatInput) {
    if (!text.trim()) return;
    setMessages(prev => [...prev, {from:'user', text}, {from:'bot', text:'متوجه شدم. برای حفظ سلامت شما، یک پزشک عمومی آنلاین در کمتر از ۳ دقیقه به گفت‌وگو می‌پیوندد. آیا مایلید تماس متنی باشد یا تصویری؟'}]);
    setChatInput('');
  }
  const scrollTo = (id) => { document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' }); setMobileOpen(false); };

  return (
    <div className="app-shell">
      <div className="announcement">
        <div className="container announcement-inner">
          <p><Zap size={15} fill="currentColor" /> ارسال اکسپرس رایگان برای سفارش‌های بالای ۵۰۰ هزار تومان</p>
          <div><span><Clock3 size={14}/> باز و پاسخگو؛ ۲۴ ساعته</span><button onClick={() => setLocationOpen(true)}><MapPin size={14}/> انتخاب آدرس</button></div>
        </div>
      </div>

      <header><div className="container nav">
        <button className="mobile-menu icon-button" aria-label="باز کردن منو" onClick={() => setMobileOpen(!mobileOpen)}><Menu /></button>
        <button className="logo" onClick={() => scrollTo('home')} aria-label="نبض سبز">
          <span className="logo-mark"><HeartPulse /><i /></span><span><strong>نبض‌سبز</strong><small>داروخانه شبانه‌روزی</small></span>
        </button>
        <nav className={mobileOpen ? 'open' : ''}>
          <button onClick={() => scrollTo('products')}>فروشگاه</button><button onClick={() => setRxOpen(true)}>ارسال نسخه</button>
          <button onClick={() => scrollTo('consult')}>مشاوره آنلاین</button><button onClick={() => scrollTo('services')}>خدمات سلامت</button>
          <button onClick={() => scrollTo('magazine')}>مجله سلامت</button>
        </nav>
        <div className="nav-actions">
          <button className="consult-mini" onClick={() => setConsultOpen(true)}><Headphones size={18}/><span>مشاوره فوری</span></button>
          <button className="icon-button hide-mobile" aria-label="حساب کاربری" onClick={() => setToast('ورود و عضویت به‌زودی فعال می‌شود')}><CircleUserRound /></button>
          <button className="icon-button cart-button" aria-label="سبد خرید" onClick={() => setCartOpen(true)}><ShoppingBag />{cartCount > 0 && <b>{toFa(cartCount)}</b>}</button>
        </div>
      </div></header>

      <main>
        <section className="hero" id="home">
          <span className="hero-orb one"/><span className="hero-orb two"/>
          <div className="container hero-grid">
            <div className="hero-copy">
              <div className="eyebrow"><span className="live-dot"/> پزشک و داروساز، همین حالا آنلاین‌اند</div>
              <h1>سلامتی، همین نزدیکی‌ست؛<br/><em>سریع، مطمئن، شبانه‌روزی.</em></h1>
              <p>از مشاوره تخصصی تا تحویل دارو و محصولات سلامت؛ نبض‌سبز همیشه و همه‌جا کنار شماست.</p>
              <div className="hero-search"><Search /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="جستجوی نام محصول، برند یا دسته‌بندی..." /><button onClick={() => scrollTo('products')}>جستجو</button></div>
              <div className="hot-searches"><span>جستجوهای محبوب:</span><button onClick={()=>{setSearch('امگا');scrollTo('products')}}>امگا ۳</button><button onClick={()=>{setSearch('آبرسان');scrollTo('products')}}>آبرسان</button><button onClick={()=>{setSearch('فشار خون');scrollTo('products')}}>فشار خون</button></div>
              <div className="hero-actions"><button className="primary-btn" onClick={() => setRxOpen(true)}><Upload size={19}/> ارسال نسخه پزشک <ArrowLeft size={18}/></button><button className="ghost-btn" onClick={() => setConsultOpen(true)}><MessageCircle size={19}/> مشاوره آنلاین</button></div>
              <div className="trust-row">
                <div><span><ShieldCheck /></span><p><strong>خرید امن</strong><small>مجوز رسمی وزارت بهداشت</small></p></div>
                <div><span><Truck /></span><p><strong>تحویل سریع</strong><small>میانگین ۴۵ دقیقه</small></p></div>
                <div><span><Headphones /></span><p><strong>پاسخگویی ۲۴/۷</strong><small>بدون تعطیلی</small></p></div>
              </div>
            </div>
            <div className="hero-showcase" aria-label="محصولات سلامت نبض سبز">
              <div className="cross-pattern">+</div><div className="showcase-ring r1"/><div className="showcase-ring r2"/>
              <div className="phone-card">
                <div className="phone-top"><span/><span/></div><div className="mini-head"><div className="mini-logo"><HeartPulse/></div><Bell size={15}/></div>
                <p className="mini-hello">صبح بخیر نیلوفر 👋</p><strong className="mini-title">امروز چطور می‌تونیم کمکت کنیم؟</strong>
                <div className="mini-search"><Search size={13}/> جستجوی محصولات...</div><div className="mini-banner"><span><small>تخفیف تا</small><b>۳۰٪</b><i>برای پوست تو</i></span><Sparkles /></div>
                <div className="mini-products">{products.slice(0,2).map(p => <div key={p.id}><ProductVisual product={p} small/><small>{p.brand}</small><b>{toFa(p.price/1000)} ت</b></div>)}</div>
                <div className="phone-nav"><HeartPulse/><Search/><ShoppingBag/><UserRound/></div>
              </div>
              <div className="floating-card pharmacist"><span className="avatar"><img src="/doctor.jpg" alt="دکتر نادری"/></span><p><small><i/> داروساز آنلاین</small><strong>دکتر سارا نادری</strong><b>پاسخ در کمتر از ۲ دقیقه</b></p><button onClick={() => setConsultOpen(true)}><PhoneCall size={16}/></button></div>
              <div className="floating-card delivered"><span><PackageCheck/></span><p><strong>سفارش تحویل شد!</strong><small>۲۶ دقیقه زودتر از موعد</small></p><Check/></div>
              <div className="floating-card rating-card"><Star fill="currentColor"/><strong>۴.۹</strong><small>رضایت مشتریان</small></div>
            </div>
          </div>
        </section>

        <section className="quick-strip"><div className="container quick-grid">
          <button onClick={() => setRxOpen(true)}><span className="quick-icon mint"><ScanLine/></span><p><strong>ارسال نسخه</strong><small>بررسی توسط داروساز</small></p><ChevronLeft/></button>
          <button onClick={() => setConsultOpen(true)}><span className="quick-icon blue"><Video/></span><p><strong>مشاوره پزشکی</strong><small>تماس متنی و تصویری</small></p><ChevronLeft/></button>
          <button onClick={() => setToast('یادآور دارویی برای شما فعال شد')}><span className="quick-icon orange"><TimerReset/></span><p><strong>یادآور مصرف دارو</strong><small>هرگز فراموش نکنید</small></p><ChevronLeft/></button>
          <button onClick={() => setLocationOpen(true)}><span className="quick-icon purple"><Navigation/></span><p><strong>داروخانه نزدیک من</strong><small>ارسال از نزدیک‌ترین شعبه</small></p><ChevronLeft/></button>
        </div></section>

        <section className="section categories-section" id="services"><div className="container">
          <div className="section-head"><div><span className="kicker">هر آنچه برای سلامتی می‌خواهید</span><h2>خرید بر اساس دسته‌بندی</h2></div><button className="text-link" onClick={() => {setActiveCategory('all'); scrollTo('products')}}>مشاهده همه <ArrowLeft/></button></div>
          <div className="category-grid">{categories.map(cat => { const Icon = cat.icon; return <button key={cat.id} className={`category-card ${cat.tone}`} onClick={() => {setActiveCategory(cat.id === 'rx' ? 'all' : cat.id); cat.id === 'rx' ? setRxOpen(true) : scrollTo('products')}}><span className="cat-icon"><Icon/></span><strong>{cat.title}</strong><small>{cat.subtitle}</small><span className="cat-arrow"><ChevronLeft/></span></button> })}</div>
        </div></section>

        <section className="section products-section" id="products"><div className="container">
          <div className="section-head product-heading"><div><span className="kicker">پیشنهادهای منتخب برای شما</span><h2>محبوب‌ترین‌های این هفته</h2></div>
            <div className="filter-tabs">{[['all','همه'],['vitamin','مکمل‌ها'],['skin','پوست و مو'],['mom','مادر و کودک'],['medical','تجهیزات']].map(([id,label]) => <button key={id} className={activeCategory === id ? 'active' : ''} onClick={() => setActiveCategory(id)}>{label}</button>)}</div>
          </div>
          {search && <div className="search-result-label"><Search size={17}/><span>نتایج جستجو برای «{search}»</span><button onClick={()=>setSearch('')}><X size={16}/> پاک کردن</button></div>}
          <div className="product-grid">
            {(showAll ? filtered : filtered.slice(0,4)).map(product => <article className="product-card" key={product.id}>
              <div className="product-media" onClick={() => setQuickView(product)}>{product.badge && <span className="product-badge">{product.badge}</span>}{product.discount > 0 && <span className="discount">٪{toFa(product.discount)}</span>}<button className={`fav ${favorites.includes(product.id) ? 'active' : ''}`} onClick={(e)=>{e.stopPropagation();toggleFav(product.id)}} aria-label="افزودن به علاقه‌مندی"><Heart fill={favorites.includes(product.id) ? 'currentColor' : 'none'}/></button><ProductVisual product={product}/><span className="quick-view">مشاهده سریع</span></div>
              <div className="product-info"><span className="brand">{product.brand}</span><h3>{product.name}</h3><div className="product-rating"><Star fill="currentColor"/><b>{toFa(product.rating)}</b><span>({toFa(product.reviews)} نظر)</span></div><div className="product-bottom"><div className="price">{product.oldPrice && <del>{toFa(product.oldPrice)}</del>}<strong>{toFa(product.price)} <small>تومان</small></strong></div><button className="add-btn" onClick={() => addToCart(product)} aria-label="افزودن به سبد"><Plus/></button></div></div>
            </article>)}
            {filtered.length === 0 && <div className="empty-products"><Search/><h3>محصولی پیدا نشد</h3><p>عبارت دیگری را جستجو کنید یا فیلترها را پاک کنید.</p><button onClick={()=>{setSearch('');setActiveCategory('all')}}>نمایش همه محصولات</button></div>}
          </div>
          {filtered.length > 4 && <button className="show-more" onClick={() => setShowAll(!showAll)}>{showAll ? 'نمایش کمتر' : 'مشاهده همه محصولات'} <ArrowLeft/></button>}
        </div></section>

        <section className="consult-section" id="consult"><div className="container consult-wrap">
          <div className="consult-photo"><div className="photo-backdrop"/><img src="/doctor-hero.png" alt="پزشک آنلاین نبض سبز"/><div className="online-pill"><i/> آنلاین و آماده پاسخگویی</div><div className="doctor-info"><span><BadgeCheck fill="currentColor"/></span><p><strong>تیم پزشکی تأییدشده</strong><small>+۱۲۰ پزشک و داروساز</small></p></div></div>
          <div className="consult-copy"><span className="kicker light"><Stethoscope/> مشاوره‌ای امن و محرمانه</span><h2>سؤالت را از پزشک بپرس؛<br/>هر ساعت از شبانه‌روز.</h2><p>با پزشکان متخصص، روان‌شناسان و داروسازان باتجربه به‌صورت متنی، صوتی یا تصویری گفت‌وگو کنید.</p>
            <div className="consult-features"><span><Check/> پاسخ در کمتر از ۳ دقیقه</span><span><Check/> انتخاب پزشک بر اساس تخصص</span><span><Check/> پرونده سلامت یکپارچه</span><span><Check/> حفظ کامل حریم خصوصی</span></div>
            <div className="consult-buttons"><button className="white-btn" onClick={() => setConsultOpen(true)}><MessageCircle/> شروع مشاوره فوری <ArrowLeft/></button><button className="video-btn" onClick={() => setConsultOpen(true)}><Video/> رزرو تماس تصویری</button></div>
            <div className="consult-stats"><div><strong>+۵۰ هزار</strong><small>مشاوره موفق</small></div><i/><div><strong>۴.۹ از ۵</strong><small>رضایت کاربران</small></div><i/><div><strong>۲۴/۷</strong><small>همیشه در دسترس</small></div></div>
          </div>
        </div></section>

        <section className="section promo-section"><div className="container promo-grid">
          <div className="promo-card skin-promo"><img src="/skincare.jpg" alt="محصولات مراقبت پوست"/><div className="promo-content"><span>روتین پوست سالم</span><h3>درخشش طبیعی،<br/>با انتخاب درست.</h3><p>تا ۳۰٪ تخفیف محصولات منتخب مراقبت پوست</p><button onClick={()=>{setActiveCategory('skin');scrollTo('products')}}>خرید محصولات <ArrowLeft/></button></div><div className="promo-bubble"><b>۳۰٪</b><small>تخفیف</small></div></div>
          <div className="rx-promo"><div className="rx-icon"><ClipboardCheck/></div><div><span>نسخه‌ات را به ما بسپار</span><h3>پیچیدن نسخه، بدون معطلی</h3><p>تصویر نسخه را ارسال کنید؛ داروساز بررسی می‌کند و در سریع‌ترین زمان به دستتان می‌رسانیم.</p><button onClick={() => setRxOpen(true)}>آپلود تصویر نسخه <Upload/></button></div><span className="deco-pill one"/><span className="deco-pill two"/></div>
        </div></section>

        <section className="section magazine" id="magazine"><div className="container">
          <div className="section-head"><div><span className="kicker">دانستنی‌های معتبر برای زندگی بهتر</span><h2>مجله سلامت نبض‌سبز</h2></div><button className="text-link" onClick={()=>setToast('مجله سلامت در نسخه کامل در دسترس است')}>همه مقاله‌ها <ArrowLeft/></button></div>
          <div className="articles-grid"><article className="article-card featured"><div className="article-art sleep"><span className="moon">☾</span><div className="bed"><i/><i/></div></div><div><span className="article-tag">خواب و آرامش</span><h3>۷ راهکار علمی برای خوابی عمیق‌تر و روزی پرانرژی‌تر</h3><p>چطور با چند تغییر کوچک در سبک زندگی، کیفیت خوابمان را متحول کنیم؟</p><small><Clock3/> ۶ دقیقه مطالعه</small></div></article><article className="article-card"><div className="article-art vitamin"><span>C</span><i/><b>+</b></div><div><span className="article-tag">تغذیه و مکمل</span><h3>ویتامین C را چه زمانی مصرف کنیم؟</h3><small><Clock3/> ۴ دقیقه مطالعه</small></div></article><article className="article-card"><div className="article-art skincare"><span>SPF</span><i/><i/></div><div><span className="article-tag">پوست و زیبایی</span><h3>راهنمای انتخاب ضدآفتاب برای انواع پوست</h3><small><Clock3/> ۸ دقیقه مطالعه</small></div></article></div>
        </div></section>

        <section className="app-banner"><div className="container app-banner-inner"><div className="app-copy"><span className="kicker">نبض‌سبز همیشه همراه شما</span><h2>سلامتی در جیب شماست!</h2><p>با نصب اپلیکیشن، اولین سفارش خود را با <strong>۵۰ هزار تومان تخفیف</strong> ثبت کنید.</p><div className="download-buttons"><button><span>A</span><small>دریافت از</small><b>بازار</b></button><button><span>◉</span><small>دریافت از</small><b>مایکت</b></button><button className="qr">▦</button></div></div><div className="app-phones"><div className="app-phone back"><div><HeartPulse/><strong>نبض‌سبز</strong><span/></div></div><div className="app-phone front"><div className="app-screen-logo"><HeartPulse/><b>نبض‌سبز</b></div><span className="app-welcome">حالِ خوبت از اینجا شروع می‌شه</span><button>ورود به فروشگاه</button></div></div></div></section>
      </main>

      <footer><div className="container footer-grid">
        <div className="footer-brand"><div className="logo inverse"><span className="logo-mark"><HeartPulse/><i/></span><span><strong>نبض‌سبز</strong><small>داروخانه شبانه‌روزی</small></span></div><p>تجربه‌ای تازه از مراقبت سلامت؛ خرید مطمئن، مشاوره تخصصی و ارسال سریع، هر جا که باشید.</p><div className="footer-contact"><span><PhoneCall/> ۰۲۱-۹۱۰۰ ۲۴۰۰</span><span><MessageCircle/> پشتیبانی آنلاین ۲۴ ساعته</span></div></div>
        <div><h4>نبض‌سبز</h4><a>درباره ما</a><a>تماس با ما</a><a>فرصت‌های شغلی</a><a>شعب داروخانه</a></div><div><h4>خدمات مشتریان</h4><a>راهنمای خرید</a><a>پیگیری سفارش</a><a>شرایط بازگشت</a><a>پرسش‌های متداول</a></div><div><h4>خدمات سلامت</h4><a>مشاوره آنلاین</a><a>ارسال نسخه</a><a>یادآور دارویی</a><a>مجله سلامت</a></div>
        <div className="newsletter"><h4>خبرنامه نبض‌سبز</h4><p>تازه‌ترین پیشنهادها و مطالب سلامت را دریافت کنید.</p><div><input placeholder="شماره موبایل"/><button onClick={()=>setToast('عضویت شما در خبرنامه ثبت شد')}><ArrowLeft/></button></div><small><ShieldCheck/> اطلاعات شما نزد ما محفوظ است.</small></div>
      </div><div className="container footer-bottom"><p>© ۱۴۰۵ نبض‌سبز؛ همه حقوق محفوظ است.</p><div><span>مجوز رسمی وزارت بهداشت</span><span>دارای نماد اعتماد الکترونیکی</span></div></div></footer>

      <button className="floating-help" onClick={() => setConsultOpen(true)} aria-label="گفتگو با پشتیبانی"><span><MessageCircle/></span><b>یک سؤال داری؟</b><i/></button>
      {toast && <div className="toast"><span><Check/></span>{toast}</div>}

      {cartOpen && <div className="overlay" onMouseDown={(e)=>e.target===e.currentTarget&&setCartOpen(false)}><aside className="drawer"><div className="drawer-head"><div><ShoppingBag/><h3>سبد خرید</h3><span>{toFa(cartCount)} کالا</span></div><button onClick={()=>setCartOpen(false)}><X/></button></div><div className="drawer-body">{cart.length === 0 ? <div className="empty-cart"><span><ShoppingBag/></span><h3>سبد خریدتان خالی است</h3><p>می‌توانید از بین محصولات محبوب نبض‌سبز انتخاب کنید.</p><button onClick={()=>{setCartOpen(false);scrollTo('products')}}>مشاهده محصولات</button></div> : cart.map(item=><div className="cart-item" key={item.id}><ProductVisual product={item} small/><div><small>{item.brand}</small><strong>{item.name}</strong><b>{toFa(item.price)} تومان</b><div className="qty"><button onClick={()=>changeQty(item.id,-1)}>{item.qty===1?<X/>:<Minus/>}</button><span>{toFa(item.qty)}</span><button onClick={()=>changeQty(item.id,1)}><Plus/></button></div></div></div>)}</div>{cart.length>0&&<div className="drawer-footer"><div><span>جمع سبد خرید</span><strong>{toFa(cartTotal)} تومان</strong></div><p><Truck/> ارسال اکسپرس {cartTotal>=500000?'برای شما رایگان است':'با خرید بالای ۵۰۰ هزار تومان رایگان است'}</p><button onClick={()=>setToast('به مرحله ثبت آدرس منتقل شدید')}>ادامه فرایند خرید <ArrowLeft/></button></div>}</aside></div>}

      {consultOpen && <div className="overlay center" onMouseDown={(e)=>e.target===e.currentTarget&&setConsultOpen(false)}><div className="chat-modal"><div className="chat-head"><div><span className="bot-avatar"><Bot/></span><p><strong>دستیار سلامت نبض‌سبز</strong><small><i/> آنلاین؛ پاسخ‌گویی فوری</small></p></div><button onClick={()=>setConsultOpen(false)}><X/></button></div><div className="chat-security"><ShieldCheck/> گفت‌وگو کاملاً محرمانه و امن است</div><div className="chat-body">{messages.map((m,i)=><div className={`message ${m.from}`} key={i}>{m.text}</div>)}{messages.length===1&&<div className="chat-options"><button onClick={()=>sendMessage('مشاوره با پزشک عمومی')}><Stethoscope/> پزشک عمومی</button><button onClick={()=>sendMessage('مشاوره دارویی')}><Pill/> مشاوره دارویی</button><button onClick={()=>sendMessage('مشاوره پوست و مو')}><Sparkles/> پوست و مو</button></div>}</div><div className="chat-input"><input value={chatInput} onChange={e=>setChatInput(e.target.value)} onKeyDown={e=>e.key==='Enter'&&sendMessage()} placeholder="پیام خود را بنویسید..."/><button onClick={()=>sendMessage()}><Send/></button></div><small className="medical-note"><AlertCircle/> این سامانه جایگزین اورژانس پزشکی نیست.</small></div></div>}

      {rxOpen && <div className="overlay center" onMouseDown={(e)=>e.target===e.currentTarget&&setRxOpen(false)}><div className="rx-modal"><button className="modal-close" onClick={()=>setRxOpen(false)}><X/></button><div className="rx-modal-icon"><FileText/></div><span className="kicker">سریع، امن و محرمانه</span><h2>ارسال نسخه پزشک</h2><p>تصویر خوانا از نسخه را بارگذاری کنید. داروساز ما در کمتر از ۱۰ دقیقه آن را بررسی و برای تأیید با شما تماس می‌گیرد.</p><label className="upload-zone"><input type="file" accept="image/*,.pdf" onChange={(e)=>{if(e.target.files[0])setToast(`فایل «${e.target.files[0].name}» آماده ارسال است`)}}/><span><Upload/></span><strong>برای بارگذاری کلیک کنید</strong><small>یا تصویر نسخه را اینجا رها کنید</small><em>JPG, PNG یا PDF — حداکثر ۱۰ مگابایت</em></label><div className="rx-tips"><span><Check/> نسخه باید کامل و خوانا باشد</span><span><Check/> اطلاعات شما رمزگذاری می‌شود</span></div><button className="full-primary" onClick={()=>{setRxOpen(false);setToast('نسخه شما با موفقیت ثبت شد')}}>ثبت و ارسال برای داروساز <ArrowLeft/></button></div></div>}

      {quickView && <div className="overlay center" onMouseDown={(e)=>e.target===e.currentTarget&&setQuickView(null)}><div className="quick-modal"><button className="modal-close" onClick={()=>setQuickView(null)}><X/></button><div className="quick-modal-media"><ProductVisual product={quickView}/></div><div className="quick-modal-info"><span className="brand">{quickView.brand}</span><h2>{quickView.name}</h2><div className="product-rating"><Star fill="currentColor"/><b>{toFa(quickView.rating)}</b><span>از {toFa(quickView.reviews)} نظر خریداران</span></div><p>محصول اصل با تضمین اصالت و تاریخ مصرف معتبر، نگهداری‌شده در شرایط استاندارد داروخانه.</p><div className="stock"><Check/> موجود در انبار — ارسال امروز</div><div className="modal-price">{quickView.oldPrice&&<del>{toFa(quickView.oldPrice)}</del>}<strong>{toFa(quickView.price)} <small>تومان</small></strong></div><button className="full-primary" onClick={()=>{addToCart(quickView);setQuickView(null)}}><ShoppingBag/> افزودن به سبد خرید</button></div></div></div>}

      {locationOpen && <div className="overlay center" onMouseDown={(e)=>e.target===e.currentTarget&&setLocationOpen(false)}><div className="location-modal"><button className="modal-close" onClick={()=>setLocationOpen(false)}><X/></button><span className="location-icon"><MapPin/></span><h2>سفارش را کجا بفرستیم؟</h2><p>با انتخاب موقعیت، زمان دقیق تحویل و موجودی نزدیک‌ترین شعبه را می‌بینید.</p><div className="address-input"><Search/><input placeholder="جستجوی محله یا آدرس..."/></div><button className="locate-btn" onClick={()=>setToast('موقعیت فعلی شما شناسایی شد')}><Navigation/> استفاده از موقعیت فعلی من</button><div className="map-placeholder"><MapPin/></div><button className="full-primary" onClick={()=>{setLocationOpen(false);setToast('آدرس انتخاب شد؛ ارسال حدود ۴۵ دقیقه')}}>تأیید این محدوده <ArrowLeft/></button></div></div>}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App/>);
