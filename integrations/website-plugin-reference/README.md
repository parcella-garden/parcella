# Website plugin reference receiver

A minimal, runnable implementation of the receiving side of the
[Parcella Website Plugin Protocol](../../docs/website-plugin-protocol.md).
It's the starting point for anyone writing a Parcella plugin for a CMS
(TYPO3, Contao, Drupal, Joomla, ...): every rule of the spec is in
`reference_receiver.py`, in plain standard-library Python, ready to be
translated into the CMS's own language.

It stores drafts in a JSON file instead of a CMS. **Don't use it in
production.**

## Try it

```
export PARCELLA_SHARED_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
python3 reference_receiver.py 8091
```

In Parcella, under Admin -> Integrations -> Website:

1. Choose **Parcella plugin**.
2. Plugin address: `http://<this host>:8091/parcella/v1`
3. Shared secret: the value of `PARCELLA_SHARED_SECRET`.
4. "Test connection", then save.

Create a website draft from an announcement: it appears in
`reference_drafts.json` with `"status": "draft"`. Change that to
`"published"` and add a `"public_url"` to see how Parcella's print
notice picks up the link for its QR code.

## Writing a real plugin

What a CMS plugin adds on top of this file:

- store the shared secret in the CMS's own settings, generate it on
  install, and show it together with the endpoint URL on the plugin's
  settings page;
- turn a draft into the CMS's native, unpublished content (and an image
  into its media library);
- return the CMS's edit link as `edit_url`, and the live URL as
  `public_url` once a human has published the post.

The WordPress plugin in `../wordpress/parcella-connector/` shows how to
bundle Parcella's inbound features (signup and contact forms, calendar)
into the same plugin. ADR 0105 explains the overall design and the
licensing question to settle before a marketplace upload.
