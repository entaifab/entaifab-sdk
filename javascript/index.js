/**
 * Official JavaScript SDK for the EntaiFab AI Gateway.
 *
 * Same call shapes as the OpenAI Node SDK, pointed at your organization's
 * EntaiFab gateway. Zero dependencies; uses the global fetch available in
 * Node 18+, browsers, and edge runtimes.
 *
 *   import EntaiFab from "entaifab";
 *
 *   const client = new EntaiFab({ apiKey: "efab_...", organizationId: "<org-guid>" });
 *   const response = await client.chat.completions.create({
 *     messages: [{ role: "user", content: "Hello!" }],
 *   });
 *   console.log(response.choices[0].message.content);
 *
 * Each API key is bound to one provider + model in the EntaiFab dashboard,
 * so `model` is optional - omit it and the key's bound model is used. Pass
 * it only to override, and only with the provider's exact model id (e.g.
 * "gemini-2.5-flash"), never a route alias.
 */

const VERSION = "0.1.0";
const DEFAULT_API_HOST = "https://api.entaifab.com";
const DEFAULT_TIMEOUT_MS = 60_000;

/** Base class for every error thrown by this SDK. */
export class EntaiFabError extends Error {}

/** The request never reached the gateway (network failure or timeout). */
export class APIConnectionError extends EntaiFabError {
  constructor(message = "Connection error.", { cause } = {}) {
    super(message, cause ? { cause } : undefined);
    this.name = "APIConnectionError";
  }
}

/** The gateway responded with a non-success HTTP status. */
export class APIStatusError extends EntaiFabError {
  constructor(message, { status, code, type } = {}) {
    super(message);
    this.name = new.target.name;
    /** HTTP status of the response. */
    this.status = status;
    /** EntaiFab error code, e.g. "INVALID_API_KEY". */
    this.code = code ?? null;
    /** OpenAI-style error type, e.g. "invalid_request_error". */
    this.type = type ?? null;
  }
}

export class BadRequestError extends APIStatusError {}       // 400
export class AuthenticationError extends APIStatusError {}   // 401
export class PermissionDeniedError extends APIStatusError {} // 403
export class NotFoundError extends APIStatusError {}         // 404
export class ConflictError extends APIStatusError {}         // 409
export class RateLimitError extends APIStatusError {}        // 429
export class InternalServerError extends APIStatusError {}   // 5xx (incl. 502 upstream provider failures)

function statusErrorClass(status) {
  if (status >= 500) return InternalServerError;
  return (
    {
      400: BadRequestError,
      401: AuthenticationError,
      403: PermissionDeniedError,
      404: NotFoundError,
      409: ConflictError,
      429: RateLimitError,
    }[status] ?? APIStatusError
  );
}

export class EntaiFab {
  /**
   * @param {Object} [options]
   * @param {string} [options.apiKey] Gateway API key ("efab_..."). Falls back to ENTAIFAB_API_KEY.
   * @param {string} [options.organizationId] Organization id from the Developer Tools page. Falls back to ENTAIFAB_ORGANIZATION_ID.
   * @param {string} [options.baseURL] Full gateway base URL; overrides organizationId. Falls back to ENTAIFAB_BASE_URL.
   * @param {number} [options.timeout] Per-request timeout in milliseconds (default 60000).
   */
  constructor({ apiKey, organizationId, baseURL, timeout = DEFAULT_TIMEOUT_MS } = {}) {
    const env = (typeof process !== "undefined" && process.env) || {};

    this.apiKey = apiKey ?? env.ENTAIFAB_API_KEY;
    if (!this.apiKey) {
      throw new EntaiFabError(
        "No API key provided. Pass { apiKey } or set the ENTAIFAB_API_KEY environment variable.",
      );
    }

    baseURL = baseURL ?? env.ENTAIFAB_BASE_URL;
    organizationId = organizationId ?? env.ENTAIFAB_ORGANIZATION_ID;

    if (baseURL) {
      this.baseURL = baseURL.replace(/\/+$/, "");
    } else if (organizationId) {
      this.baseURL = `${DEFAULT_API_HOST}/gateway/${organizationId}/v1`;
    } else {
      throw new EntaiFabError(
        "No gateway endpoint configured. Pass { organizationId } (or { baseURL }), " +
          "or set the ENTAIFAB_ORGANIZATION_ID environment variable.",
      );
    }

    this.timeout = timeout;

    this.chat = {
      completions: {
        /**
         * Create a chat completion. `model` is optional - omit it and the
         * API key's bound model is used (the normal path; an admin can swap
         * the provider/model behind your key later without any code
         * change). Pass it only to override, and only with the provider's
         * exact model id (e.g. "gemini-2.5-flash"), never a route alias.
         * `provider` is deprecated and ignored by the gateway - routing is
         * fully determined by the API key now.
         */
        create: (params) => this.#request("POST", "/chat/completions", params),
      },
    };

    this.models = {
      /** List the model this API key is bound to (empty if the key has no route assigned yet). */
      list: () => this.#request("GET", "/models"),
    };
  }

  async #request(method, path, body) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);

    let response;
    try {
      response = await fetch(`${this.baseURL}${path}`, {
        method,
        headers: {
          Authorization: `Bearer ${this.apiKey}`,
          "Content-Type": "application/json",
          Accept: "application/json",
          "X-Client": `entaifab-js/${VERSION}`,
        },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: controller.signal,
      });
    } catch (cause) {
      const timedOut = cause && cause.name === "AbortError";
      throw new APIConnectionError(
        timedOut ? `Request timed out after ${this.timeout}ms.` : "Could not reach the EntaiFab gateway.",
        { cause },
      );
    } finally {
      clearTimeout(timer);
    }

    if (!response.ok) {
      let message = `HTTP ${response.status}`;
      let code = null;
      let type = null;
      try {
        const detail = (await response.json())?.error ?? {};
        message = detail.message ?? message;
        code = detail.code ?? null;
        type = detail.type ?? null;
      } catch {
        // Non-JSON error body; keep the status-line message.
      }
      throw new (statusErrorClass(response.status))(message, { status: response.status, code, type });
    }

    return response.json();
  }
}

export default EntaiFab;
