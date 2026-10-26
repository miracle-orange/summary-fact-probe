# Summary Fact Probe

This repository stores the offline audit and experiment artifacts for the summary-fact-probe dataset.

## Included in this repo
- Analysis/audit outputs under `audit-20261014-exp04-*`
- Processed source data under `data/`
- Compressed run archives under `runs/*.tar.gz`
- Small run folders kept for lightweight metadata

## Large data policy
The largest raw run directories are compressed before upload to keep GitHub sync practical.

Example:
```bash
tar -xzf runs/exp04-2gpu.tar.gz -C runs
tar -xzf runs/exp05-omni1800-2gpu.tar.gz -C runs
```
