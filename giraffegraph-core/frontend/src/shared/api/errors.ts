export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export interface ErrorExplanation {
  /** What the person can do about it, in plain Turkish. */
  advice: string;
  /** The raw message, for the "ayrıntı" disclosure. */
  detail: string | null;
}

export function isProviderNotConfigured(error: unknown): boolean {
  return (
    error instanceof ApiError &&
    error.status === 422 &&
    error.message.includes("is not configured for candidate extraction")
  );
}

export function explainError(error: unknown): ErrorExplanation {
  if (error instanceof ApiError) {
    const detail = `${error.status} · ${error.message}`;
    if (isProviderNotConfigured(error)) {
      return {
        advice:
          "Seçtiğin yöntem bu sunucuda kurulu değil. Kurallarla çıkarmayı seçebilir ya da sunucuyu yöneten kişiden dil modeli anahtarını tanımlamasını isteyebilirsin.",
        detail,
      };
    }
    if (error.status === 404) {
      return {
        advice:
          "Aranan kayıt sunucuda yok. Sunucu yeniden başlatıldıysa içindeki veriler silinmiş olabilir; projeler sayfasına dönüp tekrar bakabilirsin.",
        detail,
      };
    }
    if (error.status === 409) {
      return {
        advice:
          "Bu işlem daha önce yapılmış görünüyor. Sayfayı yenileyip son duruma bakabilirsin.",
        detail,
      };
    }
    if (error.status === 422) {
      return {
        advice:
          "Sunucu bu isteği olduğu gibi kabul etmedi. Girdiğin bilgileri kontrol edip tekrar deneyebilirsin.",
        detail,
      };
    }
    if (error.status === 502) {
      return {
        advice:
          "Dil modeli servisine ulaşılamadı. Biraz sonra tekrar deneyebilir ya da kurallarla çıkarmayı seçebilirsin.",
        detail,
      };
    }
    return {
      advice:
        "Sunucuda beklenmeyen bir sorun oldu. Tekrar deneyebilirsin; sorun sürerse sunucu kayıtlarına bakmak gerekir.",
      detail,
    };
  }

  if (error instanceof TypeError) {
    return {
      advice:
        "Sunucuya ulaşılamadı. Sunucunun çalıştığından emin olup birkaç saniye sonra tekrar deneyebilirsin.",
      detail: error.message,
    };
  }

  if (error instanceof Error) {
    return { advice: error.message, detail: null };
  }

  return { advice: "Beklenmeyen bir sorun oldu. Tekrar deneyebilirsin.", detail: null };
}
