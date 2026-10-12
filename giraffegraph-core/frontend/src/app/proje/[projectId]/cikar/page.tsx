import type { Metadata } from "next";

import { ExtractScreen } from "@/modules/runs/components/extract-screen";

export const metadata: Metadata = { title: "Zincirleri çıkar · GiraffeGraph" };

export default function ExtractPage() {
  return <ExtractScreen />;
}
