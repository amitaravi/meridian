"use client";

import { useState } from "react";
import StepAccomplishments from "@/components/onboarding/StepAccomplishments";
import StepAvailability from "@/components/onboarding/StepAvailability";
import StepGoalAreas from "@/components/onboarding/StepGoalAreas";
import StepPaths from "@/components/onboarding/StepPaths";
import StepWhy, { type WhyAnswers } from "@/components/onboarding/StepWhy";
import type { GoalArea, Profile } from "@/types";

interface FormData {
  goal_areas: GoalArea[];
  why: WhyAnswers;
  path_a: string;
  path_b: string;
  accomplishments: string[];
  brief_hour: number;
  brief_minute: number;
  timezone: string;
}

function parseWhyText(text: string): WhyAnswers {
  const parts = text.split("\n\n");
  const extract = (s: string | undefined, prefix: string) =>
    (s ?? "").replace(prefix, "").trim();
  return {
    q1: extract(parts[0], "What I'm building toward: "),
    q2: extract(parts[1], "My life on current path: "),
    q3: extract(parts[2], "What the hard path unlocks: "),
  };
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="py-8 border-t border-slate-800/60">
      <h2 className="text-xs font-semibold tracking-widest text-slate-500 uppercase mb-6">
        {title}
      </h2>
      {children}
    </section>
  );
}

interface Props {
  telegramId: string;
  userId: string;
  profile: Profile;
}

export default function SettingsForm({ telegramId, userId, profile }: Props) {
  const [data, setData] = useState<FormData>({
    goal_areas: profile.goal_areas,
    why: parseWhyText(profile.why_text),
    path_a: profile.path_a,
    path_b: profile.path_b,
    accomplishments: profile.accomplishments,
    brief_hour: profile.brief_hour,
    brief_minute: profile.brief_minute,
    timezone: profile.timezone,
  });

  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const update = <K extends keyof FormData>(key: K, value: FormData[K]) =>
    setData((d) => ({ ...d, [key]: value }));

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    setError(null);

    const why_text = [
      `What I'm building toward: ${data.why.q1}`,
      `My life on current path: ${data.why.q2}`,
      `What the hard path unlocks: ${data.why.q3}`,
    ].join("\n\n");

    try {
      const res = await fetch("/api/settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          telegram_id: parseInt(telegramId, 10),
          user_id: userId,
          goal_areas: data.goal_areas,
          why_text,
          path_a: data.path_a,
          path_b: data.path_b,
          accomplishments: data.accomplishments.filter(Boolean),
          brief_hour: data.brief_hour,
          brief_minute: data.brief_minute,
          timezone: data.timezone,
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error((body as { error?: string }).error ?? "Save failed");
      }
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setSaving(false);
    }
  };

  const botUrl = `https://t.me/${process.env.NEXT_PUBLIC_BOT_USERNAME ?? "MeridianBot"}`;

  return (
    <div className="max-w-lg mx-auto px-6 pb-32">
      <div className="flex items-center justify-between py-8">
        <h1 className="text-lg font-bold">Settings</h1>
        <a href={botUrl} className="text-xs text-slate-500 hover:text-slate-300 transition-colors">
          ← Back to Telegram
        </a>
      </div>

      <Section title="Goal areas">
        <StepGoalAreas value={data.goal_areas} onChange={(v) => update("goal_areas", v)} />
      </Section>

      <Section title="Your why">
        <StepWhy value={data.why} onChange={(v) => update("why", v)} />
      </Section>

      <Section title="Path A & Path B">
        <StepPaths
          pathA={data.path_a}
          pathB={data.path_b}
          onChange={(a, b) => setData((d) => ({ ...d, path_a: a, path_b: b }))}
        />
      </Section>

      <Section title="Past accomplishments">
        <StepAccomplishments
          value={data.accomplishments}
          onChange={(v) => update("accomplishments", v)}
        />
      </Section>

      <Section title="Delivery time">
        <StepAvailability
          briefHour={data.brief_hour}
          briefMinute={data.brief_minute}
          timezone={data.timezone}
          onChange={(h, m, tz) =>
            setData((d) => ({ ...d, brief_hour: h, brief_minute: m, timezone: tz }))
          }
        />
      </Section>

      <div className="fixed bottom-0 left-0 right-0 bg-slate-950/90 backdrop-blur-sm border-t border-slate-800/50 px-6 py-5">
        <div className="max-w-lg mx-auto flex items-center gap-4">
          {saved && (
            <span className="text-sm text-amber-400 flex-shrink-0">Saved ✓</span>
          )}
          {error && (
            <span className="text-sm text-red-400 flex-shrink-0 truncate">{error}</span>
          )}
          <button
            onClick={handleSave}
            disabled={saving}
            className="ml-auto px-8 py-3 rounded-full bg-amber-400 text-slate-950 text-sm font-semibold hover:bg-amber-300 transition-colors disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save changes"}
          </button>
        </div>
      </div>
    </div>
  );
}
