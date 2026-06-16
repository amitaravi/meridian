"use client";

import { useState } from "react";
import type { GoalArea } from "@/types";
import ProgressBar from "@/components/ui/ProgressBar";
import StepAccomplishments from "./StepAccomplishments";
import StepAvailability from "./StepAvailability";
import StepGoalAreas from "./StepGoalAreas";
import StepPaths from "./StepPaths";
import StepWhy, { type WhyAnswers } from "./StepWhy";

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

const INITIAL: FormData = {
  goal_areas: [],
  why: { q1: "", q2: "", q3: "" },
  path_a: "",
  path_b: "",
  accomplishments: [],
  brief_hour: 7,
  brief_minute: 0,
  timezone: "Asia/Kolkata",
};

const TOTAL = 5;

function validate(step: number, data: FormData): string | null {
  switch (step) {
    case 1:
      if (data.goal_areas.length === 0) return "Add at least one goal area.";
      if (data.goal_areas.some((a) => !a.name.trim() || !a.description.trim()))
        return "Each goal area needs a name and description.";
      return null;
    case 2:
      if (!data.why.q1.trim() || !data.why.q2.trim() || !data.why.q3.trim())
        return "Please answer all three questions.";
      return null;
    case 3:
      if (!data.path_a.trim()) return "Describe your Path A.";
      if (!data.path_b.trim()) return "Describe your Path B.";
      return null;
    case 4:
      if (data.accomplishments.length === 0 || !data.accomplishments[0].trim())
        return "Add at least one accomplishment.";
      if (data.accomplishments.some((a) => !a.trim()))
        return "Remove any empty accomplishment entries.";
      return null;
    default:
      return null;
  }
}

interface Props {
  telegramId: string;
}

export default function OnboardingForm({ telegramId }: Props) {
  const [step, setStep] = useState(1);
  const [data, setData] = useState<FormData>(INITIAL);
  const [stepError, setStepError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  const update = <K extends keyof FormData>(key: K, value: FormData[K]) =>
    setData((d) => ({ ...d, [key]: value }));

  const handleNext = () => {
    const err = validate(step, data);
    if (err) {
      setStepError(err);
      return;
    }
    setStepError(null);
    setStep((s) => s + 1);
  };

  const handleBack = () => {
    setStepError(null);
    setStep((s) => s - 1);
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setSubmitError(null);

    const why_text = [
      `What I'm building toward: ${data.why.q1}`,
      `My life on current path: ${data.why.q2}`,
      `What the hard path unlocks: ${data.why.q3}`,
    ].join("\n\n");

    try {
      const res = await fetch("/api/onboarding", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          telegram_id: parseInt(telegramId, 10),
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
      setDone(true);
    } catch (e) {
      setSubmitError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  };

  if (done) return <Confirmation />;

  const stepProps = { error: stepError ?? undefined };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col">
      <div className="max-w-lg w-full mx-auto px-6 pt-10 pb-32 flex-1">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-bold text-white">Meridian</span>
            <span className="text-xs text-slate-500">
              Step {step} of {TOTAL}
            </span>
          </div>
          <ProgressBar current={step} total={TOTAL} />
        </div>

        {step === 1 && (
          <StepGoalAreas
            value={data.goal_areas}
            onChange={(v) => update("goal_areas", v)}
            {...stepProps}
          />
        )}
        {step === 2 && (
          <StepWhy
            value={data.why}
            onChange={(v) => update("why", v)}
            {...stepProps}
          />
        )}
        {step === 3 && (
          <StepPaths
            pathA={data.path_a}
            pathB={data.path_b}
            onChange={(a, b) => setData((d) => ({ ...d, path_a: a, path_b: b }))}
            {...stepProps}
          />
        )}
        {step === 4 && (
          <StepAccomplishments
            value={data.accomplishments}
            onChange={(v) => update("accomplishments", v)}
            {...stepProps}
          />
        )}
        {step === 5 && (
          <StepAvailability
            briefHour={data.brief_hour}
            briefMinute={data.brief_minute}
            timezone={data.timezone}
            onChange={(h, m, tz) =>
              setData((d) => ({ ...d, brief_hour: h, brief_minute: m, timezone: tz }))
            }
            {...stepProps}
          />
        )}
      </div>

      <div className="fixed bottom-0 left-0 right-0 bg-slate-950/90 backdrop-blur-sm border-t border-slate-800/50 px-6 py-5">
        <div className="max-w-lg mx-auto flex gap-3">
          {step > 1 && (
            <button
              onClick={handleBack}
              className="px-6 py-3 rounded-full border border-slate-700 text-slate-300 text-sm font-semibold hover:border-slate-500 transition-colors"
            >
              ← Back
            </button>
          )}
          <div className="flex-1 flex flex-col gap-2">
            {submitError && (
              <p className="text-xs text-red-400 text-center">{submitError}</p>
            )}
            {step < TOTAL ? (
              <button
                onClick={handleNext}
                className="w-full py-3 rounded-full bg-amber-400 text-slate-950 text-sm font-semibold hover:bg-amber-300 transition-colors"
              >
                Next →
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="w-full py-3 rounded-full bg-amber-400 text-slate-950 text-sm font-semibold hover:bg-amber-300 transition-colors disabled:opacity-50"
              >
                {submitting ? "Saving..." : "Complete setup →"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function Confirmation() {
  const botUrl = `https://t.me/${process.env.NEXT_PUBLIC_BOT_USERNAME ?? "MeridianBot"}`;
  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col items-center justify-center px-6 text-center">
      <p className="text-xs font-semibold tracking-widest text-amber-400 uppercase mb-6">
        Setup complete
      </p>
      <h1 className="text-4xl font-bold mb-4">You&apos;re on Path B.</h1>
      <p className="text-slate-400 max-w-sm mb-10">
        Your first brief arrives at your chosen time tomorrow morning. Head back to Telegram to confirm your setup.
      </p>
      <a
        href={botUrl}
        className="inline-flex items-center justify-center rounded-full px-8 py-4 bg-amber-400 text-slate-950 text-sm font-semibold hover:bg-amber-300 transition-colors"
      >
        Return to Meridian →
      </a>
    </div>
  );
}
