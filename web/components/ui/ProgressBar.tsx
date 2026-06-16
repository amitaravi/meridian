interface ProgressBarProps {
  current: number;
  total: number;
}

export default function ProgressBar({ current, total }: ProgressBarProps) {
  return (
    <div className="flex gap-1.5">
      {Array.from({ length: total }).map((_, i) => (
        <div
          key={i}
          className={`h-0.5 flex-1 rounded-full transition-colors duration-300 ${
            i < current ? "bg-amber-400" : "bg-slate-700"
          }`}
        />
      ))}
    </div>
  );
}
