"""MNQ intraday momentum, causal.

Hypothesis: CME equity-index intraday momentum (Gao-Han-Li-Zhou 2018; Baltussen
et al. 2021) -- the move from the 17:00 CT session reopen to just before 10:00 CT
predicts the remaining regular-session direction. Position is chosen at 10:00 CT
using only closes at or before 09:59 CT, fills at the 10:01 CT open (outside the
08:30-09:30 CT entry window), and is held to the 15:09 CT close unless a
close-based dollar stop fires first. One MNQ position, integer size, no leverage
beyond 0.5 standard equivalents.
"""
import numpy as np

QTY = 8               # MNQ contracts = 0.5 NQ equivalents
STOP = 600.0          # dollars, close-based, same session
ENTRY = 86400 + 36060  # 10:01 CT in session-relative seconds (17:00 CT = 61200)
EXIT = 86400 + 54540   # 15:09 CT bar close
SIGNAL_END = 86400 + 36000  # reference close strictly before 10:00 CT
POINT_VALUE = 2.0


def signals(panel):
    result = {}
    for symbol, df in panel.items():
        out = np.zeros(len(df), dtype=np.int64)
        if symbol != 'MNQ':
            result[symbol] = out
            continue
        sec = df.ct_sec.to_numpy().astype(np.int64)
        # Session-relative clock: 17:00 CT -> 61200, after midnight -> +86400.
        t = np.where(sec >= 61200, sec, sec + 86400)
        session = df.session.to_numpy()
        o = df.open.to_numpy()
        c = df.close.to_numpy()
        n = len(df)
        starts = np.flatnonzero(np.r_[True, session[1:] != session[:-1]])
        ends = np.r_[starts[1:], n]
        for st, en in zip(starts, ends):
            j = st + np.searchsorted(t[st:en], ENTRY)
            # Decisions use only bars < j, so a truncated session must still
            # produce the same target on bar j-1 as the full panel does.
            if j - 2 < st or j - 1 >= en:
                continue
            if j == en and t[en - 1] != ENTRY - 60:
                continue  # panel ends before the 10:00 CT decision bar
            reference = o[st]          # 17:00 CT session open, already known
            base = c[j - 2]            # last close at or before 09:59 CT
            if base == reference:
                continue
            qty = QTY if base > reference else 0
            if qty == 0:
                continue
            if j == en:
                out[j - 1] = qty       # decision bar present, entry bar truncated
                continue
            if qty == 0:
                continue
            e = st + np.searchsorted(t[st:en], EXIT)
            out[j - 1:en] = qty        # target at bar i fills at open of bar i+1
            if e < en:
                out[e - 1:en] = 0      # flat from the 15:09 CT open
            if j >= en:
                continue
            basis = o[j]
            for i in range(j, min(e, en) - 1):
                if qty * (c[i] - basis) * POINT_VALUE <= -STOP:
                    out[i:en] = 0      # stop on close i, flat from open i+1
                    break
        result[symbol] = out
    return result
