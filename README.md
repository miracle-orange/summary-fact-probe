# Summary Fact Probe

This repository contains the offline analysis, experiment metadata, and compressed run artifacts for the summary fact probe project.

## Repository policy
- Source code and analysis outputs are kept in git.
- Very large raw run directories are archived as compressed tar.gz files under `runs/`.
- Local caches such as `cache/` and `models/` are intentionally excluded.

## Extracting large run bundles
```bash
tar -xzf runs/exp04-2gpu.tar.gz -C runs
tar -xzf runs/exp05-omni1800-2gpu.tar.gz -C runs
```
