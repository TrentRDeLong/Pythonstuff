"""
pa_setup_checker.py

Simple Price-Action / ICT-style Setup Validator.
User-driven: you input your market read (structure, patterns, ICT levels, entry, stop/ATR, time).
Script returns: validity, recommended stop (if not provided), suggested TPs (R-multiples and level-aware), and position sizing hint.

Author: ChatGPT (example starter). Edit comments and rules to match your trading ruleset.
"""

from datetime import datetime, time
import math

# ---------- Helper functions ----------


def parse_time_str(tstr):
    """Parse "HH:MM" into a datetime.time object. Returns None if invalid."""
    try:
        h, m = map(int, tstr.strip().split(":"))
        return time(hour=h, minute=m)
    except Exception:
        return None


def time_in_windows(t, windows):
    """
    t: datetime.time
    windows: list of tuples (start_time, end_time) both datetime.time
    Handles windows that cross midnight (end < start).
    """
    for s, e in windows:
        if s <= e:
            if s <= t <= e:
                return True
        else:
            # window wraps midnight
            if t >= s or t <= e:
                return True
    return False


def parse_windows_input(win_str):
    """
    Accepts input like "09:30-11:30,13:00-15:00" and returns list of (start_time, end_time).
    """
    windows = []
    parts = [p.strip() for p in win_str.split(",") if p.strip()]
    for p in parts:
        if "-" not in p:
            continue
        a, b = p.split("-")
        ta = parse_time_str(a)
        tb = parse_time_str(b)
        if ta and tb:
            windows.append((ta, tb))
    return windows


def suggest_stop_from_atr(entry, direction, atr, atr_multiplier=1.5):
    """Simple stop suggestion using ATR multiplier (price units)."""
    dist = atr * atr_multiplier
    if direction == "long":
        stop = round(entry - dist, 5)
    else:
        stop = round(entry + dist, 5)
    return stop, round(dist, 5)


def r_multiples(entry, stop, direction, r_list=(1.0, 1.5, 2.0, 3.0)):
    """Return TP prices for given R multiples."""
    stop_dist = abs(entry - stop)
    tps = []
    for r in r_list:
        if direction == "long":
            tp = round(entry + stop_dist * r, 5)
        else:
            tp = round(entry - stop_dist * r, 5)
        tps.append((r, tp))
    return tps

# ---------- Main logic ----------


def get_input(prompt, valid=None, default=None):
    """
    Simplified input with validation.
    If valid is set to a list/tuple, input must be one of those (case-insensitive).
    """
    while True:
        s = input(prompt).strip()
        if s == "" and default is not None:
            return default
        if valid:
            if s.lower() in [v.lower() for v in valid]:
                return s.lower()
            else:
                print("  ➜ invalid option; expected one of:", valid)
        else:
            return s


def main():
    print("\n=== Price-Action / ICT Setup Checker ===\n")
    print("This tool asks you about your analysis and returns a simple validity check,")
    print("recommended stop (if not provided), TP suggestions, and a position-sizing hint.\n")
    print("All times are assumed in your local timezone. Input 'q' at any prompt to quit.\n")

    # --- user preferences / trading window ---
    win_input = input(
        "Enter your allowed trading windows (e.g. 09:30-11:30,13:00-15:00) or leave blank to skip: ").strip()
    trading_windows = parse_windows_input(win_input) if win_input else []

    # --- basic trade metadata ---
    direction = get_input(
        "Intended trade direction? (long / short): ", valid=("long", "short"))
    structure_1h = get_input("Current 1-hour short-term structure? (higher / lower / unclear): ",
                             valid=("higher", "lower", "unclear"))
    market_env = get_input("Market environment? (expansion / consolidation / reversal / retracement): ",
                           valid=("expansion", "consolidation", "reversal", "retracement"))
    # patterns (user types comma separated known patterns they see)
    patterns_raw = input(
        "Patterns present? (comma-separated, e.g. engulfing,breakout,inside) or 'none': ").strip()
    if patterns_raw.lower() == "q":
        return
    patterns = [p.strip().lower()
                for p in patterns_raw.split(",") if p.strip()]
    if not patterns:
        patterns = ["none"]

    # ICT level inputs
    fvg = get_input(
        "Is a Fair Value Gap (FVG) near the entry? (y/n): ", valid=("y", "n"))
    ob = get_input(
        "Is there an Order Block relevant to this setup? (y/n): ", valid=("y", "n"))
    liq = get_input(
        "Is price near a liquidity pool (highs/lows of larger-degree) ? (y/n): ", valid=("y", "n"))

    # time of setup check
    time_setup_str = input(
        "Time of setup (HH:MM) — enter now in local time, or leave blank to skip: ").strip()
    time_ok = True
    if time_setup_str:
        tsetup = parse_time_str(time_setup_str)
        if not tsetup:
            print("  ➜ invalid time format; ignoring time check.")
            tsetup = None
            time_ok = True
        else:
            if trading_windows:
                time_ok = time_in_windows(tsetup, trading_windows)
            else:
                time_ok = True

    # entry / stop / account
    entry_s = input(
        "Entry price (e.g. 1.23456) — leave blank if you only want logic check: ").strip()
    entry = None
    try:
        if entry_s != "":
            entry = float(entry_s)
    except:
        entry = None

    stop_s = input("Stop price (leave blank to auto-calc from ATR): ").strip()
    stop_price = None
    try:
        if stop_s != "":
            stop_price = float(stop_s)
    except:
        stop_price = None

    atr = None
    if entry is not None and stop_price is None:
        # ask for ATR to calculate stop
        atr_s = input(
            "Enter ATR (price units) to auto-calc stop (e.g. 0.0020) or leave blank to skip: ").strip()
        try:
            if atr_s != "":
                atr = float(atr_s)
        except:
            atr = None

    acct_s = input(
        "Account size (optional, e.g. 10000) or leave blank to skip position sizing: ").strip()
    risk_pct_s = input(
        "Risk percent per trade (e.g. 1 for 1%) — leave blank to skip sizing calc: ").strip()

    # --- Simple Rules Engine ---
    reasons = []
    score = 0  # higher score -> more valid

    # 1) structure vs direction
    if direction == "long":
        if structure_1h == "higher":
            score += 2
        elif structure_1h == "unclear":
            score += 0
            reasons.append(
                "1H structure unclear — prefer structure in trade direction.")
        else:
            reasons.append(
                "1H structure is LOWER while you plan a LONG. That's a structural mismatch.")
    else:  # short
        if structure_1h == "lower":
            score += 2
        elif structure_1h == "unclear":
            score += 0
            reasons.append(
                "1H structure unclear — prefer structure in trade direction.")
        else:
            reasons.append(
                "1H structure is HIGHER while you plan a SHORT. That's a structural mismatch.")

    # 2) market environment checks
    if market_env == "expansion":
        score += 1
    elif market_env == "consolidation":
        # breakouts could be valid but in consolidation it's riskier
        if "breakout" in patterns:
            reasons.append(
                "Market consolidation — breakouts can be false; consider waiting for clear momentum.")
            score -= 1
    elif market_env == "reversal":
        # reversal + engulfing/order block could be strong
        if "engulfing" in patterns or ob == "y":
            score += 2
    elif market_env == "retracement":
        # retracement into an ICT level + structure with trend favored -> good
        if fvg == "y" or ob == "y" or liq == "y":
            score += 1

    # 3) pattern/ICT confirmation
    ict_confirm = (fvg == "y") or (ob == "y") or (liq == "y")
    pattern_confirm = any(p in ("engulfing", "breakout",
                          "pinbar", "inside") for p in patterns)
    if ict_confirm and pattern_confirm:
        score += 3
    elif pattern_confirm:
        score += 1
        reasons.append("Pattern present but no ICT-level confirmation.")
    elif ict_confirm:
        score += 1
        reasons.append(
            "ICT level(s) present but no classic pattern; may need further price reaction.")
    else:
        reasons.append(
            "No patterns or ICT levels flagged — consider waiting for clearer confluence.")

    # 4) time-of-day check
    if trading_windows and time_setup_str:
        if not time_ok:
            reasons.append(
                "Setup time is outside your allowed trading windows — recommended to wait.")
        else:
            score += 1

    # 5) final pass/fail logic
    should_trade = True
    # basic rule: require structure alignment and at least one confirmation (pattern or ICT)
    if ("mismatch" in " ".join(reasons).lower()) or (structure_1h == "unclear" and not (pattern_confirm and ict_confirm)) or (not (pattern_confirm or ict_confirm)):
        should_trade = False

    # --- stop & TP calculation ---
    suggested_stop = stop_price
    stop_distance = None
    if entry is not None:
        if stop_price is None:
            if atr is not None:
                suggested_stop, stop_distance = suggest_stop_from_atr(
                    entry, direction, atr, atr_multiplier=1.5)
                reasons.append(
                    f"Stop auto-calculated from ATR (multiplier 1.5): distance {stop_distance}")
            else:
                reasons.append(
                    "No stop provided and no ATR — cannot auto-calc stop.")
        else:
            stop_distance = round(abs(entry - stop_price), 5)
    else:
        reasons.append(
            "No entry price provided — TP/stop calculations skipped.")

    tps = []
    if entry is not None and (suggested_stop or stop_price):
        used_stop = suggested_stop if suggested_stop is not None else stop_price
        tps = r_multiples(entry, used_stop, direction, r_list=(1.0, 1.5, 2.0))

    # --- position sizing hint ---
    pos_hint = None
    try:
        if acct_s and risk_pct_s and entry is not None and (stop_price is not None or suggested_stop is not None):
            acct = float(acct_s)
            risk_pct = float(risk_pct_s)
            risk_amount = acct * (risk_pct / 100.0)
            # stop distance in price units:
            used_stop = suggested_stop if suggested_stop is not None else stop_price
            if used_stop is None:
                pos_hint = "No stop price available to compute position size."
            else:
                stop_dist_price = abs(entry - used_stop)
                if stop_dist_price == 0:
                    pos_hint = "Stop distance is zero — cannot compute size."
                else:
                    # position size = risk_amount / (stop_dist_price)
                    # This returns units of 'account currency per price unit' (e.g., for forex you'd then convert to lots).
                    qty = risk_amount / stop_dist_price
                    pos_hint = f"Risk ${risk_amount:.2f}. Suggested position exposure (in price-units) = {qty:.2f}."
        elif acct_s or risk_pct_s:
            pos_hint = "Provide both account size and risk% to get a position-sizing hint."
    except Exception as e:
        pos_hint = f"Position sizing error: {e}"

    # ---------- Output ----------
    print("\n\n=== Setup Evaluation ===\n")
    print(
        f"Direction: {direction.upper()} | 1H Structure: {structure_1h} | Market env: {market_env}")
    print("Patterns:", ", ".join(patterns))
    print(f"ICT: FVG={fvg}, OrderBlock={ob}, LiquidityNear={liq}")
    if trading_windows:
        print("Your trading windows:", win_input)
        if time_setup_str:
            print(
                f"Time of setup: {time_setup_str} -> {'INSIDE' if time_ok else 'OUTSIDE'} allowed windows")
    print()

    # Validity summary
    if should_trade and score >= 3:
        print("✅ Setup looks VALID based on your inputs.")
    else:
        print("⚠️ Setup NOT RECOMMENDED based on current inputs.")
    print(f"Validity score (internal): {score}\n")

    if reasons:
        print("Notes / reasons to consider:")
        for r in reasons:
            print("  -", r)
    print()

    # stop & TP
    if entry is not None:
        print(f"Entry: {entry}")
        if suggested_stop is not None:
            print(
                f"Suggested Stop: {suggested_stop} (distance {stop_distance})")
        elif stop_price is not None:
            print(f"Provided Stop: {stop_price} (distance {stop_distance})")
        else:
            print("Stop: NONE provided or calculated.")
        if tps:
            print("\nSuggested Take-Profits (R multiples):")
            for r, tp in tps:
                print(f"  {r}R -> {tp}")
    else:
        print("No entry price — TP/stop suggestions skipped.")

    if pos_hint:
        print("\nPosition sizing hint:")
        print(" ", pos_hint)

    print("\n=== End ===\n")
    print("Disclaimer: This script only organizes your inputs and applies simple rules.")
    print("It does NOT replace your edge, nor is it financial advice. Adapt rules to match Al Brooks / ICT specifics as needed.")
    print()


if __name__ == "__main__":
    main()
