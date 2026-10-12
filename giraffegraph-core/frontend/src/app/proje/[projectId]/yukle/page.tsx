import type { Metadata } from "next";

import { LoadScreen } from "@/modules/ingestion/components/load-screen";

export const metadata: Metadata = { title: "Metin yükle · GiraffeGraph" };

export default function LoadPage() {
  return <LoadScreen />;
}
