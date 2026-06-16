import { redirect } from "next/navigation";
import SettingsForm from "@/components/settings/SettingsForm";
import { createServerClient } from "@/lib/supabase/server";
import type { Profile } from "@/types";

interface Props {
  searchParams: { tid?: string };
}

export default async function SettingsPage({ searchParams }: Props) {
  if (!searchParams.tid) {
    redirect("/");
  }

  const tid = parseInt(searchParams.tid, 10);
  if (isNaN(tid)) redirect("/");

  const supabase = createServerClient();

  const { data: user } = await supabase
    .from("users")
    .select("id")
    .eq("telegram_id", tid)
    .single();

  if (!user) redirect("/");

  const { data: profile } = await supabase
    .from("profiles")
    .select("*")
    .eq("user_id", user.id)
    .single();

  if (!profile) redirect(`/onboarding?tid=${searchParams.tid}`);

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <SettingsForm
        telegramId={searchParams.tid}
        userId={user.id}
        profile={profile as Profile}
      />
    </div>
  );
}
