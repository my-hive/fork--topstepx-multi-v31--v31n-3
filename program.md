# TopstepX 50K multi-asset research v3.1

## Mission
Find causal 1-minute CME futures strategies that can meet TopstepX 50K combine constraints. Development evidence is not proof. Optimize economic edge first; combine pass rate ranks only eligible strategies.

## Account model
One shared $50,000 account across all instruments. Target $3,000. Daily loss limit $1,000: evaluator flattens. EOD trailing maximum loss $2,000, locked at $50,000. At least two trading days, best day under 50% profit. Flat 15:10 CT. Integer positions only. Aggregate exposure at most 5 standard equivalents. Strategy risk at entry at most $300 per trade.

## Universe
Use only cache-present CME roots: ES MES NQ MNQ YM MYM RTY M2K NKD; CL MCL QM NG MNG QG RB HO; GC MGC SI SIL HG MHG PL; 6E M6E 6B M6B 6A M6A 6C 6J 6S 6N 6M; MBT MET; ZB UB ZT ZF ZN TN; ZC ZS ZW ZL HE LE. History begins at actual product availability. No synthetic pre-inception history. Different contract sizes of one underlying are not independent evidence.

## Data and causality
All stages use Databento 1-minute OHLCV, UTC bar-start timestamps. Completed-bar features become available after close; signal fills next minute open. Development only: `/data/dev/<SYMBOL>.parquet`, 2010-06 through 2023-12. Sealed validation: 2024-01 through 2025-08, never mounted for agents. Historical audit: 2025-09 through 2026-08, owner-only and reused data, not fresh OOS. No raw data, old task history, host memory, hidden-period probing, services, or live trading access.

## Strategy contract
`signals(panel)` receives `{symbol: pandas.DataFrame}` and returns aligned integer target arrays. Omitted symbols are flat. No future shifts, centered windows, full-sample normalization, leakage through cross-market alignment, fractional sleeves, or Kelly sizing selected from backtest wins. Trailing windows must be lagged.

## Evaluation and eligibility
Evaluator uses stressed costs: 2 ticks slippage plus 1.5x estimated commission. Inspect yearly PnL, per-market PnL, turnover, fills, and ledger. New entries from 08:30–09:30 CT must not exceed 40%. Do not add correlated or losing sleeves only to raise account variance.

A candidate is **eligible only when every gate passes**:

1. Total stressed development PnL is positive.
2. At least three calendar years have positive stressed PnL.
3. Entry-time diversity passes.
4. Its account-pass score beats 200 frozen whole-session shared-side randomizations at `p <= 0.05`.

Ineligible candidate score is zero. Eligible candidates rank by mean worst three yearly rolling-30-session pass rates. Report raw score and each gate; never claim edge from raw score alone. A randomized-side null preserves exact entries, sizes, and timings; it tests directional information only.

## Experiment budget
At most 30 recorded development experiments per agent. Every change, crash, screen, or variant counts. No unrecorded grid/random sweeps. Append hypothesis, source SHA256, symbols, raw score, eligibility gates, economics, mechanism, and variants to `experiments.jsonl`. Commit only `strategy.py`, `experiments.jsonl`, and mechanism notes. Push then submit self-reported development result. Do not adopt another candidate without independent reproduction. Do not create `.hive/research-complete` before 30 entries unless a real environmental blocker is recorded in feed.

## Sealed validation
Freeze up to three distinct source SHA256 finalists using **eligible development evidence** before validation. Submit with:

```bash
python3 /usr/local/bin/v31-validate --strategy strategy.py --symbols MNQ,MCL
```

Receipt exposes status, SHA, quota only. It exposes no metrics, errors, traces, or timing signal. Failed accepted reservation consumes quota. Do not modify candidates or continue research based on service behavior. Validator independently reruns 200 null seeds and records validation eligibility gates for owner review only.

After budget exhaustion: write mechanism notes, submit frozen finalists only, post completion, create `.hive/research-complete`, exit.
