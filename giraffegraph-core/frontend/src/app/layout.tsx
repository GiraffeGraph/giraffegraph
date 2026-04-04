import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "GiraffeGraph Dashboard",
  description: "Internal dashboard for GiraffeGraph Core.",
};

type RootLayoutProps = Readonly<{
  children: React.ReactNode;
}>;

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
