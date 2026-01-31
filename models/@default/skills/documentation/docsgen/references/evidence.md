# evidence — tracing claims and reporting conflicts

Every claim a page makes is traceable to the target project. This reference defines the traceability record `docsgen` holds per claim (step 4), and how a disagreement between design, specification and source is recorded rather than silently resolved (step 5). A teaching site earns trust by never asserting something the code does not do.

## The traceability record

For each claim a page will make, `docsgen` holds one record:

```yaml
claim: <the assertion, in the page's own words>
source: design | spec | source        # which layer the claim is drawn from
citation: <path:line>                 # the exact location the claim traces to
conflict: <none | a reference to the conflict record below>
```

The record is why the run report can list, per claim, where it came from. A claim with no citation is not written: an assertion the target does not support is either dropped or raised in the report as an unverifiable gap, never stated as fact. This is the `identifier-verification` discipline applied to prose — a symbol, route, table or config key named on a page is one visible at its citation.

## The three layers and their standing

- **Source** is authoritative for behaviour. What the code does is what the running system does, so where behaviour is documented, the citation is to source.
- **Specification** is authoritative for the contract the system is meant to honour. A specification claim with a matching source citation is documented plainly. A specification claim with no source counterpart is intent (see below).
- **Design** is authoritative for intent — the problem and the shape. A design claim about a behaviour is confirmed against source before it is stated as fact.

## Recording a conflict

Design, specification and source **disagree** when they make incompatible claims about the same behaviour — the specification states a retry budget of 5, the source implements 3. `docsgen` does not choose a winner by editing either side. It:

1. Documents the **source** behaviour on the page (the code is what runs), stating the value plainly.
2. Records a conflict entry naming **both** readings and **both** citations.
3. Carries the conflict into the run report, under `Conflicts`.
4. Modifies no specification, design or source file — the report is the whole output of a conflict.

The reader of the page sees the true behaviour; the operator reading the report sees that the specification and the code disagree and can reconcile them through the appropriate sync path. `docsgen` surfaces the drift; it does not resolve it.

## Marking an intent-only claim

Design or specification sometimes states something with **no counterpart in source** — a reconciliation report the design describes that the code has not yet built. This is not a conflict; it is unbuilt intent. `docsgen`:

1. Writes the claim on the relevant page, **labelled as intent** — "planned, not yet built" — so a reader never mistakes a plan for a live capability.
2. Records it under `Intent-only claims` in the run report, with the design or specification citation.

An intent-only claim is never written as though the behaviour exists. Labelling it is what keeps the site honest about the gap between what the system is meant to do and what it does today.
