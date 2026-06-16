"use client";

interface Props {
  value: string[];
  onChange: (v: string[]) => void;
  error?: string;
}

export default function StepAccomplishments({ value, onChange, error }: Props) {
  const update = (i: number, val: string) => {
    const next = [...value];
    next[i] = val;
    onChange(next);
  };

  const addEntry = () => {
    if (value.length >= 3) return;
    onChange([...value, ""]);
  };

  const remove = (i: number) => onChange(value.filter((_, idx) => idx !== i));

  const inputClass =
    "w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-600 text-sm focus:outline-none focus:border-amber-400 transition-colors";

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">You&apos;ve already proven it.</h2>
        <p className="text-slate-400 text-sm">
          What have you already done that proves you can do hard things when the stakes are real? These become your daily reminder that capability is not the issue.
        </p>
      </div>

      <div className="space-y-3">
        {value.map((entry, i) => (
          <div key={i} className="flex gap-2">
            <input
              value={entry}
              onChange={(e) => update(i, e.target.value)}
              placeholder="e.g. Studied 10 hours daily for board exams and topped the school"
              className={`${inputClass} flex-1`}
            />
            <button
              onClick={() => remove(i)}
              className="text-slate-600 hover:text-red-400 transition-colors px-2 text-sm"
            >
              ×
            </button>
          </div>
        ))}
      </div>

      {value.length < 3 && (
        <button
          onClick={addEntry}
          className="w-full py-3 rounded-xl border border-dashed border-slate-700 text-slate-500 text-sm hover:border-slate-500 hover:text-slate-400 transition-colors"
        >
          + Add accomplishment {value.length > 0 ? `(${3 - value.length} more)` : ""}
        </button>
      )}

      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}
