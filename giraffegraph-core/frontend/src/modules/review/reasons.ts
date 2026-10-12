import { ApiError } from "@/shared/api/errors";

/** Why a suggestion is waiting for a person, said the way a colleague would say it. */
const REASON_SENTENCES: Record<string, string> = {
  value_not_in_quote:
    "Önerilen isim, sistemin gösterdiği alıntının içinde geçmiyor. İsim değiştirilmiş ya da metnin başka bir yerinden tamamlanmış olabilir.",
  quote_not_in_segment:
    "Sistemin gösterdiği alıntı bu metinde bulunamadı. Öneri metne dayanmıyor olabilir.",
  missing_evidence:
    "Bu öneri için metinden bir alıntı gösterilmedi; neye dayandığı bilinmiyor.",
  node_confidence_threshold: "Sistem bu öneriden yeterince emin değil.",
  relation_confidence_threshold: "Sistem bu öneriden yeterince emin değil.",
  potential_duplicate_node:
    "Aynı ravi bu hadiste iki kez önerildi. Hangisinin kalacağına sen karar ver; biri zaten kabul edildiyse bunu reddedebilirsin.",
  potential_duplicate_relation:
    "Aynı bağlantı bu hadiste iki kez önerildi. Hangisinin kalacağına sen karar ver; biri zaten kabul edildiyse bunu reddedebilirsin.",
  missing_relation_merge_key:
    "Bu bağlantının hangi hadise ya da zincirdeki hangi sıraya ait olduğu eksik. Düzelt’e basıp eksik alanı doldurabilirsin.",
  relation_dependency_review:
    "Bu bağlantının iki ucundaki ravilerden biri hâlâ karar bekliyor. O raviye karar verdiğinde bu bağlantı kendiliğinden sonuçlanır.",
  relation_dependency_rejected: "Bu bağlantının ucundaki ravilerden biri reddedildi.",
  schema_type_proposal:
    "Sistem, bu projede tanımlı olmayan bir tür önerdi. Kabul edersen bu not kayda geçer; projenin tanımları kendiliğinden değişmez.",
  schema_property_proposal:
    "Sistem, bu projede tanımlı olmayan bir alan önerdi. Kabul edersen bu not kayda geçer; projenin tanımları kendiliğinden değişmez.",
  property_value_not_allowed:
    "Önerilen değer, bu alan için izin verilen seçenekler arasında değil.",
};

const FALLBACK_REASON = "Sistem bu öneriyi kendi başına kabul edemedi; karar senin.";

export function reasonSentence(reasonCode: string): string {
  return REASON_SENTENCES[reasonCode] ?? FALLBACK_REASON;
}

/** A plain sentence for the refusals the server gives to a decision; null when it is something else. */
export function decisionRefusal(error: unknown): string | null {
  if (!(error instanceof ApiError)) {
    return null;
  }
  const message = error.message;
  if (message.includes("would create a duplicate")) {
    return "Bu bilgi bu hadiste zaten var, aynısı ikinci kez kabul edilemez. Bu öneriyi reddedebilir ya da düzelterek farklı bir kayıt hâline getirebilirsin.";
  }
  if (message.includes("when both node candidates are validated")) {
    return "Bağlantının iki ucundaki raviler kabul edilmeden bağlantı kabul edilemez. Önce o ravilere karar ver; istersen bu öneriyi şimdilik geç.";
  }
  if (message.includes("is already completed")) {
    return "Bu hadis grafa yazılmış; kararları artık değiştirilemez.";
  }
  if (message.includes("is missing merge keys") || message.includes("missing required properties")) {
    return "Bu öneride doldurulması gereken alanlar eksik. Düzelt’e basıp eksikleri tamamlayabilirsin.";
  }
  if (message.includes("would invalidate an existing relation")) {
    return "Bu düzeltme, ravinin bağlı olduğu bir bağlantıyı geçersiz kılıyor. Yalnızca ismi düzeltmeyi deneyebilirsin.";
  }
  return null;
}
