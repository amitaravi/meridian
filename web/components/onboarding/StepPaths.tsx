"use client";

interface Props {
  pathA: string;
  pathB: string;
  onChange: (pathA: string, pathB: string) => void;
  error?: string;
}

const textareaClass =
  "w-full bg-slate-800 border rounded-xl px-4 py-3 text-white placeholder-slate-600 text-sm focus:outline-none transition-colors resize-none min-h-[120px]";

export default function StepPaths({ pathA, pathB, onChange, error }: Props) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Your two futures.</h2>
        <p className="text-slate-400 text-sm">
          The more vivid and specific these are, the harder it is to ignore them. Write the version of each future that you believe is real.
        </p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold tracking-widest text-slate-500 uppercase">
              Path A — The comfortable future
            </span>
          </div>
          <p className="text-xs text-slate-600">
            What does your life look like at 35 if you keep doing what you're doing? Be specific and honest.
          </p>
          <textarea
            value={pathA}
            onChange={(e) => onChange(e.target.value, pathB)}
            placeholder="e.g. Still in the same role, watching others build what I imagined. The side project never left Notion..."
            className={`${textareaClass} border-slate-700 focus:border-slate-500`}
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold tracking-widest text-amber-400 uppercase">
              Path B — The ambitious future
            </span>
          </div>
          <p className="text-xs text-slate-600">
            What does your life look like if you execute consistently for the next 3 years? Make it specific enough that it feels real.
          </p>
          <textarea
            value={pathB}
            onChange={(e) => onChange(pathA, e.target.value)}
            placeholder="e.g. I shipped the product. Left the job. The side project became the main thing..."
            className={`${textareaClass} border-amber-400/20 focus:border-amber-400/50`}
          />
        </div>
      </div>

      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}
