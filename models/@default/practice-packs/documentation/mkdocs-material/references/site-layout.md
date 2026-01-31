# Site layout (MkDocs Material)

Where the documentation site sits in a target project, and where `docsgen` writes each part of the concept ladder.

## Directory tree

MkDocs expects the configuration file at the project root and the pages under `docs/` beside it. Both values are declared in this pack's `documentationConventions`; the tree below is what they resolve to.

```
<target project root>/
  mkdocs.yml              # configFile — carries site metadata, theme, extensions and nav
  docs/                   # siteRoot — every page docsgen writes lives under here
    index.md              # rung 1: the problem the system solves
    concepts/
      01-<slug>.md        # one concept per rung, numbered in ladder order
      02-<slug>.md
    composition/
      01-<slug>.md        # how the concepts fit together
    walkthroughs/
      01-<slug>.md        # end-to-end journeys, naming only established concepts
```

## Which ladder section goes where

| Ladder section | Directory | Notes |
|---|---|---|
| The problem the system solves | `docs/index.md` | Always rung 1. Always the site's home page, so a reader landing on the site starts at the bottom of the ladder |
| One concept per rung | `docs/concepts/` | Filenames carry a two-digit ordinal so the on-disk order matches the ladder even though `nav:` governs the rendered order |
| How the concepts compose | `docs/composition/` | Omitted entirely at `depth: minimal` |
| End-to-end walkthroughs | `docs/walkthroughs/` | One page at `depth: standard`; one per principal journey at `depth: full` |

## Rules

- **Write nothing outside `siteRoot` and `configFile`.** These two paths are the whole write scope. A path discovered while reading the target project is never a write target.
- **Refuse an unsafe root.** A `siteRoot` or `configFile` that is absolute or contains a `..` segment stops the run before any file is written.
- **Never overwrite a page the operator wrote.** A file already present under `siteRoot` that carries no rung front matter was authored by a human. Report it and leave it; do not fold it into the ladder and do not replace it.
- **The ordinal in a filename is not the rung number.** Ordinals restart in each directory; `rung` is unique across the whole site and is declared in front matter.
- **An existing project may already have `docs/`.** Many do, holding design and specification material. Write the site alongside what is there, into the three subdirectories above, rather than clearing the directory.

## When the target project has no site yet

The common case on a first run. `docsgen` creates `mkdocs.yml` with the minimum MkDocs Material needs — `site_name`, `theme.name: material`, the `markdown_extensions` listed in `mermaid-setup.md`, and the `nav:` block — plus the `docs/` tree above. The operator runs the build themselves; `docsgen` never does.
