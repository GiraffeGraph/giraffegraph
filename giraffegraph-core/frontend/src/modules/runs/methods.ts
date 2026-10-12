import { isExtractionProviderConfigured } from "@/modules/projects/api";

export interface ExtractionMethod {
  /** The provider name the server knows. */
  provider: string;
  title: string;
  description: string;
  /** How many hadiths go into one request; smaller keeps the progress line moving. */
  batchSize: number;
}

export const RULES_METHOD: ExtractionMethod = {
  provider: "rule_based_isnad",
  title: "Kurallarla (ücretsiz, anında)",
  description:
    "Rivayet kalıplarını tanıyan hazır kurallar isnadı okur. İnternet bağlantısı ya da anahtar gerekmez.",
  batchSize: 10,
};

const MODEL_METHODS: ExtractionMethod[] = [
  {
    provider: "anthropic",
    title: "Dil modeliyle: Claude",
    description:
      "Sunucuda tanımlı Anthropic hesabını kullanır. Ücretlidir ve kurallardan yavaştır.",
    batchSize: 3,
  },
  {
    provider: "openai",
    title: "Dil modeliyle: OpenAI",
    description:
      "Sunucuda tanımlı OpenAI hesabını kullanır. Ücretlidir ve kurallardan yavaştır.",
    batchSize: 3,
  },
];

let availableMethods: Promise<ExtractionMethod[]> | null = null;

/**
 * The rules are always there; a language model is offered only when the server has it set up.
 * What the server has does not change while the page is open, so it is asked once.
 */
export function listAvailableMethods(projectId: string): Promise<ExtractionMethod[]> {
  availableMethods ??= Promise.all(
    MODEL_METHODS.map((method) =>
      isExtractionProviderConfigured(projectId, method.provider).catch(() => false),
    ),
  ).then((checks) => [RULES_METHOD, ...MODEL_METHODS.filter((_, index) => checks[index])]);
  return availableMethods;
}
