# EntaiFab JavaScript SDK

> **Deprecated.** No longer maintained — use the official [OpenAI Node SDK](https://github.com/openai/openai-node) pointed at your gateway's base URL instead (see **Developer Tools** in the EntaiFab dashboard).

The official JavaScript/TypeScript SDK for the [EntaiFab](https://app.entaifab.com) AI Gateway. Same call shapes as the OpenAI Node SDK — if you've used that, you already know this. Zero dependencies; works in Node 18+, browsers, and edge runtimes.

## Install

```bash
npm install entaifab
```

## Quick start

```js
import EntaiFab from "entaifab";

const client = new EntaiFab({
  apiKey: "efab_your_key_here",          // or set ENTAIFAB_API_KEY
  organizationId: "your-org-guid-here",  // or set ENTAIFAB_ORGANIZATION_ID
});

const response = await client.chat.completions.create({
  messages: [{ role: "user", content: "Hello!" }],
});
console.log(response.choices[0].message.content);
```

Your organization id and API keys are on the EntaiFab dashboard under **Developer Tools** and **AI Providers → API Keys**. Each key is bound to a provider + model when you create it, so there's nothing to configure here — no `model` required.

## Coming from OpenAI

```diff
-import OpenAI from "openai";
-const client = new OpenAI({ apiKey: "sk-..." });
+import EntaiFab from "entaifab";
+const client = new EntaiFab({ apiKey: "efab_...", organizationId: "<org-guid>" });

 const response = await client.chat.completions.create({
-  model: "gpt-4o-mini",
+  model: "gemini-2.5-flash",
   messages: [{ role: "user", content: "Hello!" }],
 });
 console.log(response.choices[0].message.content);
```

Everything else — `response.choices[0].message.content`, `response.usage.total_tokens`, error class names like `AuthenticationError` — matches.

## Choosing a model

Your API key is bound to one provider + model in the EntaiFab dashboard (**AI Providers → API Keys**) — that binding is the routing decision, not anything you send here.

- **Omit `model` entirely** (recommended) — the key's bound model is used. Your EntaiFab admin can later repoint the key at a different provider/model and your code never changes.
- **Pass `model`** set to the provider's exact model id (e.g. `"gemini-2.5-flash"`) to override it for that call — never a route alias, and it's still served through the same provider the key is bound to.
- `provider` is deprecated and ignored by the gateway now that routing is fully determined by the key; the SDK still accepts it so older code doesn't break, but there's no reason to set it.

```js
// Normal path — the key's bound model decides:
const response = await client.chat.completions.create({
  messages: [{ role: "user", content: "Hello!" }],
});
```

List the model your key is bound to:

```js
const models = await client.models.list();
for (const model of models.data) console.log(model.id);
```

## Errors

```js
import EntaiFab, { AuthenticationError, APIStatusError } from "entaifab";

try {
  await client.chat.completions.create({ messages: [...] });
} catch (error) {
  if (error instanceof AuthenticationError) {
    // bad or revoked API key
  } else if (error instanceof APIStatusError) {
    console.error(error.status, error.code, error.message);
  }
}
```

## Browser usage

The SDK works in browsers, but remember an API key shipped in front-end code is visible to anyone. Use a key dedicated to that site so it can be revoked independently, or keep the key server-side.

## License

MIT
