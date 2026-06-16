interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export default function Input({ label, error, className = "", ...props }: InputProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-xs font-medium text-slate-400">{label}</label>
      )}
      <input
        className={`bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-600 text-sm focus:outline-none focus:border-amber-400 transition-colors ${className}`}
        {...props}
      />
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}
