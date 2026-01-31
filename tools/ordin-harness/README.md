# Ordin harness

Two test files that run Ordin's own Checker and Catalogue Service against this repository. They
are not part of ordin and must not be committed there.

1. Copy an ordin checkout (`git archive HEAD`) to a scratch folder.
2. Put `checker_bundled_agents.rs` at `crates/ordin-checker/tests/zz_bundled_agents.rs` and
   `catalogue_bundled_agents.rs` at `crates/ordin-catalogue/tests/zz_bundled_agents.rs`.
3. Run `run.sh` (a `rust:1.96` container; it sets `ORDIN_AGENTS_DIR` to this repository's copy).

`checker_bundled_agents.rs` reuses the helpers of ordin's `crates/ordin-checker/tests/parity.rs`.
