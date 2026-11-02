"""Mathematical Helper Functions Module.

Provides mathematical formulas, theoretical bounds calculation,
engineering number formatting, and time-series generation for graphs.
"""

import math
from typing import Any, Dict, List, Tuple


def calculate_theoretical_iterations(a: float, b: float, tol: float) -> int:
    """Calculate theoretical minimum iterations required for Bisection convergence.

    Based on the error bound: (b - a) / (2^n) <= tol
    Rearranging: n >= (ln(b - a) - ln(tol)) / ln(2)

    Args:
        a: Initial lower bound bracket.
        b: Initial upper bound bracket.
        tol: Desired error tolerance.

    Returns:
        Minimum theoretical iterations n (rounded up).
    """
    if b <= a or tol <= 0:
        return 0
    span = b - a
    if span <= tol:
        return 0
    try:
        n = math.ceil((math.log(span) - math.log(tol)) / math.log(2.0))
        return max(1, n)
    except (ValueError, ZeroDivisionError):
        return 0


def format_duration(minutes: float) -> Dict[str, Any]:
    """Format duration in minutes into hours, minutes, and seconds breakdown.

    Args:
        minutes: Total time in decimal minutes.

    Returns:
        Dictionary with decimal minutes, total seconds, and formatted string.
    """
    total_seconds = max(0.0, minutes * 60.0)
    hours = int(total_seconds // 3600)
    rem_seconds = total_seconds % 3600
    mins = int(rem_seconds // 60)
    secs = rem_seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours} hr{'s' if hours != 1 else ''}")
    if mins > 0 or hours > 0:
        parts.append(f"{mins} min{'s' if mins != 1 else ''}")
    parts.append(f"{secs:.2f} sec{'s' if secs != 1 else ''}")

    human_readable = " ".join(parts)

    return {
        "minutes_decimal": round(minutes, 6),
        "total_seconds": round(total_seconds, 3),
        "hours": hours,
        "minutes": mins,
        "seconds": round(secs, 2),
        "human_readable": human_readable,
    }


def format_number(val: float, precision: int = 6) -> str:
    """Format floating point numbers cleanly for engineering reports.

    Uses scientific notation if absolute value < 0.001 (and not 0),
    otherwise rounds to specified precision without trailing zeros.
    """
    if val is None:
        return "N/A"
    if val == 0:
        return "0"
    abs_val = abs(val)
    if abs_val < 1e-4 or abs_val >= 1e7:
        return f"{val:.4e}"
    rounded = round(val, precision)
    # Strip unnecessary trailing zeros after decimal
    text = f"{rounded:.{precision}f}".rstrip("0").rstrip(".")
    return text if text != "" else "0"


def relative_error(approx: float, true_val: float) -> float:
    """Calculate relative error: |approx - true_val| / |true_val|."""
    if abs(true_val) < 1e-12:
        return abs(approx - true_val)
    return abs(approx - true_val) / abs(true_val)


def evaluate_tank_volume(
    t: float,
    v0: float,
    q_in: float,
    q_out: float = 0.0,
    capacity: float = 1000.0,
    model: str = "linear",
) -> float:
    """Compute tank water volume V(t) at time t.

    Models:
      - 'linear': Ideal net inflow: V(t) = V0 + (q_in - q_out) * t
      - 'hydrodynamic': Dynamic backpressure head loss:
          Pump effective delivery decreases as water head increases:
          V(t) = V_max - (V_max - V0) * exp(- (q_in - q_out) * t / V_max)

    Args:
        t: Time in minutes (t >= 0).
        v0: Initial volume in Litres.
        q_in: Inflow rate (L/min).
        q_out: Drain rate (L/min).
        capacity: Maximum tank capacity (L).
        model: 'linear' or 'hydrodynamic'.

    Returns:
        Current volume V(t) clamped between 0 and capacity.
    """
    if t <= 0:
        return min(capacity, max(0.0, v0))

    net_flow = q_in - q_out

    if model == "hydrodynamic":
        # Dynamic differential equation solution: dV/dt = net_flow * (1 - 0.4 * V / capacity)
        # Yields exponential saturation curve:
        k = max(1e-5, net_flow / capacity)
        v_eff = capacity - (capacity - v0) * math.exp(-k * t)
        return min(capacity, max(0.0, v_eff))
    else:
        # Standard uniform filling
        v_t = v0 + net_flow * t
        return min(capacity, max(0.0, v_t))


def generate_time_series(
    filling_time: float,
    v0: float,
    v_target: float,
    capacity: float,
    q_in: float,
    q_out: float = 0.0,
    model: str = "linear",
    num_points: int = 50,
) -> Dict[str, List[Any]]:
    """Generate time vs. water level curve data for Chart.js.

    Extends slightly beyond target time (to 115%) to give context.

    Returns:
        Dict with 'labels' (time in mins), 'levels' (volume in L), and 'percentages' (%).
    """
    # Safeguard against zero or negative filling time
    t_max = max(1.0, filling_time * 1.15)
    step = t_max / max(10, num_points - 1)

    labels = []
    levels = []
    percentages = []

    for i in range(num_points):
        t = round(i * step, 2)
        v = evaluate_tank_volume(t, v0, q_in, q_out, capacity, model)
        pct = round((v / capacity) * 100.0, 2) if capacity > 0 else 0.0

        labels.append(t)
        levels.append(round(v, 2))
        percentages.append(pct)

    return {
        "labels": labels,
        "levels": levels,
        "percentages": percentages,
        "target_level": v_target,
        "capacity": capacity,
        "initial_level": v0,
    }
