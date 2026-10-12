import Image from "next/image";
import Link from "next/link";

import { Glossary } from "@/shared/ui/glossary";

export function AppHeader() {
  return (
    <header className="app-header">
      <div className="app-header-inner">
        <Link href="/" className="brand" aria-label="GiraffeGraph, projeler sayfası">
          <Image src="/icon.png" alt="" width={28} height={28} priority />
          <span>GiraffeGraph</span>
        </Link>
        <Glossary />
      </div>
    </header>
  );
}
