# Module ownership map

How ownership is recorded and enforced in a single-database modular monolith. The
ownership map is the artefact that keeps "one owner per table" auditable.

## The rule

- One database. Every table is owned by **exactly one** module.
- Only the owning module's code writes (INSERT/UPDATE/DELETE) its tables.
- Cross-module reads go through the owner's facade
  (`../patterns/module-facade.md`); a module never writes another module's table.

## Recording ownership

Keep an explicit map from table → owning module, reviewed as part of any schema
change. A worked shape:

| Table | Owning module | Read by (via facade) |
|---|---|---|
| `orders`, `order_lines` | `orders` | `billing`, `shipping` |
| `invoices`, `payments` | `billing` | `orders` (status only) |
| `shipments` | `shipping` | `orders` (status only) |

The map is the single place that answers "who may change this table?". A table
with no owner, or two owners, is a defect.

## Enforcing ownership

- **Naming / placement.** Owned tables live under (or are namespaced by) the
  owning module, so a cross-module write is visible in review.
- **Migrations.** A migration touching a table is authored by that table's owner
  and reviewed against the map; a migration that lets a second module write an
  existing table changes ownership and must be a deliberate map update.
- **Observability.** `cross_module_call_total{from,to}` and
  `module_request_total{module}` (`../observability/required-signals.md`) surface
  traffic that crosses boundaries, so creeping shared-write coupling is visible.

## Extraction readiness

Because each module owns its tables and is reached only through a facade, lifting
one module out into its own service later is a **local** change: replace the
in-process facade call with a remote one and split the owned tables out with it.
A shared-write table would make that extraction a data-migration project — which
is exactly why the single-owner rule is non-negotiable.
