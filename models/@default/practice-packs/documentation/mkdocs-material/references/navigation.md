# Navigation (MkDocs Material)

MkDocs decides the order of pages from the `nav:` block in `mkdocs.yml`, not from the filesystem. This is why `documentationConventions.navigation.declaredIn` is `manifest` and `ordering` is `explicit`: `docsgen` writes the block as well as the pages, or the ladder renders in alphabetical order and stops teaching anything.

## The block

```yaml
nav:
  - What this is for: index.md
  - Concepts:
      - Payments, in this system's words: concepts/01-payments.md
      - What happens to a payment: concepts/02-payment-lifecycle.md
      - Why a payment is retried: concepts/03-retries.md
  - How it fits together: composition/01-services.md
  - Walkthroughs:
      - A card payment, end to end: walkthroughs/01-card-payment.md
```

Paths are relative to `siteRoot`. The label left of the colon is what the reader sees in the navigation; it is the page's title in the reader's words, not its filename.

## Rules

- **Every emitted page appears exactly once.** A page listed twice renders twice in the navigation and doubles the ladder. A page not listed is still built, but MkDocs warns about it — and under `--strict` a warning fails the build.
- **The order in the block is the rung order.** The reader's path down the page list is the order the ladder was derived in. Nothing else enforces it: the front-matter `rung` field records the intent, but the reader only ever experiences `nav:`.
- **Group labels carry no page.** `Concepts:` and `Walkthroughs:` above are section headings with children, not links. Do not point a group label at a page.
- **Rung 1 is the first entry and is `index.md`.** MkDocs serves `index.md` as the site root, so a reader arriving at the bare URL lands on the bottom rung rather than on whichever page happens to sort first.
- **Labels are prose, not slugs.** `What happens to a payment` teaches; `payment-lifecycle` does not.
- **Preserve entries the operator added.** If `mkdocs.yml` already has a `nav:` block containing pages outside the three ladder directories, keep those entries and merge the ladder in. Rewriting the block wholesale would delete a human's navigation.

## Interaction with the prerequisite block

Navigation order and prerequisite order are related but not the same thing. `nav:` is a single linear reading path; `prerequisites` in a page's front matter is a set, and a rung may depend on more than one earlier rung. Where they disagree, `nav:` must still be a valid linearisation — every page appears after all of its prerequisites. `docsgen` refuses to emit a page whose prerequisites have not been emitted, which makes that property hold by construction.
