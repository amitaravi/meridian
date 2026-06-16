import { redirect } from "next/navigation";
import OnboardingForm from "@/components/onboarding/OnboardingForm";

interface Props {
  searchParams: { tid?: string };
}

export default function OnboardingPage({ searchParams }: Props) {
  if (!searchParams.tid) {
    redirect("/");
  }

  return <OnboardingForm telegramId={searchParams.tid} />;
}
