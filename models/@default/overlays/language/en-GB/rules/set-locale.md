---
apiVersion: ai.enterprise/v1
kind: rule
metadata:
  id: "urn:ordin:default:overlays:language:en-GB:set-locale"
  name: Set active locale to en-GB
  description: "Sets the agent's writing language to British English. Identifiers and quotations are left as they are."
  version: 1.0.0
  owner: gatblau
---

# Set active locale: en-GB

The active output locale for this workspace is **en-GB** (British English).

This rule is read by the `urn:ordin:default:rules:layer:output-language` layer rule, which governs how the active locale is applied to generated artefacts. See that rule for the full set of conventions and exemptions.

Spelling, idiom, date format, and number format conventions follow British English. Examples of expected forms: *behaviour*, *organise*, *colour*, *centre*, *catalogue*, *programme*, *defence*, *licence* (noun), *license* (verb), DD Month YYYY date format.
