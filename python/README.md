# EntaiFab Python SDK

The official Python SDK for the [EntaiFab](https://app.entaifab.com) AI Gateway. Same call shapes as the OpenAI Python SDK — if you've used that, you already know this. Zero runtime dependencies.

## Install

```bash
pip install entaifab
```

## Quick start

```python
from entaifab import EntaiFab

client = EntaiFab(
    api_key="efab_your_key_here",          # or set ENTAIFAB_API_KEY
    organization_id="your-org-guid-here",  # or set ENTAIFAB_ORGANIZATION_ID
)

response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

Your organization id and API keys are on the EntaiFab dashboard under **Developer Tools** and **AI Providers → API Keys**. Each key is bound to a provider + model when you create it, so there's nothing to configure here — no `model` required.

## Coming from OpenAI

```diff
-from openai import OpenAI
-client = OpenAI(api_key="sk-...")
+from entaifab import EntaiFab
+client = EntaiFab(api_key="efab_...", organization_id="<org-guid>")

 response = client.chat.completions.create(
-    model="gpt-4o-mini",
+    model="gemini-2.5-flash",
     messages=[{"role": "user", "content": "Hello!"}],
 )
 print(response.choices[0].message.content)
```

Everything else — `response.choices[0].message.content`, `response.usage.total_tokens`, error class names like `AuthenticationError` — matches.

## Choosing a model

Your API key is bound to one provider + model in the EntaiFab dashboard (**AI Providers → API Keys**) — that binding is the routing decision, not anything you send here.

- **Omit `model` entirely** (recommended) — the key's bound model is used. Your EntaiFab admin can later repoint the key at a different provider/model and your code never changes.
- **Pass `model`** set to the provider's exact model id (e.g. `"gemini-2.5-flash"`) to override it for that call — never a route alias, and it's still served through the same provider the key is bound to.
- `provider` is deprecated and ignored by the gateway now that routing is fully determined by the key; the SDK still accepts it so older code doesn't break, but there's no reason to set it.

```python
# Normal path — the key's bound model decides:
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello!"}],
)
```

List the model your key is bound to:

```python
for model in client.models.list():
    print(model.id)
```

## Errors

```python
from entaifab import EntaiFab, AuthenticationError, APIStatusError

try:
    response = client.chat.completions.create(messages=[...])
except AuthenticationError:
    ...  # bad or revoked API key
except APIStatusError as error:
    print(error.status_code, error.code, error.message)
```

## Configuration

| Constructor argument | Environment variable | Notes |
| --- | --- | --- |
| `api_key` | `ENTAIFAB_API_KEY` | Required. `efab_...` gateway key. |
| `organization_id` | `ENTAIFAB_ORGANIZATION_ID` | Required unless `base_url` is set. |
| `base_url` | `ENTAIFAB_BASE_URL` | Full gateway URL; overrides `organization_id`. |
| `timeout` | — | Seconds per request, default 60. |

## License

MIT
