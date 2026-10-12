import { ButtonLink } from "@/shared/ui/button";
import { EmptyState } from "@/shared/ui/states";

export default function NotFound() {
  return (
    <main id="icerik" className="page">
      <EmptyState
        icon="search"
        title="Bu sayfa bulunamadı"
        action={
          <ButtonLink href="/" variant="primary" icon="arrowLeft">
            Projelere dön
          </ButtonLink>
        }
      >
        Adres yanlış yazılmış ya da sayfa taşınmış olabilir. Projeler sayfasından devam
        edebilirsin.
      </EmptyState>
    </main>
  );
}
