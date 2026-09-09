import { createContext, useCallback, useContext, useState } from 'react';
import { X, CheckCircle2, AlertTriangle, Info } from 'lucide-react';

/* ---------------- Toast ---------------- */
const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const push = useCallback((message, tone = 'good') => {
    const id = Date.now() + Math.random();
    setToasts((t) => [...t, { id, message, tone }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3500);
  }, []);

  return (
    <ToastContext.Provider value={push}>
      {children}
      <div className="toast-stack">
        {toasts.map((t) => (
          <div key={t.id} className={`toast toast-${t.tone}`}>
            {t.tone === 'good' && <CheckCircle2 size={18} />}
            {t.tone === 'warn' && <AlertTriangle size={18} />}
            {t.tone === 'info' && <Info size={18} />}
            <span>{t.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  return useContext(ToastContext);
}

/* ---------------- Button ---------------- */
export function Button({ variant = 'primary', size, className = '', children, ...props }) {
  return (
    <button className={`btn btn-${variant} ${size ? 'btn-' + size : ''} ${className}`} {...props}>
      {children}
    </button>
  );
}

/* ---------------- Card ---------------- */
export function Card({ className = '', children, title, icon, actions }) {
  return (
    <div className={`card ${className}`}>
      {(title || actions) && (
        <div className="card-head">
          <div className="card-title">
            {icon}
            <h3>{title}</h3>
          </div>
          {actions && <div className="card-actions">{actions}</div>}
        </div>
      )}
      {children}
    </div>
  );
}

/* ---------------- Badge ---------------- */
const TONES = {
  gold: 'gold',
  green: 'green',
  red: 'red',
  amber: 'amber',
  blue: 'blue',
  purple: 'purple',
  gray: 'gray'
};

export function Badge({ tone = 'gray', children }) {
  return <span className={`badge badge-${TONES[tone] || tone}`}>{children}</span>;
}

/* ---------------- Modal ---------------- */
export function Modal({ open, onClose, title, children, width }) {
  if (!open) return null;
  return (
    <div className="overlay" onClick={onClose}>
      <div className="modal" style={width ? { maxWidth: width } : undefined} onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h3>{title}</h3>
          <button className="icon-btn" onClick={onClose} aria-label="بستن">
            <X size={18} />
          </button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
}

/* ---------------- Form ---------------- */
export function Field({ label, hint, children }) {
  return (
    <label className="field">
      <span className="label">{label}</span>
      {children}
      {hint && <span className="hint">{hint}</span>}
    </label>
  );
}

export function Input(props) {
  return <input className="input" {...props} />;
}

export function Select({ children, ...props }) {
  return (
    <select className="select" {...props}>
      {children}
    </select>
  );
}

export function Textarea(props) {
  return <textarea className="textarea" {...props} />;
}

/* ---------------- Empty state ---------------- */
export function Empty({ icon, title, hint }) {
  return (
    <div className="empty">
      {icon}
      <p className="empty-title">{title}</p>
      {hint && <p className="empty-hint">{hint}</p>}
    </div>
  );
}
