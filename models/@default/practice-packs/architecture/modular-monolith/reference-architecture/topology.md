# Reference architecture — topology

The single-deployable, in-process module topology this pack carries.
Language-neutral and broker-free.

## Diagram

```mermaid
flowchart TB
  subgraph Deployable [Single deployable · one process]
    direction LR
    subgraph O [Module: orders]
      OF[Facade] --> OI[internal + tables]
    end
    subgraph B [Module: billing]
      BF[Facade] --> BI[internal + tables]
    end
    subgraph S [Module: shipping]
      SF[Facade] --> SI[internal + tables]
    end
    BF -->|facade call| OF
    SF -->|facade call| OF
    BUS((In-process event bus))
    OI -. orders.order.placed .-> BUS
    BUS -. handler .-> BI
  end
  DB[(One database<br/>module-owned tables)]
  OI --- DB
  BI --- DB
  SI --- DB
```

## Single deployable, hard internal boundaries

- One process, one database. Internal structure is N modules, each with a
  **published facade** and a private `internal/`.
- Cross-module calls go **facade → facade** only; no module imports another's
  internals (`../patterns/module-facade.md`).
- Loose reactions go through the **in-process event bus**
  (`../patterns/in-process-events.md`) — no broker, no network, no redelivery.
- Each table is owned by exactly one module (`../modules/ownership-map.md`); only
  the owner writes it.

## Flow

1. A request enters a module and is handled behind its facade.
2. A cross-module need is met by calling another module's facade (synchronous,
   in-process) or by publishing an in-process domain event for loose coupling.
3. State changes that span modules run in **one in-process transaction** — there
   is no distributed transaction because there is no network boundary.

## ADRs (binding)

- **no-internal-cross-module-calls** — internals are private to a module.
- **facade-only-cross-module** — the published facade is the only entry point.
- **one-db-module-owned-tables** — one database; one owner per table.
