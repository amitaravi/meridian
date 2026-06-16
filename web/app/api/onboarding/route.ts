import { NextRequest, NextResponse } from "next/server";
import { createServerClient } from "@/lib/supabase/server";

export async function POST(request: NextRequest) {
  let body: Record<string, unknown>;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const {
    telegram_id,
    goal_areas,
    why_text,
    path_a,
    path_b,
    accomplishments,
    brief_hour,
    brief_minute,
    timezone,
  } = body;

  if (typeof telegram_id !== "number" || !telegram_id) {
    return NextResponse.json({ error: "telegram_id required" }, { status: 400 });
  }

  const supabase = createServerClient();

  // Resolve user_id from telegram_id, creating the user if missing
  let userId: string;
  const { data: existingUser } = await supabase
    .from("users")
    .select("id")
    .eq("telegram_id", telegram_id)
    .single();

  if (existingUser) {
    userId = existingUser.id as string;
  } else {
    const { data: newUser, error: createErr } = await supabase
      .from("users")
      .insert({ telegram_id })
      .select("id")
      .single();

    if (createErr || !newUser) {
      console.error("Failed to create user:", createErr);
      return NextResponse.json({ error: "Failed to save profile" }, { status: 500 });
    }
    userId = newUser.id as string;
  }

  const { error: profileErr } = await supabase.from("profiles").upsert({
    user_id: userId,
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
    console.error("Failed to upsert profile:", profileErr);
    return NextResponse.json({ error: "Failed to save profile" }, { status: 500 });
  }

  // Notify bot to register scheduler job immediately (non-fatal if bot is sleeping)
  const botUrl = process.env.BOT_INTERNAL_URL;
  const key = process.env.INTERNAL_API_KEY;
  if (botUrl && key) {
    fetch(`${botUrl}/internal/register-job`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Internal-Key": key },
      body: JSON.stringify({
        user_id: userId,
        telegram_id,
        brief_hour,
        brief_minute,
        timezone,
      }),
    }).catch((e) => console.error("Bot scheduler notification failed:", e));
  }

  return NextResponse.json({ success: true });
}
