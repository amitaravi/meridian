import GoalAreaRow, { type CellState } from "./GoalAreaRow";

export interface AreaGridData {
  name: string;
  colorEmoji: string;
  hoursWorked: number;
  weeklyTarget: number;
  cells: CellState[];
}

interface Props {
  areas: AreaGridData[];
  dayLabels: string[];
}

const DAY_ABBR = ["M", "T", "W", "T", "F", "S", "S"];

export default function WeekGrid({ areas, dayLabels }: Props) {
  return (
    <div className="space-y-2">
      {/* Day header */}
      <div className="flex items-center gap-3">
        <div className="w-36 sm:w-44 flex-shrink-0" />
        <div className="grid grid-cols-7 gap-1 flex-1">
          {dayLabels.map((label, i) => (
            <div key={i} className="text-center">
              <span className="hidden sm:inline text-xs text-slate-600">{label}</span>
              <span className="sm:hidden text-xs text-slate-600">{DAY_ABBR[i]}</span>
            </div>
          ))}
        </div>
        <div className="w-20 flex-shrink-0 text-right">
          <span className="text-xs text-slate-600">week</span>
        </div>
      </div>

      {/* One row per goal area */}
      {areas.map((area) => (
        <GoalAreaRow
          key={area.name}
          name={area.name}
          colorEmoji={area.colorEmoji}
          hoursWorked={area.hoursWorked}
          weeklyTarget={area.weeklyTarget}
          cells={area.cells}
        />
      ))}
    </div>
  );
}
