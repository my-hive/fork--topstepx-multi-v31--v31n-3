# v31n-3 mechanism notes (development only)

## Accounting facts that dominate candidate design

1. **Data gaps are expensive.** `run_days` flattens at the prior close whenever the
   next bar is not exactly +1 minute, same contract, same session, and a still-nonzero
   target re-enters at the next open. One missing minute therefore costs a full
   stressed round trip. Sparse early standard contracts (NQ/ES 2010-2012, MGC before
   2019) lose $100k+/year from churn alone, which is why apparently large segment
   drifts do not survive there. Dense recent micros (MNQ/MES 2019+) pay roughly one
   extra round trip per session.
2. **Cost floor.** Stressed round trip = 4 ticks of slippage + 3x base commission:
   MNQ x5 $21.25, NQ $27.50, ES $57.50, ZN $70.00, 6E $32.50. Unconditional segment
   drifts in rates/FX/metals ($2-25/day) sit below their cost floor; only equity
   index drift clears it.
3. **Pass-rate geometry.** Rolling 30-session attempts need +$3000 before a
   $2000 peak-to-valley breach, daily adverse $1000 lock, best day < 50% of profit.
   Synthetic calibration with `sim.attempts`: mean $100/day with $200-400 daily std
   gives 0.54-0.58; mean $25/day with $400 std gives 0.27; tiny std causes timeouts,
   huge std causes MLL failure. Real MNQ x5 RTH-long has mean $17/day, std $949,
   28% of days touch the daily loss lock, 74% of attempts end in MLL breach. Position
   size alone cannot fix a low daily Sharpe; it only moves the failure mode.

## Failed approach kept on record (leakage)

Early trend variants (`flex.py`, E07-E10) used the *same session's* final close in
the moving-average filter while entering at 17:01 CT. That is intraday leakage.
Scores up to 0.57 and total PnL up to $700k were artefacts. After lagging the filter
by one session (E11) the same family is flat to negative. This is the single most
important negative result: session-scale trend filters on this evaluator must be
lagged, and any large score from an unlagged filter is invalid.

## Surviving candidate mechanism

MNQ intraday momentum, causal:

* reference = 17:00 CT session open (known at entry),
* decision bar = 10:00 CT close, using the 09:59 CT close vs the session open,
* sign-matched 5 MNQ (0.5 NQ equivalent) filled at the 10:01 CT open,
* close-based $800 dollar stop, flat for the rest of the session once hit,
* flat from the 15:09 CT open; no overnight inventory, no 08:30-09:30 CT entries.

Development (2019-05..2023-12, stressed): total $42,377.50, positive years
2020/2021/2022 (3), yearly pass rates 0.255/0.378/0.330/0.214/0.223,
worst-three mean 0.2307, entry-time diversity pass (all entries at 10:01 CT).
2019 and 2023 are negative: the effect is not stable, so development score is not
evidence of deployable profitability. Expected OOS risk: the Nasdaq 2019-2023
intraday continuation premium need not persist in 2024-2025.

Variants screened and rejected: unconditional RTH long, overnight-only hold,
long-only follow, asymmetric short sleeve, vol-targeted sizing (zero-pass years),
12:01/11:01/09:41 entries, 14:00/15:00 exits, thresholds on overnight magnitude,
other roots (MES, M2K, NQ, ES, MGC, MCL all negative after costs).

## Frozen finalists (all three independently reproduced on the trusted evaluator, 200 nulls)

| rank | file sha256 | rule | stressed dev PnL | pos. years | worst-3 pass | null p |
|---|---|---|---|---|---|---|
| 1 | fa2f9cd96198b782839f1998bea51f6f1353b611e331c79e45fb2e13ee2538b2 | MNQ long 5 / short 5, stop $800 | +42,377.50 | 3 | 0.23067 | 0.004975 |
| 2 | 8ea10fdc0a85154fe819d013e9a56b3e5ac82eb828dbfdbefdb9d12bc69fcba9 | MNQ long 5 / short 2, stop $600 | +36,081.25 | 4 | 0.22178 | 0.004975 |
| 3 | 5e44a520479a25791c08adb3960b30665857a25fbbc099a14a846c271f28f1ea | MNQ long 8 only when 09:59 CT > 17:00 CT open, stop $600 | +55,886.00 | 4 | 0.15470 | 0.024876 |

All enter at 10:01 CT, flat from 15:09 CT, MNQ only, max exposure 0.5/0.8 standard
equivalents, 0% of entries inside 08:30-09:30 CT.

Robustness (E21-E25): stop 600/800/1000/none -> 0.197/0.231/0.204/0.204; size
3/4/5/6 -> 0.162/0.215/0.231/0.196; entry 09:56/10:01/10:06 -> 0.220/0.231/0.188;
base-cost PnL 53.3k/43.9k/65.4k; late 2022-2023 PnL +10.7k/+25.0k/+26.4k;
flat control exactly 0, sign-flipped F1 -106,269. Selection of q=5/stop=$800 is a
local optimum inside a smooth neighbourhood, so residual selection bias remains.
Ranking is development-only and does not imply sealed-validation performance.
