const REVIEWER_ID_STORAGE_KEY = "giraffegraph.reviewerId";

export function readStoredReviewer(): string {
  try {
    return window.localStorage.getItem(REVIEWER_ID_STORAGE_KEY)?.trim() ?? "";
  } catch {
    return "";
  }
}

export function storeReviewer(name: string): void {
  try {
    window.localStorage.setItem(REVIEWER_ID_STORAGE_KEY, name);
  } catch {
    // Storage can be unavailable (private mode); the name then lasts for this visit only.
  }
}
