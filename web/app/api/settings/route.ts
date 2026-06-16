import { NextRequest, NextResponse } from "next/server";
import { createServerClient } from "@/lib/supabase/server";

async function notifyBotScheduler(params: {
  user_id: string;
  telegram_id: number;
  brief_hour: number;
  brief_minute: number;
  timezone: string;
}): Promise<void> {
  const botUrl = process.env.BOT_INTERNAL_URL;
  const key = process.env.INTERNAL_API_KEY;
  if (!botUrl || !key) return;

  try {
    await fetch(`${botUrl}/internal/register-job`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Internal-Key": key },
      body: JSON.stringify(params),
    });
  } catch (e) {
    console.error("Failed to notify bot scheduler:", e);
    // Non-fatal: scheduler picks up changes on next bot restart
  }
}

export async function PUT(request: NextRequest) {
  let body: Record<string, unknown>;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const {
    telegram_id,
    user_id,
    goal_areas,
    why_text,
    path_a,
    path_b,
    accomplishments,
    brief_hour,
    brief_minute,
    timezone,
  } = body;

  if (!user_id || !telegram_id) {
    return NextResponse.json({ error: "user_id and telegram_id required" }, { status: 400 });
  }

  const supabase = createServerClient();

  const { error: profileErr } = await supabase.from("profiles").upsert({
    user_id,
    goal_areas,
    why_text,
    path_a,
    path_b,
    accomplishments,
    brief_hour,
    brief_minute,
    timezone,
    updated_at: new Date().toISOString(),
  });

  if (profileErr) {
    console.error("Failed to update profile:", profileErr);
    return NextResponse.json({ error: "Failed to save changes" }, { status: 500 });
  }

  await notifyBotScheduler({
    user_id: user_id as string,
    telegram_id: telegram_id as number,
    brief_hour: brief_hour as number,
    brief_minute: brief_minute as number,
    timezone: timezone as string,
  });

  return NextResponse.json({ success: true });
}
