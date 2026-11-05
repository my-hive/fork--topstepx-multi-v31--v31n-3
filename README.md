# TopstepX multi-asset v3.1

Causal CME 1-minute OHLCV research task. Agents see development data only. Sealed validator sees validation data. Owner alone may inspect validation reports and final reused historical audit.

## Local development

```bash
python3 /opt/v31-eval/eval/sim.py \
  --data /data/dev --symbols MES MGC \
  --strategy "$PWD/strategy.py" --output report.json --ledger fills.jsonl
```

Report always runs 200 shared-session side-randomized null seeds. `stressed.eligibility` must pass before `stressed.score` can be nonzero:

- positive stressed total PnL
- three positive stressed calendar years
- entry-time diversity
- side-null `p <= 0.05`

## Sealed validation

Freeze source before submit. No validation result reaches research agent.

```bash
python3 /usr/local/bin/v31-validate --strategy strategy.py --symbols MNQ,MCL
```

Receipt means queued/finished execution only. It does not mean candidate passed.

Read `program.md` before research.
