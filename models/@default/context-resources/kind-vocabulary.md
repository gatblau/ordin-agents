---
apiVersion: ai.enterprise/v1
kind: context-resource
metadata:
  id: "urn:ordin:default:context-resources:kind-vocabulary"
  name: Artefact-kind vocabulary
  version: 1.0.0
  owner: gatblau
  description: "Reference for the anatomy of an agent — what each leaf artefact kind means (Skill, Rule, Command, ContextResource, OperatingMode, ToolBinding) and how to tell them apart. Load it when deciding which kind a piece of authored content belongs to, or when a kind name is used and its distinction from a neighbour is unclear."
---

# Artefact kinds — vocabulary

Reference for the leaf kinds that compose an agent. Knowledge to consult when classifying content, not a rule that binds behaviour. The decisive question for every kind is *what role does this content play* — behaviour, constraint, knowledge, entry point, or access.

## The leaf kinds

- **Skill** — a **procedure the agent performs**. Steps to follow, invoked by the harness on demand. Loading mode: on-demand.
- **Rule** — a **constraint the agent obeys**. A "must" or "must not" that is always in force. If the agent ignoring the document is a *mistake*, it is a Rule. Loading mode: always-on.
- **Command** — an **entry point a user invokes**. A user-facing verb (a slash-command) that drives one or more skills. Loading mode: registered-invocation.
- **ContextResource** — **knowledge the agent reads**. Reference material — a glossary, a standard, a domain note — consulted when relevant, never executed and never binding. If the agent merely *would have benefited* from reading it, it is a ContextResource. Loading mode: on-demand.
- **OperatingMode** — a **stance the agent adopts**. One mode is active at a time; it governs which tools are permitted for the current step. Loading mode: mode-switch.
- **ToolBinding** — **access to an external system**. Declares a tool (an MCP server) the agent may reach, with its scope. Loading mode: structural.
- **SystemRole** — the **persona** the agent assumes for a workspace. Loading mode: always-on.

## Telling neighbours apart

The four axes an agent is built from, and the mistake that confuses each pair:

- **Skill vs Rule** — a procedure versus a constraint. "Run the tests, then lint" is a Skill; "tests must pass before merge" is a Rule.
- **Rule vs ContextResource** — a constraint versus knowledge. If the agent is *bound* by the document it is a Rule; if it is merely *informed* by it, it is a ContextResource.
- **ContextResource vs PracticePack** — general knowledge versus stack-specific convention. Content that changes with the language or framework belongs in a PracticePack (selected per install), not a ContextResource.
- **Command vs Skill** — an entry point versus the procedure it drives. `/apply` is a Command; the `codegen` procedure it invokes is a Skill.

## Composition roots

Leaf kinds are never installed alone. A **WorkspaceProfile** composes them into an installable interactive agent; a **CrewProfile** composes a deployment of one or more profiles for autonomous operation; a **PracticePack** supplies stack conventions selected at install time. A ContextResource is referenced by a WorkspaceProfile through its `contextResources` relation and is offered in the Composer under **References**.
