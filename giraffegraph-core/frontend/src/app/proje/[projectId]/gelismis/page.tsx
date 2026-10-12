import type { Metadata } from "next";

import { AdvancedScreen } from "@/modules/projects/components/advanced-screen";

export const metadata: Metadata = { title: "Gelişmiş · GiraffeGraph" };

export default function AdvancedPage() {
  return <AdvancedScreen />;
}
