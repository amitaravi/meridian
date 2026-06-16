"use client";

import { useEffect } from "react";

interface Props {
  briefHour: number;
  briefMinute: number;
  timezone: string;
  onChange: (hour: number, minute: number, timezone: string) => void;
  error?: string;
}

const TIMEZONES = [
  "Asia/Kolkata",
  "Asia/Singapore",
  "Asia/Dubai",
  "Europe/London",
  "Europe/Berlin",
  "America/New_York",
  "America/Chicago",
  "America/Los_Angeles",
  "Australia/Sydney",
];

const HOURS = Array.from({ length: 24 }, (_, i) => i);

const MINUTES = [0, 15, 30, 45];

function pad(n: number) {
  return String(n).padStart(2, "0");
}

const selectClass =
  "bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-amber-400 transition-colors";

export default function StepAvailability({
  briefHour,
  briefMinute,
  timezone,
  onChange,
  error,
}: Props) {
  useEffect(() => {
    const detected = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (detected && TIMEZONES.includes(detected) && timezone !== detected) {
      onChange(briefHour, briefMinute, detected);
    }
    // Only run on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">When should your brief arrive?</h2>
        <p className="text-slate-400 text-sm">
          Set the time Meridian sends your daily brief. Most users choose between 6–8am — before the workday claims the morning.
        </p>
      </div>

      <div className="space-y-5">
        <div className="space-y-2">
          <label className="text-xs font-medium text-slate-400">Daily brief delivery time</label>
          <div className="flex items-center gap-3">
            <select
              value={briefHour}
              onChange={(e) => onChange(parseInt(e.target.value), briefMinute, timezone)}
              className={`${selectClass} flex-1`}
            >
              {HOURS.map((h) => (
                <option key={h} value={h}>
                  {pad(h)}
                </option>
              ))}
            </select>
            <span className="text-slate-500 font-bold">:</span>
            <select
              value={briefMinute}
              onChange={(e) => onChange(briefHour, parseInt(e.target.value), timezone)}
              className={`${selectClass} flex-1`}
            >
              {MINUTES.map((m) => (
                <option key={m} value={m}>
                  {pad(m)}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-xs font-medium text-slate-400">Timezone</label>
          <select
            value={timezone}
            onChange={(e) => onChange(briefHour, briefMinute, e.target.value)}
            className={`${selectClass} w-full`}
          >
            {TIMEZONES.map((tz) => (
              <option key={tz} value={tz}>
                {tz}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="bg-amber-950/30 border border-amber-400/20 rounded-xl p-4">
        <p className="text-xs text-amber-200/70">
          Your brief will arrive at{" "}
          <strong>
            {pad(briefHour)}:{pad(briefMinute)}
          </strong>{" "}
          {timezone} every morning. You can change this anytime via /settings.
        </p>
      </div>

      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}
