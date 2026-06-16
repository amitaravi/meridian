"use client";

export interface WhyAnswers {
  q1: string;
  q2: string;
  q3: string;
}

interface Props {
  value: WhyAnswers;
  onChange: (v: WhyAnswers) => void;
  error?: string;
}

const QUESTIONS = [
  {
    key: "q1" as const,
    prompt: "What are you ultimately trying to build or become?",
    hint: "Not your job title. The actual thing.",
  },
  {
    key: "q2" as const,
    prompt: "What does your life look like at 40 if you stay on your current path?",
    hint: "Be honest. Specific. This becomes your Path A.",
  },
  {
    key: "q3" as const,
    prompt: "What does taking the hard path unlock for your life?",
    hint: "Go beyond money. What changes about your days, your identity, your options?",
  },
];

const textareaClass =
  "w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-600 text-sm focus:outline-none focus:border-amber-400 transition-colors resize-none min-h-[100px]";

export default function StepWhy({ value, onChange, error }: Props) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Your why.</h2>
        <p className="text-slate-400 text-sm">
          These answers are the source of your daily brief. The more specific you are, the more the brief will feel written for you.
        </p>
      </div>

      <div className="space-y-6">
        {QUESTIONS.map(({ key, prompt, hint }) => (
          <div key={key} className="space-y-2">
            <p className="text-sm font-medium text-white">{prompt}</p>
            <p className="text-xs text-slate-500">{hint}</p>
            <textarea
              value={value[key]}
              onChange={(e) => onChange({ ...value, [key]: e.target.value })}
              placeholder="Write freely..."
              className={textareaClass}
            />
          </div>
        ))}
      </div>

      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}
