import type { Metadata } from "next";

import { ReviewScreen } from "@/modules/review/components/review-screen";

export const metadata: Metadata = { title: "İncele · GiraffeGraph" };

export default function ReviewPage() {
  return <ReviewScreen />;
}
