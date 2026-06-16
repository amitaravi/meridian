"use client";

import type { GoalArea } from "@/types";

const COLOR_OPTIONS = ["🟦", "🟩", "🟥", "🟨", "🟧", "🟪"];

interface Props {
  value: GoalArea[];
  onChange: (areas: GoalArea[]) => void;
  error?: string;
}

export default function StepGoalAreas({ value, onChange, error }: Props) {
  const addArea = () => {
    if (value.length >= 3) return;
    onChange([
      ...value,
      {
        name: "",
        description: "",
        weekly_hours: 5,
        color_emoji: COLOR_OPTIONS[value.length] ?? "🟦",
      },
    ]);
  };

  const removeArea = (i: number) => onChange(value.filter((_, idx) => idx !== i));

  const update = (i: number, field: keyof GoalArea, val: string | number) => {
    const next = [...value];
    next[i] = { ...next[i], [field]: val };
    onChange(next);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">What are you building toward?</h2>
        <p className="text-slate-400 text-sm">
          Define up to 3 life areas. Be specific — these become the source material for every daily brief and time block.
        </p>
      </div>

      <div className="space-y-4">
        {value.map((area, i) => (
          <div key={i} className="bg-slate-800/50 rounded-2xl p-5 border border-slate-700 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-slate-500">Area {i + 1}</span>
              <button
                onClick={() => removeArea(i)}
                className="text-xs text-slate-600 hover:text-red-400 transition-colors"
              >
                Remove
              </button>
            </div>

            <input
              value={area.name}
              onChange={(e) => update(i, "name", e.target.value)}
              placeholder="e.g. Career Transition"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-600 text-sm focus:outline-none focus:border-amber-400 transition-colors"
            />

            <input
              value={area.description}
              onChange={(e) => update(i, "description", e.target.value)}
              placeholder="Describe this goal area in one sentence"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-600 text-sm focus:outline-none focus:border-amber-400 transition-colors"
            />

            <div className="flex items-center gap-4">
              <div className="flex-1">
                <label className="text-xs text-slate-500 mb-1.5 block">Hours / week</label>
                <input
                  type="number"
                  min={1}
                  max={40}
                  value={area.weekly_hours}
                  onChange={(e) => update(i, "weekly_hours", parseInt(e.target.value) || 1)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-amber-400 transition-colors"
                />
              </div>
              <div>
                <label className="text-xs text-slate-500 mb-1.5 block">Colour</label>
                <div className="flex gap-2">
                  {COLOR_OPTIONS.map((emoji) => (
                    <button
                      key={emoji}
                      onClick={() => update(i, "color_emoji", emoji)}
                      className={`text-lg p-1 rounded transition-transform ${
                        area.color_emoji === emoji ? "scale-125" : "opacity-40 hover:opacity-70"
                      }`}
                    >
                      {emoji}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {value.length < 3 && (
        <button
          onClick={addArea}
          className="w-full py-3 rounded-xl border border-dashed border-slate-700 text-slate-500 text-sm hover:border-slate-500 hover:text-slate-400 transition-colors"
        >
          + Add goal area {value.length === 0 ? "" : `(${3 - value.length} remaining)`}
        </button>
      )}

      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}
