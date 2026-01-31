# Authoring syntax (MkDocs Material)

The markup `docsgen` emits. Every construct here needs an entry in `markdown_extensions` — see `mermaid-setup.md`, which lists the whole block in one place.

## Page front matter

MkDocs parses a leading YAML block and exposes it as `page.meta`. Unknown keys are preserved, so the rung contract travels in the page rather than in a side file.

```markdown
---
title: Why a payment is retried
rung: 4
prerequisites:
  - concepts/02-payment-lifecycle.md
enables: "I can explain why a payment is retried three times before it is set aside."
concepts:
  - retry budget
  - dead-letter queue
---
```

`title` is MkDocs Material's own key and sets the browser tab and the page heading. The other four are the rung contract.

## Callouts

The admonition syntax, used for the prerequisite block at the top of every rung above the first.

```markdown
!!! info "Before this page"
    Read [What happens to a payment](02-payment-lifecycle.md) first. This page
    assumes you can name the states a payment moves through.
```

Body lines are indented by four spaces. The title is optional in MkDocs; `docsgen` always supplies one, because an untitled callout gives the reader no reason to stop and read it.

Available kinds, as declared in `documentationConventions.callout.kinds`:

| Kind | Use for |
|---|---|
| `note` | An aside the reader can skip without losing the thread |
| `abstract` | A summary of what the page will establish |
| `info` | The prerequisite block |
| `tip` | A shortcut or a better habit |
| `warning` | Something that will bite the reader if ignored |
| `example` | A worked case |
| `question` | A question the page then answers |

Do not invent a kind. An unrecognised kind renders as literal text, and under `--strict` it does not fail the build, so the fault reaches the reader.

## Content tabs

For the same idea expressed two ways — a request in two protocols, a value in two formats.

```markdown
=== "What the caller sends"
    A card number, an amount, and a reference the caller chooses.

=== "What comes back"
    A decision, and the same reference so the caller can match them up.
```

Use sparingly. Tabs hide content behind a click, which suits alternatives and hurts a sequence the reader must follow.

## Links

Relative, and to the `.md` file rather than to the built URL:

```markdown
[What happens to a payment](02-payment-lifecycle.md)
```

MkDocs rewrites the extension when it builds. A link written to the built path (`../payment-lifecycle/`) works in the browser but is not checked at build time, so it rots silently. A relative `.md` link that resolves to no page is a warning, and `--strict` turns that into a failed build.

## What not to emit

- **No raw HTML.** It bypasses the theme, breaks the dark colour scheme, and is not checked by the build.
- **No `path:line` citations in the page body.** Evidence lives in the run report. A citation is exactly the jargon the site exists to avoid.
- **No credential, token, key, connection string or environment-variable value.** Write a placeholder: `<your-token>`, `<connection-string>`. This holds even when the target project checked the real value in.
- **No emoji shortcodes.** They need another extension and add nothing to an explanation.
