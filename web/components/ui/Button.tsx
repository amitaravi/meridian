import Link from "next/link";

type Variant = "primary" | "outline";

interface ButtonProps {
  href: string;
  children: React.ReactNode;
  variant?: Variant;
  external?: boolean;
  className?: string;
}

export default function Button({
  href,
  children,
  variant = "primary",
  external = false,
  className = "",
}: ButtonProps) {
  const base =
    "inline-flex items-center justify-center rounded-full px-8 py-4 text-sm font-semibold tracking-wide transition-colors duration-150";
  const variants: Record<Variant, string> = {
    primary: "bg-amber-400 text-slate-950 hover:bg-amber-300",
    outline:
      "border border-slate-700 text-slate-200 hover:border-slate-500 hover:text-white",
  };
  const cls = `${base} ${variants[variant]} ${className}`;

  if (external) {
    return (
      <a href={href} target="_blank" rel="noopener noreferrer" className={cls}>
        {children}
      </a>
    );
  }

  return (
    <Link href={href} className={cls}>
      {children}
    </Link>
  );
}
