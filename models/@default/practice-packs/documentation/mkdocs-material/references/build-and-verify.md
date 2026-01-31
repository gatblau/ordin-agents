# Build and verify (MkDocs Material)

The command that checks the site, what it catches, what it does not, and what the target project must have installed. `docsgen` reports this command to the operator; it never runs it. Running a build is Execute mode and the operator's decision.

## The command

```
mkdocs build --strict
```

Declared as `documentationConventions.buildCommand`. `--strict` promotes every MkDocs warning to an error and returns a non-zero exit code, which is what makes it a gate rather than a report.

To read the site locally instead of building it:

```
mkdocs serve --strict
```

Same checks, served at `http://127.0.0.1:8000` with live reload.

## What `--strict` catches

| Fault | Reported as |
|---|---|
| A relative link resolving to no page | Warning → error under `--strict` |
| A page under `siteRoot` missing from `nav:` | Warning → error under `--strict` |
| A `nav:` entry pointing at a file that does not exist | Warning → error under `--strict` |
| An unreadable or malformed `mkdocs.yml` | Error regardless of `--strict` |
| Malformed YAML front matter on a page | Error regardless of `--strict` |

The first row is why `documentationConventions.linkCheck` is `strict`: the ladder's prerequisite links are ordinary relative links, so a rung pointing at a page that was never written fails the build. That is the second half of the prerequisite guarantee — `docsgen` refuses to emit such a page in the first place, and this catches any that slip through a hand edit afterwards.

## What it does not catch

Know these, because each one reaches the reader silently:

- **A Mermaid fence that did not render.** Valid Markdown either way. See `mermaid-setup.md` for how to check the generated HTML.
- **An unrecognised callout kind.** Renders as literal text.
- **A link to a built URL rather than to a `.md` file.** Not checked, so it rots when a page moves.
- **Prose that teaches the wrong thing.** No build command has an opinion about whether an explanation is true or useful.

## Target-project prerequisites

These belong to the target project, not to the workspace. `docsgen` reads none of them and does not check they are present — it reports the build command and lets the operator find out.

```
pip install mkdocs-material
```

That single distribution pulls in MkDocs and the `pymdown-extensions` package the `markdown_extensions` block depends on. A Python interpreter is assumed.

The project may pin these in `requirements.txt`, `pyproject.toml`, or a lockfile — follow whatever that project already does rather than introducing a new mechanism.

## Publication

Out of scope for this pack and for `docsgen`. The workspace safety floor prohibits publication verbs, so no artefact here runs `mkdocs gh-deploy`, pushes a branch, or uploads a built site. The build produces `site/` locally; what happens to it is the operator's decision and their pipeline's job.
