import type { Metadata } from "next";

import { ChainsScreen } from "@/modules/graph/components/chains-screen";

export const metadata: Metadata = { title: "Zincirleri oku · GiraffeGraph" };

export default function ChainsPage() {
  return <ChainsScreen />;
}
