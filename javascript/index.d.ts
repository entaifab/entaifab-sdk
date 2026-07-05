export interface ClientOptions {
  /** Gateway API key ("efab_..."). Falls back to ENTAIFAB_API_KEY. */
  apiKey?: string;
  /** Organization id from the EntaiFab Developer Tools page. Falls back to ENTAIFAB_ORGANIZATION_ID. */
  organizationId?: string;
  /** Full gateway base URL, e.g. "https://api.entaifab.com/gateway/<org-guid>/v1". Overrides organizationId. Falls back to ENTAIFAB_BASE_URL. */
  baseURL?: string;
  /** Per-request timeout in milliseconds. Default 60000. */
  timeout?: number;
}

export interface ChatCompletionMessageParam {
  role: "system" | "user" | "assistant" | (string & {});
  content: string;
}

export interface ChatCompletionCreateParams {
  /** OpenAI-style messages. */
  messages: ChatCompletionMessageParam[];
  /**
   * Optional override of the provider's exact model id (e.g. "gemini-2.5-flash") - never a route alias.
   * Omit it and the API key's bound model is used; this is the normal path.
   */
  model?: string;
  /** @deprecated Ignored by the gateway - routing is fully determined by the API key now. Kept only for backward compatibility. */
  provider?: "gemini" | "openai" | (string & {});
  temperature?: number;
  max_tokens?: number;
  [key: string]: unknown;
}

export interface ChatCompletionMessage {
  role: string;
  content: string;
}

export interface ChatCompletionChoice {
  index: number;
  message: ChatCompletionMessage;
  finish_reason: string | null;
}

export interface CompletionUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface ChatCompletion {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: ChatCompletionChoice[];
  usage?: CompletionUsage | null;
}

export interface Model {
  id: string;
  object: "model";
  created: number;
  owned_by: string;
}

export interface ModelsPage {
  object: "list";
  data: Model[];
}

export declare class EntaiFabError extends Error {}

export declare class APIConnectionError extends EntaiFabError {}

export declare class APIStatusError extends EntaiFabError {
  status: number;
  code: string | null;
  type: string | null;
}

export declare class BadRequestError extends APIStatusError {}
export declare class AuthenticationError extends APIStatusError {}
export declare class PermissionDeniedError extends APIStatusError {}
export declare class NotFoundError extends APIStatusError {}
export declare class ConflictError extends APIStatusError {}
export declare class RateLimitError extends APIStatusError {}
export declare class InternalServerError extends APIStatusError {}

export declare class EntaiFab {
  constructor(options?: ClientOptions);

  apiKey: string;
  baseURL: string;
  timeout: number;

  chat: {
    completions: {
      create(params: ChatCompletionCreateParams): Promise<ChatCompletion>;
    };
  };

  models: {
    list(): Promise<ModelsPage>;
  };
}

export default EntaiFab;
