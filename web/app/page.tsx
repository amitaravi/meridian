import type { Metadata } from "next";
import Button from "@/components/ui/Button";

const BOT_URL = `https://t.me/${process.env.NEXT_PUBLIC_BOT_USERNAME ?? "MeridianBot"}`;

export const metadata: Metadata = {
  title: "Meridian — See your two futures. Show up for the right one.",
  description:
    "A daily ritual for ambitious professionals who know what they want to build — and keep losing the thread. Morning brief + pre-generated time blocks, delivered to Telegram.",
  openGraph: {
    title: "Meridian — See your two futures. Show up for the right one.",
    description:
      "A daily ritual for ambitious professionals. Morning brief + pre-generated time blocks, delivered to Telegram.",
    type: "website",
  },
};

export default function HomePage() {
  return (
    <div className="bg-slate-950 text-white">
      <Nav />
      <Hero />
      <Problem />
      <Paths />
      <HowItWorks />
      <Preview />
      <Pricing />
      <BottomCTA />
      <Footer />
    </div>
  );
}

function Nav() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-5 bg-slate-950/80 backdrop-blur-sm border-b border-slate-800/50">
      <span className="text-base font-bold tracking-tight">Meridian</span>
      <Button href={BOT_URL} external>
        Start →
      </Button>
    </nav>
  );
}

function Hero() {
  return (
    <section className="min-h-screen flex flex-col items-center justify-center text-center px-6 pt-24 pb-16">
      <p className="text-xs font-semibold tracking-widest text-amber-400 uppercase mb-8">
        Daily ritual · Ambitious professionals
      </p>
      <h1 className="text-5xl sm:text-7xl font-bold leading-tight tracking-tight mb-6 max-w-3xl">
        See your two futures.
        <br />
        Show up for the right one.
      </h1>
      <p className="text-lg sm:text-xl text-slate-400 max-w-lg mb-10 leading-relaxed">
        A morning brief that reconnects you to the life you&apos;re building —
        then gives you today&apos;s exact hourly plan. No blank page. No drift.
      </p>
      <Button href={BOT_URL} external>
        Start with Meridian →
      </Button>
      <p className="mt-4 text-sm text-slate-600">
        Free for 7 days. No credit card.
      </p>
    </section>
  );
}

function Problem() {
  const stages = [
    { step: "01", text: "Strong week. You're executing on the thing." },
    { step: "02", text: "Disruption. Travel, a heavy work sprint, a holiday." },
    { step: "03", text: 'Reconnecting to "why" feels heavy. Defer it.' },
    { step: "04", text: "Default habits fill the gap. Weeks pass." },
  ];

  return (
    <section className="py-24 px-6 border-t border-slate-800/50">
      <div className="max-w-3xl mx-auto">
        <p className="text-xs font-semibold tracking-widest text-slate-500 uppercase mb-6">
          The problem
        </p>
        <h2 className="text-3xl sm:text-4xl font-bold mb-6 leading-tight">
          You know what you want to build.
          <br />
          <span className="text-slate-500">So why does another week pass?</span>
        </h2>
        <p className="text-slate-400 text-lg leading-relaxed mb-12">
          It&apos;s not a motivation problem. You&apos;ve proven what you can do
          when the stakes are clear. The issue is the thread connecting today to
          the future you&apos;re building — it breaks, silently, every time life
          gets busy.
        </p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {stages.map(({ step, text }) => (
            <div key={step} className="bg-slate-900 rounded-xl p-5">
              <p className="text-xs font-mono text-slate-600 mb-3">{step}</p>
              <p className="text-sm text-slate-300 leading-snug">{text}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Paths() {
  return (
    <section className="py-24 px-6 border-t border-slate-800/50">
      <div className="max-w-3xl mx-auto">
        <p className="text-xs font-semibold tracking-widest text-slate-500 uppercase mb-6">
          The core mechanic
        </p>
        <h2 className="text-3xl sm:text-4xl font-bold mb-4">
          Every morning, your two futures.
        </h2>
        <p className="text-slate-400 mb-10">
          Specific to you. Written in your words. Delivered to Telegram at the
          time you set.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <div className="bg-slate-900 rounded-2xl p-8 border border-slate-800">
            <p className="text-xs font-semibold tracking-widest text-slate-500 uppercase mb-4">
              Path A — The comfortable future
            </p>
            <p className="text-slate-400 text-sm leading-relaxed">
              Still in the same role at 34. The side project never left Notion.
              Not because you couldn&apos;t — because you kept waiting for a
              better week to start.
            </p>
          </div>
          <div className="bg-amber-950/30 rounded-2xl p-8 border border-amber-400/20">
            <p className="text-xs font-semibold tracking-widest text-amber-400 uppercase mb-4">
              Path B — The ambitious future
            </p>
            <p className="text-slate-300 text-sm leading-relaxed">
              You shipped it. The side project became the thing. You remember
              exactly which morning you decided to stop waiting and treated the
              first hour as sacred.
            </p>
          </div>
        </div>
        <p className="text-sm text-slate-500 text-center">
          These come from your onboarding — not templates. The contrast lands
          differently when it&apos;s your actual life.
        </p>
      </div>
    </section>
  );
}

function HowItWorks() {
  const steps = [
    {
      number: "01",
      title: "Tell Meridian your two paths",
      body: "A 5-minute web onboarding. Your Path A, your Path B, your goals, past accomplishments, and the time you want your brief delivered.",
    },
    {
      number: "02",
      title: "Wake up to your daily brief",
      body: "A Telegram message with a vivid contrast between your two futures — generated fresh each morning. Followed immediately by today's exact time blocks. Pre-decided. Just start.",
    },
    {
      number: "03",
      title: "Execute and build the streak",
      body: "Mark blocks done as you go. A streak builds. A weekly scoreboard shows every day you chose Path B. You stop asking what to work on — the answer is already there.",
    },
  ];

  return (
    <section className="py-24 px-6 border-t border-slate-800/50">
      <div className="max-w-3xl mx-auto">
        <p className="text-xs font-semibold tracking-widest text-slate-500 uppercase mb-6">
          How it works
        </p>
        <h2 className="text-3xl sm:text-4xl font-bold mb-12">
          Three minutes every morning.
        </h2>
        <div className="space-y-10">
          {steps.map(({ number, title, body }) => (
            <div key={number} className="flex gap-8">
              <p className="text-sm font-mono text-amber-400 mt-0.5 flex-shrink-0 w-6">
                {number}
              </p>
              <div>
                <h3 className="font-semibold text-white mb-2">{title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{body}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Preview() {
  const blocks = [
    {
      color: "bg-blue-500",
      area: "Career Pivot",
      mins: 50,
      task: "Write the first 500 words of the blog post you've been outlining.",
    },
    {
      color: "bg-amber-400",
      area: "Side Project",
      mins: 25,
      task: "Wire up the Stripe webhook — it's been open in 3 tabs since Tuesday.",
    },
  ];

  return (
    <section className="py-24 px-6 border-t border-slate-800/50">
      <div className="max-w-3xl mx-auto">
        <p className="text-xs font-semibold tracking-widest text-slate-500 uppercase mb-6">
          What arrives
        </p>
        <h2 className="text-3xl sm:text-4xl font-bold mb-4">
          Today&apos;s plan, already written.
        </h2>
        <p className="text-slate-400 mb-10">
          Generated from your goals. Ready in Telegram when you wake up.
        </p>
        <div className="bg-slate-900 rounded-2xl p-6 border border-slate-800 max-w-sm">
          <div className="flex items-center gap-3 mb-5 pb-4 border-b border-slate-800">
            <div className="w-8 h-8 rounded-full bg-amber-400 flex items-center justify-center text-slate-950 text-xs font-bold flex-shrink-0">
              M
            </div>
            <span className="text-sm font-semibold">Meridian</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed mb-5 italic">
            &ldquo;At 32, Path A has a name: still in the same role, watching
            someone else build the thing you described to friends at 26. Today
            is another small deferral — or it isn&apos;t. You shipped last week.
            You know how.&rdquo;
          </p>
          <div className="space-y-3">
            {blocks.map(({ color, area, mins, task }) => (
              <div key={area} className="bg-slate-800 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <div className={`w-2 h-2 rounded-full ${color} flex-shrink-0`} />
                  <span className="text-xs font-semibold text-slate-300">
                    {area}
                  </span>
                  <span className="text-xs text-slate-600 ml-auto">
                    {mins} min
                  </span>
                </div>
                <p className="text-xs text-slate-400 mb-3">{task}</p>
                <div className="flex gap-2">
                  <span className="flex-1 py-1.5 rounded-lg bg-slate-700 text-xs text-slate-300 font-medium text-center">
                    ✓ Done
                  </span>
                  <span className="flex-1 py-1.5 rounded-lg bg-slate-700 text-xs text-slate-500 font-medium text-center">
                    → Skip
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function Pricing() {
  return (
    <section className="py-24 px-6 border-t border-slate-800/50">
      <div className="max-w-3xl mx-auto text-center">
        <p className="text-xs font-semibold tracking-widest text-slate-500 uppercase mb-6">
          Pricing
        </p>
        <h2 className="text-3xl sm:text-4xl font-bold mb-4">
          A career investment.
          <br />
          <span className="text-slate-500">Not a productivity app.</span>
        </h2>
        <p className="text-slate-400 mb-12">
          Less than one coffee a week to stay on the path to the life you
          actually want.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-2xl mx-auto text-left">
          <div className="bg-slate-900 rounded-2xl p-8 border border-slate-800">
            <p className="text-base font-bold mb-2">Free trial</p>
            <p className="text-3xl font-bold mb-5">
              $0
              <span className="text-sm text-slate-500 font-normal"> / 7 days</span>
            </p>
            <ul className="space-y-2 text-sm text-slate-400">
              <li>Daily morning brief</li>
              <li>Pre-generated time blocks</li>
              <li>Block completion + streak</li>
              <li>Weekly scoreboard</li>
            </ul>
          </div>
          <div className="bg-amber-950/30 rounded-2xl p-8 border border-amber-400/20">
            <p className="text-base font-bold mb-2 text-amber-400">Pro</p>
            <p className="text-3xl font-bold mb-5">
              $15
              <span className="text-sm text-slate-500 font-normal"> / month</span>
            </p>
            <ul className="space-y-2 text-sm text-slate-400">
              <li>Everything in Free</li>
              <li>Unlimited daily briefs</li>
              <li>$120 / year — save 33%</li>
              <li className="text-slate-600">Payments opening soon</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}

function BottomCTA() {
  return (
    <section className="py-24 px-6 border-t border-slate-800/50 text-center">
      <div className="max-w-2xl mx-auto">
        <h2 className="text-4xl sm:text-5xl font-bold leading-tight mb-6">
          Which path are you
          <br />
          walking tomorrow?
        </h2>
        <p className="text-slate-400 mb-10">
          Five minutes of setup. A morning ritual that keeps the thread alive.
        </p>
        <Button href={BOT_URL} external>
          Start with Meridian →
        </Button>
        <p className="mt-4 text-sm text-slate-600">
          Free for 7 days. No credit card.
        </p>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="py-8 px-6 border-t border-slate-800/50">
      <div className="max-w-3xl mx-auto flex items-center justify-between">
        <span className="text-sm font-bold">Meridian</span>
        <span className="text-xs text-slate-600">
          Reconnect with who you&apos;re becoming.
        </span>
      </div>
    </footer>
  );
}
