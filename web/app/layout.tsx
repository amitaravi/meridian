import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Meridian",
  description: "Reconnect with your future self, every morning.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
