# EntaiFab SDK

Official SDKs for the **EntaiFab AI Gateway** — one endpoint, one key, any AI provider. Each API key is bound to a provider and model your admin configures (Gemini, OpenAI, ...) in the EntaiFab dashboard, so applications never hard-code a vendor — and never even need to name a model.

The API is OpenAI-compatible by design: if you've used the OpenAI SDK, switching is literally changing the import and the key.

| Language | Package | Directory |
| --- | --- | --- |
| Python | `pip install entaifab` | [`python/`](python/) |
| JavaScript / TypeScript | `npm install entaifab` | [`javascript/`](javascript/) |

## Quick start

**Python**

```python
from entaifab import EntaiFab

client = EntaiFab(api_key="efab_...", organization_id="<org-guid>")

response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

**JavaScript**

```js
import EntaiFab from "entaifab";

const client = new EntaiFab({ apiKey: "efab_...", organizationId: "<org-guid>" });

const response = await client.chat.completions.create({
  messages: [{ role: "user", content: "Hello!" }],
});
console.log(response.choices[0].message.content);
```

Find your organization id and create API keys in the EntaiFab dashboard: **Developer Tools** and **AI Providers → API Keys**.

## How model selection works

Each API key is bound to one provider + model when it's created (**AI Providers → API Keys**) — that's the whole routing decision, made once in the dashboard instead of in every call:

1. **Omit `model` entirely** — the key's bound model is used. This is the normal path, and it's a feature: your admin can repoint the key at a different provider/model later without any code change on your side.
2. **Pass `model`** set to the provider's exact model id (e.g. `gemini-2.5-flash`, never a route alias) to override it for that one call. It's still served through the same provider the key is bound to.

## Design principles

- **Drop-in for OpenAI SDK users** — same resource layout (`client.chat.completions.create`, `client.models.list`), same response shapes, same error class names.
- **Zero dependencies** — both packages use only the standard library / platform `fetch`. Nothing extra to audit.
- **Thin by intention** — the gateway does the routing, masking, logging, and provider auth; the SDK just speaks HTTP to it.

## License

[MIT](LICENSE)
