import type { Metadata, Viewport } from "next";
import { Inter, Noto_Naskh_Arabic } from "next/font/google";

import { AppHeader } from "@/shared/ui/app-header";

import "./globals.css";

const inter = Inter({
  subsets: ["latin", "latin-ext"],
  variable: "--font-inter",
  display: "swap",
});

const naskh = Noto_Naskh_Arabic({
  subsets: ["arabic"],
  variable: "--font-naskh",
  display: "swap",
});

export const metadata: Metadata = {
  title: "GiraffeGraph",
  description: "Hadis metninden ravi zincirini çıkarır, kontrol eder ve grafa yazar.",
  icons: { icon: "/icon.png" },
};

export const viewport: Viewport = {
  themeColor: "#0b1624",
};

type RootLayoutProps = Readonly<{
  children: React.ReactNode;
}>;

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="tr" className={`${inter.variable} ${naskh.variable}`}>
      <body>
        <a className="skip-link" href="#icerik">
          İçeriğe geç
        </a>
        <AppHeader />
        {children}
      </body>
    </html>
  );
}
