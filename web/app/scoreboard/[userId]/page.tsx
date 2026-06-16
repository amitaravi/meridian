import { notFound } from "next/navigation";
import WeekGrid, { type AreaGridData } from "@/components/scoreboard/WeekGrid";
import { type CellState } from "@/components/scoreboard/GoalAreaRow";
import { createServerClient } from "@/lib/supabase/server";
import type { Block, DailyLog, GoalArea, Profile, Streak } from "@/types";

interface Props {
  params: { userId: string };
}

// ── Date helpers ──────────────────────────────────────────────────────────────

function getWeekDates(): Date[] {
  const today = new Date();
  const dayOfWeek = today.getDay(); // 0=Sun
  const monday = new Date(today);
  monday.setDate(today.getDate() - ((dayOfWeek + 6) % 7));
  monday.setHours(0, 0, 0, 0);
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday);
    d.setDate(monday.getDate() + i);
    return d;
  });
}

function toIso(d: Date): string {
  return d.toISOString().slice(0, 10);
}

// ── Computation helpers ───────────────────────────────────────────────────────

function cellState(log: DailyLog | null, areaName: string, isFuture: boolean): CellState {
  if (isFuture) return "future";
  if (!log) return "empty";
  const areaBlocks = (log.blocks as Block[]).filter((b) => b.goal_area === areaName);
  if (areaBlocks.length === 0) return "empty";
  const done = areaBlocks.filter((b) =>
    (log.completed_block_indices ?? []).includes(b.index)
  ).length;
  if (done === 0) return "empty";
  return done === areaBlocks.length ? "full" : "partial";
}

function hoursForArea(logs: (DailyLog | null)[], areaName: string): number {
  let mins = 0;
  for (const log of logs) {
    if (!log) continue;
    for (const block of log.blocks as Block[]) {
      if (
        block.goal_area === areaName &&
        (log.completed_block_indices ?? []).includes(block.index)
      ) {
        mins += block.duration_mins;
      }
    }
  }
  return Math.round((mins / 60) * 10) / 10;
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default async function ScoreboardPage({ params }: Props) {
  const supabase = createServerClient();
  const today = new Date();
  const weekDates = getWeekDates();
  const weekStart = toIso(weekDates[0]);
  const weekEnd = toIso(weekDates[6]);

  const [{ data: profile }, { data: logsRaw }, { data: streak }] = await Promise.all([
    supabase.from("profiles").select("*").eq("user_id", params.userId).single(),
    supabase
      .from("daily_logs")
      .select("*")
      .eq("user_id", params.userId)
      .gte("date", weekStart)
      .lte("date", weekEnd),
    supabase.from("streaks").select("*").eq("user_id", params.userId).single(),
  ]);

  if (!profile) notFound();

  const logsByDate = new Map<string, DailyLog>(
    (logsRaw ?? []).map((l) => [l.date as string, l as DailyLog])
  );

  const goalAreas: GoalArea[] = (profile as Profile).goal_areas ?? [];

  const dayLabels = weekDates.map((d) =>
    d.toLocaleDateString("en-US", { weekday: "short" })
  );

  const areas: AreaGridData[] = goalAreas.map((area) => {
    const cells: CellState[] = weekDates.map((d) => {
      const isFuture = d > today;
      const log = logsByDate.get(toIso(d)) ?? null;
      return cellState(log, area.name, isFuture);
    });
    const orderedLogs = weekDates.map((d) => logsByDate.get(toIso(d)) ?? null);
    return {
      name: area.name,
      colorEmoji: area.color_emoji,
      hoursWorked: hoursForArea(orderedLogs, area.name),
      weeklyTarget: area.weekly_hours,
      cells,
    };
  });

  const currentStreak = (streak as Streak | null)?.current_streak ?? 0;
  const weekLabel = `${weekDates[0].toLocaleDateString("en-US", { month: "short", day: "numeric" })} – ${weekDates[6].toLocaleDateString("en-US", { month: "short", day: "numeric" })}`;

  return (
    <div className="min-h-screen bg-slate-950 text-white px-4 py-10">
      <div className="max-w-2xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <p className="text-xs font-semibold tracking-widest text-amber-400 uppercase mb-2">
            Meridian
          </p>
          <h1 className="text-2xl font-bold mb-1">Weekly scoreboard</h1>
          <p className="text-sm text-slate-500">{weekLabel}</p>
        </div>

        {/* Streak */}
        <div className="flex items-center gap-3 bg-slate-900 rounded-2xl px-5 py-4">
          <span className="text-3xl">🔥</span>
          <div>
            <p className="text-2xl font-bold">{currentStreak}</p>
            <p className="text-xs text-slate-500">
              day streak{currentStreak !== 1 ? "s" : ""}
            </p>
          </div>
        </div>

        {/* Grid */}
        {areas.length > 0 ? (
          <div className="bg-slate-900 rounded-2xl px-4 py-5">
            <WeekGrid areas={areas} dayLabels={dayLabels} />
          </div>
        ) : (
          <div className="bg-slate-900 rounded-2xl px-5 py-8 text-center">
            <p className="text-slate-500 text-sm">No goal areas set up yet.</p>
          </div>
        )}

        {/* Legend */}
        <div className="flex gap-4 text-xs text-slate-600">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-blue-500 inline-block" />
            Complete
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-blue-500 opacity-40 inline-block" />
            Partial
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-slate-800 inline-block" />
            None
          </span>
        </div>

        <p className="text-xs text-slate-700 text-center pb-4">
          Built with Meridian
        </p>
      </div>
    </div>
  );
}
