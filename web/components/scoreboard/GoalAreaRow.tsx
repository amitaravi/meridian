const EMOJI_COLORS: Record<string, string> = {
  "🟦": "bg-blue-500",
  "🟩": "bg-emerald-500",
  "🟥": "bg-red-500",
  "🟨": "bg-yellow-400",
  "🟧": "bg-orange-500",
  "🟪": "bg-purple-500",
};

export type CellState = "empty" | "partial" | "full" | "future";

interface Props {
  name: string;
  colorEmoji: string;
  hoursWorked: number;
  weeklyTarget: number;
  cells: CellState[];
}

function Cell({ state, colorEmoji }: { state: CellState; colorEmoji: string }) {
  const base = EMOJI_COLORS[colorEmoji] ?? "bg-amber-400";
  const classes: Record<CellState, string> = {
    full: `${base} rounded`,
    partial: `${base} opacity-40 rounded`,
    empty: "bg-slate-800 rounded",
    future: "bg-slate-900 rounded border border-slate-800",
  };
  return <div className={`w-full aspect-square ${classes[state]}`} />;
}

export default function GoalAreaRow({ name, colorEmoji, hoursWorked, weeklyTarget, cells }: Props) {
  const pct = weeklyTarget > 0 ? Math.min(hoursWorked / weeklyTarget, 1) : 0;
  const onTrack = hoursWorked >= weeklyTarget * 0.7;

  return (
    <div className="flex items-center gap-3">
      <div className="w-36 sm:w-44 flex-shrink-0 flex items-center gap-1.5 min-w-0">
        <span className="text-base leading-none">{colorEmoji}</span>
        <span className="text-xs text-slate-300 truncate">{name}</span>
      </div>
      <div className="grid grid-cols-7 gap-1 flex-1">
        {cells.map((state, i) => (
          <Cell key={i} state={state} colorEmoji={colorEmoji} />
        ))}
      </div>
      <div className="w-20 flex-shrink-0 text-right">
        <span className={`text-xs font-mono ${onTrack ? "text-emerald-400" : "text-amber-400"}`}>
          {hoursWorked}
          <span className="text-slate-600">/{weeklyTarget}h</span>
        </span>
      </div>
    </div>
  );
}
