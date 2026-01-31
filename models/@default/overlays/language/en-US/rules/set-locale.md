---
apiVersion: ai.enterprise/v1
kind: rule
metadata:
  id: "urn:ordin:default:overlays:language:en-US:set-locale"
  name: Set active locale to en-US
  description: "Sets the agent's writing language to American English. Identifiers and quotations are left as they are."
  version: 1.0.0
  owner: gatblau
---

# Set active locale: en-US

The active output locale for this workspace is **en-US** (American English).

This rule is read by the `urn:ordin:default:rules:layer:output-language` layer rule, which governs how the active locale is applied to generated artefacts. See that rule for the full set of conventions and exemptions.

Spelling, idiom, date format, and number format conventions follow American English. Examples of expected forms: *behavior*, *organize*, *color*, *center*, *catalog*, *program*, *defense*, *license* (noun and verb), Month DD, YYYY date format.
