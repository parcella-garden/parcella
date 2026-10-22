# Spam filter external API: back to a generic contract

**Note: retired.** The spam filter was removed with the built-in ticket
module (ADR 0080); its leftovers went in [ADR 0103](./0103-spam-filter-leftovers-removed.md).
Kept as the design record.

**Context:** [ADR 0038](./0038-spam-filter-external-api-tied-to-apilayer-for-now.md)
tied `app/spam_filter.py`'s external spam-check integration directly to
apilayer.com's Spam Check API -- an `apikey` header, a plain-text body,
a `{"is_spam": bool}` response -- after the originally-planned generic
contract turned out to be speculative and untested against any real
service. That ADR flagged the vendor lock-in as a pre-open-source loose
end and left two ways to resolve it before going live: reintroduce a
generic contract with a documented reference adapter, or support a
short list of named providers with explicit per-provider code.

**What actually happened:** apilayer.com's Spam Check API stopped
working. With the integration hard-wired to that one vendor's specific
request/response shape, there was no fallback -- exactly the risk ADR
0038 called out.

**Decision: generic contract, with a runnable reference adapter.**
`_external_check()` now speaks a vendor-neutral shape:

```
POST {spam_api_url}
Authorization: Bearer {spam_api_key}   (only sent if a key is configured)
Content-Type: application/json
{"sender_email": "...", "subject": "...", "content": "..."}

-> 200 OK
   {"spam_score": 0.0-1.0}
```

Any mismatch -- timeout, non-2xx, a response that doesn't parse, a
missing or non-numeric `spam_score` -- is treated as "no external
signal," same as no API being configured at all, and falls back to the
built-in heuristics. This was already true of the apilayer-specific
version and stays true here: an outage or misconfiguration of the
external service must never block ticket creation.

`integrations/spam-check-adapter/` is the reference adapter ADR 0038
asked for: a small stdlib-only Python script implementing this exact
contract, meant to be read and adapted rather than deployed as-is. An
admin wanting apilayer, Akismet, a self-hosted filter like rspamd, or
anything else points Parcella at their own copy of the adapter (or an
equivalent service) instead of Parcella needing to know about any
specific provider.

**Why the generic contract over explicit per-provider support (ADR
0038's other option):** the adapter pattern means Parcella's own code
never needs to change again when a provider changes its API, gets
deprecated, or a self-hoster wants to swap providers -- exactly the
failure mode that just happened with apilayer. The cost is that
whoever wants external checking has to run one more small service
(or a thin serverless function) instead of just pasting in a vendor's
URL and key -- judged worth it given a hard-wired vendor integration
has now broken once already.

**Not addressed here:** `admin.settings.spam_help`'s help text in
`/admin/settings` was already vendor-silent (it never named apilayer),
so it didn't need correcting. It also doesn't yet document the exact
contract shape -- that lives in `app/spam_filter.py`'s docstring, this
ADR, and the reference adapter's README for now.
