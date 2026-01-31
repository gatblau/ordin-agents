# Mermaid setup (MkDocs Material)

A ```` ```mermaid ```` fence renders as a diagram only once `mkdocs.yml` declares the extensions below. Without them MkDocs treats the block as ordinary code and prints the diagram source to the reader — and because that is valid Markdown, `--strict` does not catch it. This is the one failure in the pack that no gate reports, so the configuration comes first.

## The `markdown_extensions` block

This is the whole block `docsgen` writes when it creates `mkdocs.yml`. It covers the Mermaid fence, the callouts and the content tabs in `authoring-syntax.md`.

```yaml
markdown_extensions:
  - admonition                    # callouts
  - pymdownx.details              # collapsible callouts
  - pymdownx.superfences:         # custom fences, including Mermaid
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:              # content tabs
      alternate_style: true
```

The `custom_fences` entry is the load-bearing part: it routes a fence named `mermaid` to a `<div class="mermaid">` that MkDocs Material's bundled Mermaid support then renders in the browser. Declaring `superfences` without it leaves the fence as a code block.

## When the project already has a `mkdocs.yml`

Merge rather than replace. Read the existing `markdown_extensions`, add only the entries that are absent, and leave every other key alone. In particular:

- If `pymdownx.superfences` is present but carries no `custom_fences`, add the `mermaid` entry to it. Do not add a second `superfences` key — YAML keeps the last one and silently drops the first.
- If the project uses a different Mermaid route (a `mkdocs-mermaid2-plugin` entry under `plugins:`), leave it. Two Mermaid paths in one site fight each other. Report which one is in use and emit fences in that form.

## The fence

```markdown
```mermaid
flowchart LR
    A["Payment requested"] --> B["Checked"]
    B --> C["Sent to the bank"]
```
```

`documentationConventions.diagramFence.form` carries the opener as a literal string so `docsgen` emits exactly what this configuration routes.

## Verifying it renders

`mkdocs build --strict` does **not** prove a diagram rendered — it only proves the Markdown parsed. To check the extension is wired up, build the site and confirm the generated HTML contains a `<div class="mermaid">` for a page you know carries a fence. A `<pre><code class="language-mermaid">` instead means `custom_fences` is missing or misspelled.

## Theme note

MkDocs Material renders Mermaid using the palette of the active colour scheme, so a diagram authored once works in both light and dark mode. Do not set colours inside the diagram source; hard-coded colours look correct in one scheme and become unreadable in the other.
