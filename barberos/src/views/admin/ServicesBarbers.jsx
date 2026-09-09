import { useState } from 'react';
import { Plus, Pencil, Trash2, Scissors, Clock } from 'lucide-react';
import { useStore } from '../../lib/store';
import { useToast, Button, Badge, Modal, Field, Input } from '../../components/ui';
import { faNum, toToman } from '../../lib/format';

function ServiceForm({ initial, onSave, onClose }) {
  const [name, setName] = useState(initial?.name || '');
  const [duration, setDuration] = useState(initial?.durationMinutes || 45);
  const [buffer, setBuffer] = useState(initial?.bufferMinutes ?? 5);
  const [priceToman, setPriceToman] = useState(initial ? Math.round(initial.priceRial / 10) : 0);

  function save() {
    if (!name.trim()) return;
    onSave({
      name: name.trim(),
      durationMinutes: Number(duration) || 30,
      bufferMinutes: Number(buffer) || 0,
      priceRial: (Number(priceToman) || 0) * 10
    });
    onClose();
  }

  return (
    <div>
      <Field label="نام خدمت"><Input value={name} onChange={(e) => setName(e.target.value)} placeholder="مثلاً کوتاهی مو" /></Field>
      <div className="grid grid-2">
        <Field label="مدت (دقیقه)"><Input type="number" value={duration} onChange={(e) => setDuration(e.target.value)} /></Field>
        <Field label="بافر بین نوبت (دقیقه)"><Input type="number" value={buffer} onChange={(e) => setBuffer(e.target.value)} /></Field>
      </div>
      <Field label="قیمت (تومان)"><Input type="number" value={priceToman} onChange={(e) => setPriceToman(e.target.value)} /></Field>
      <Button className="btn-block" onClick={save}>ذخیره خدمت</Button>
    </div>
  );
}

function BarberForm({ services, initial, onSave, onClose }) {
  const [name, setName] = useState(initial?.name || '');
  const [skills, setSkills] = useState(initial?.skills || []);

  function toggle(id) {
    setSkills((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]));
  }

  function save() {
    if (!name.trim()) return;
    onSave({ name: name.trim(), skills });
    onClose();
  }

  return (
    <div>
      <Field label="نام آرایشگر"><Input value={name} onChange={(e) => setName(e.target.value)} placeholder="مثلاً آرمان راد" /></Field>
      <p className="label">خدمات قابل ارائه</p>
      <div className="grid grid-2" style={{ marginBottom: 14 }}>
        {services.map((s) => (
          <label key={s.id} className="pick-card" style={{ flexDirection: 'row', alignItems: 'center', gap: 8, padding: 10 }}>
            <input type="checkbox" checked={skills.includes(s.id)} onChange={() => toggle(s.id)} />
            <span>{s.name}</span>
          </label>
        ))}
      </div>
      <Button className="btn-block" onClick={save}>ذخیره آرایشگر</Button>
    </div>
  );
}

export default function ServicesBarbers() {
  const { services, barbers, addService, updateService, removeService, addBarber, updateBarber, removeBarber } = useStore();
  const toast = useToast();
  const [svcModal, setSvcModal] = useState(false);
  const [svcEdit, setSvcEdit] = useState(null);
  const [barberModal, setBarberModal] = useState(false);
  const [barberEdit, setBarberEdit] = useState(null);

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>خدمات و آرایشگران</h1>
          <p>مدت، بافر، قیمت و مهارت‌های هر آرایشگر</p>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-head">
            <div className="card-title"><Scissors size={17} /><h3>خدمات ({faNum(services.length)})</h3></div>
            <Button size="sm" onClick={() => { setSvcEdit(null); setSvcModal(true); }}><Plus size={14} /> افزودن</Button>
          </div>
          {services.map((s) => (
            <div className="list-row" key={s.id}>
              <div className="grow">
                <div className="main">{s.name}</div>
                <div className="sub"><Clock size={12} style={{ verticalAlign: -2 }} /> {faNum(s.durationMinutes)} دقیقه · بافر {faNum(s.bufferMinutes)} دقیقه</div>
              </div>
              <div className="trail">
                <span className="price" style={{ color: 'var(--gold-strong)', fontWeight: 800 }}>{toToman(s.priceRial)}</span>
                <button className="icon-btn" onClick={() => { setSvcEdit(s); setSvcModal(true); }}><Pencil size={15} /></button>
                <button className="icon-btn" onClick={() => { removeService(s.id); toast('خدمت حذف شد.', 'warn'); }}><Trash2 size={15} /></button>
              </div>
            </div>
          ))}
        </div>

        <div className="card">
          <div className="card-head">
            <div className="card-title"><Scissors size={17} /><h3>آرایشگران ({faNum(barbers.length)})</h3></div>
            <Button size="sm" onClick={() => { setBarberEdit(null); setBarberModal(true); }}><Plus size={14} /> افزودن</Button>
          </div>
          {barbers.map((b) => (
            <div className="list-row" key={b.id}>
              <div className="avatar">{b.name.slice(0, 1)}</div>
              <div className="grow">
                <div className="main">{b.name}</div>
                <div className="chip-row" style={{ marginTop: 4 }}>
                  {b.skills.map((sid) => (
                    <Badge key={sid} tone="gray">{services.find((s) => s.id === sid)?.name}</Badge>
                  ))}
                </div>
              </div>
              <div className="trail">
                <button className="icon-btn" onClick={() => { setBarberEdit(b); setBarberModal(true); }}><Pencil size={15} /></button>
                <button className="icon-btn" onClick={() => { removeBarber(b.id); toast('آرایشگر حذف شد.', 'warn'); }}><Trash2 size={15} /></button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <Modal open={svcModal} onClose={() => setSvcModal(false)} title={svcEdit ? 'ویرایش خدمت' : 'خدمت جدید'}>
        <ServiceForm
          initial={svcEdit}
          onSave={(data) => (svcEdit ? updateService(svcEdit.id, data) : addService(data))}
          onClose={() => setSvcModal(false)}
        />
      </Modal>

      <Modal open={barberModal} onClose={() => setBarberModal(false)} title={barberEdit ? 'ویرایش آرایشگر' : 'آرایشگر جدید'}>
        <BarberForm
          services={services}
          initial={barberEdit}
          onSave={(data) => (barberEdit ? updateBarber(barberEdit.id, data) : addBarber(data))}
          onClose={() => setBarberModal(false)}
        />
      </Modal>
    </div>
  );
}
