#!/bin/bash
# Throwaway: runs the two scratch harnesses against ~/agents-scratch/ordin-agents.
cd ~/agents-scratch
docker run --rm -v "$PWD/ordin":/work -v "$PWD/ordin-agents":/agents:ro -v "$PWD/target":/target -w /work \
  -v ordin-cargo:/usr/local/cargo/registry -e CARGO_INCREMENTAL=0 -e CARGO_TARGET_DIR=/target -e ORDIN_AGENTS_DIR=/agents \
  --network host rust:1.96 bash -c "apt-get update -qq >/dev/null && apt-get install -y -qq libdbus-1-dev pkg-config >/dev/null && \
  cargo test -p ordin-checker --test zz_bundled_agents -- --nocapture; echo CHECKER_EXIT=\$?; \
  cargo test -p ordin-catalogue --test zz_bundled_agents -- --nocapture; echo CATALOGUE_EXIT=\$?" > run.log 2>&1
echo EXIT=$? >> run.log
