import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "John Studio Monograph",
  description: "A bilingual architectural studio monograph website.",
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
