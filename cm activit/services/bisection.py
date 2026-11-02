"""Bisection Method Numerical Solver Module.

Implements the classical Bisection Method (Bolzano's root-finding algorithm)
to determine the precise filling time of a water tank.
Formulates the mathematical function f(t) = V(t) - V_target = 0 and tracks
every single iteration step with rigorous error analysis and convergence monitoring.
"""

import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from utils.math_helpers import (
    calculate_theoretical_iterations,
    evaluate_tank_volume,
    format_duration,
    format_number,
    generate_time_series,
    relative_error,
)


class BisectionSolver:
    """Numerical solver for water tank filling time using the Bisection Method."""

    def __init__(
        self,
        capacity: float,
        current_level: float,
        target_level: float,
        inflow_rate: float,
        drain_rate: float = 0.0,
        tolerance: float = 1e-4,
        max_iterations: int = 100,
        bracket_a: Optional[float] = None,
        bracket_b: Optional[float] = None,
        flow_model: str = "linear",
    ):
        """Initialize solver parameters.

        Args:
            capacity: Total tank capacity in Litres.
            current_level: Initial water level V0 in Litres.
            target_level: Target water level V_target in Litres.
            inflow_rate: Water inflow rate Q_in in Litres/minute.
            drain_rate: Water drain/leak rate Q_out in Litres/minute.
            tolerance: Convergence error tolerance epsilon.
            max_iterations: Upper bound on iterations.
            bracket_a: Optional user-specified lower bracket.
            bracket_b: Optional user-specified upper bracket.
            flow_model: 'linear' or 'hydrodynamic'.
        """
        self.capacity = float(capacity)
        self.current_level = float(current_level)
        self.target_level = float(target_level)
        self.inflow_rate = float(inflow_rate)
        self.drain_rate = float(drain_rate)
        self.net_flow = self.inflow_rate - self.drain_rate
        self.tolerance = float(tolerance)
        self.max_iterations = int(max_iterations)
        self.bracket_a = bracket_a
        self.bracket_b = bracket_b
        self.flow_model = flow_model.lower()

    def function_f(self, t: float) -> float:
        """Formulate the objective function: f(t) = V(t) - V_target.

        The root t* satisfies f(t*) = 0, which corresponds to the time
        when the tank reaches the target water level.

        Args:
            t: Time in minutes.

        Returns:
            f(t): Difference between current volume at time t and target volume.
        """
        v_t = evaluate_tank_volume(
            t=t,
            v0=self.current_level,
            q_in=self.inflow_rate,
            q_out=self.drain_rate,
            capacity=self.capacity,
            model=self.flow_model,
        )
        return v_t - self.target_level

    def find_initial_bracket(self) -> Tuple[float, float]:
        """Automatically find or validate an initial interval [a, b] such that f(a) * f(b) <= 0.

        According to the Intermediate Value Theorem (Bolzano's theorem),
        if f(t) is continuous on [a, b] and f(a) * f(b) < 0, there exists
        at least one root in (a, b).

        Returns:
            Tuple (a, b) representing valid brackets.

        Raises:
            ValueError: If a valid bracket cannot be determined or validated.
        """
        # Case 1: User explicitly provided both brackets
        if self.bracket_a is not None and self.bracket_b is not None:
            a = float(self.bracket_a)
            b = float(self.bracket_b)
            if b <= a:
                raise ValueError(f"Lower bracket a ({a}) must be strictly less than upper bracket b ({b}).")
            fa = self.function_f(a)
            fb = self.function_f(b)
            if fa * fb > 0:
                raise ValueError(
                    f"Intermediate Value Theorem condition failed: f(a) = {fa:.4f} and f(b) = {fb:.4f} "
                    "have the same sign! Root is not guaranteed in [a, b]. Please adjust brackets or leave empty."
                )
            return a, b

        # Case 2: Automatic bracket discovery
        # At t = 0, V(0) = current_level < target_level => f(0) < 0
        a = 0.0
        fa = self.function_f(a)

        # Baseline analytical estimate for upper bound
        if self.net_flow > 0:
            est_time = (self.target_level - self.current_level) / self.net_flow
            b = max(1.0, est_time * 1.5)
        else:
            b = 10.0

        # Expand b until f(b) >= 0 (up to a safe engineering upper limit)
        max_search_time = 100_000.0  # 100,000 minutes limit
        multiplier = 1.6
        found = False

        while b <= max_search_time:
            fb = self.function_f(b)
            if fa * fb <= 0:
                found = True
                break
            b *= multiplier

        if not found:
            raise ValueError(
                "Could not find a valid upper bracket b where f(b) >= 0 within realistic limits. "
                "The tank may be unable to reach the target level under current flow conditions."
            )

        return a, b

    def get_analytical_solution(self) -> Optional[float]:
        """Compute the exact analytical solution for linear model for validation."""
        if self.flow_model == "linear" and self.net_flow > 0:
            return (self.target_level - self.current_level) / self.net_flow
        return None

    def solve(self) -> Dict[str, Any]:
        """Execute the Bisection algorithm step by step.

        Tracks every iteration, computes midpoint, function evaluations,
        absolute error, relative error, sign condition, and interval updates.

        Returns:
            Comprehensive results dictionary with solution metadata,
            iteration history, graph data series, and LaTeX formulas.
        """
        start_time = time.perf_counter()

        # Step 1: Establish initial bracket
        a, b = self.find_initial_bracket()
        initial_a = a
        initial_b = b

        fa = self.function_f(a)
        fb = self.function_f(b)

        # Step 2: Theoretical iterations calculation
        theoretical_iters = calculate_theoretical_iterations(a, b, self.tolerance)

        # Iteration history list
        iterations: List[Dict[str, Any]] = []
        convergence_errors: List[float] = []
        convergence_labels: List[int] = []
        theoretical_errors: List[float] = []
        function_values: List[float] = []

        root: float = (a + b) / 2.0
        converged = False
        status_message = "Maximum iterations reached before convergence."

        # Analytical solution for comparison
        analytical_time = self.get_analytical_solution()

        # Step 3: Bisection Loop
        for k in range(1, self.max_iterations + 1):
            c = (a + b) / 2.0
            fc = self.function_f(c)

            # Error at iteration k: half-interval width
            error = (b - a) / 2.0
            span = b - a
            rel_err = relative_error(c, analytical_time) if analytical_time else (error / abs(c) if abs(c) > 1e-12 else error)
            theo_bound = (initial_b - initial_a) / (2.0 ** k)

            sign_product = fa * fc
            if sign_product < 0:
                sign_test_text = "f(a) · f(c) < 0"
                action_text = f"b ← c ({format_number(c, 4)})"
                next_interval = f"[{format_number(a, 4)}, {format_number(c, 4)}]"
                next_a = a
                next_b = c
                next_fa = fa
                next_fb = fc
            elif sign_product > 0:
                sign_test_text = "f(a) · f(c) > 0"
                action_text = f"a ← c ({format_number(c, 4)})"
                next_interval = f"[{format_number(c, 4)}, {format_number(b, 4)}]"
                next_a = c
                next_b = b
                next_fa = fc
                next_fb = fb
            else:
                # Exact root hit: fc == 0 or fa == 0
                sign_test_text = "f(c) = 0"
                action_text = "Exact root found"
                next_interval = f"[{format_number(c, 4)}, {format_number(c, 4)}]"
                next_a = c
                next_b = c
                next_fa = 0.0
                next_fb = 0.0

            # Store iteration record
            record = {
                "iteration": k,
                "a": a,
                "b": b,
                "c": c,
                "fa": fa,
                "fb": fb,
                "fc": fc,
                "error": error,
                "span": span,
                "relative_error": rel_err,
                "theoretical_bound": theo_bound,
                "sign_test": sign_test_text,
                "action": action_text,
                "next_interval": next_interval,
            }
            iterations.append(record)

            # Data for convergence graph
            convergence_labels.append(k)
            convergence_errors.append(error)
            theoretical_errors.append(theo_bound)
            function_values.append(abs(fc))

            # Check stopping criteria
            if error < self.tolerance or abs(fc) < self.tolerance:
                root = c
                converged = True
                status_message = f"Successfully converged in {k} iterations with error < {self.tolerance:g}."
                break

            # Update bounds for next iteration
            a = next_a
            b = next_b
            fa = next_fa
            fb = next_fb
            root = c

        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000.0

        # Final metrics
        final_error = iterations[-1]["error"] if iterations else 0.0
        final_fc = iterations[-1]["fc"] if iterations else 0.0
        final_time_mins = max(0.0, root)
        duration_info = format_duration(final_time_mins)

        # Graph series for Water Level vs Time
        graph_time_series = generate_time_series(
            filling_time=final_time_mins,
            v0=self.current_level,
            v_target=self.target_level,
            capacity=self.capacity,
            q_in=self.inflow_rate,
            q_out=self.drain_rate,
            model=self.flow_model,
        )

        # Mathematical equation formulation strings
        if self.flow_model == "linear":
            latex_formula = (
                r"f(t) = V_0 + (Q_{\text{in}} - Q_{\text{out}}) \cdot t - V_{\text{target}} = 0"
            )
            substituted_latex = (
                rf"f(t) = {self.current_level:g} + ({self.inflow_rate:g} - {self.drain_rate:g}) \cdot t - {self.target_level:g} = 0"
            )
            simplified_latex = rf"f(t) = {self.current_level:g} + {self.net_flow:g} t - {self.target_level:g} = 0"
        else:
            latex_formula = (
                r"f(t) = V_{\text{max}} - (V_{\text{max}} - V_0) e^{-\frac{Q_{\text{net}}}{V_{\text{max}}} t} - V_{\text{target}} = 0"
            )
            k_val = self.net_flow / self.capacity
            substituted_latex = (
                rf"f(t) = {self.capacity:g} - ({self.capacity:g} - {self.current_level:g}) e^{{-{k_val:.4f} t}} - {self.target_level:g} = 0"
            )
            simplified_latex = substituted_latex

        # Mathematical stopping criterion formula
        stopping_criterion_latex = (
            rf"\epsilon_k = \frac{{|b_k - a_k|}}{{2}} < {self.tolerance:g} \quad \text{{or}} \quad |f(c_k)| < {self.tolerance:g}"
        )

        return {
            "success": converged,
            "status_message": status_message,
            "root_time": final_time_mins,
            "duration": duration_info,
            "total_iterations": len(iterations),
            "theoretical_iterations": theoretical_iters,
            "final_error": final_error,
            "final_relative_error": iterations[-1]["relative_error"] if iterations else 0.0,
            "final_residual": final_fc,
            "initial_interval": {"a": initial_a, "b": initial_b},
            "tolerance": self.tolerance,
            "max_iterations": self.max_iterations,
            "execution_time_ms": round(execution_time_ms, 3),
            "iterations": iterations,
            "analytical_time": analytical_time,
            "tank_parameters": {
                "capacity": self.capacity,
                "current_level": self.current_level,
                "target_level": self.target_level,
                "inflow_rate": self.inflow_rate,
                "drain_rate": self.drain_rate,
                "net_flow": self.net_flow,
                "flow_model": self.flow_model,
                "current_pct": round((self.current_level / self.capacity) * 100.0, 1),
                "target_pct": round((self.target_level / self.capacity) * 100.0, 1),
            },
            "equations": {
                "latex_formula": latex_formula,
                "substituted_latex": substituted_latex,
                "simplified_latex": simplified_latex,
                "stopping_criterion_latex": stopping_criterion_latex,
                "bisection_midpoint_latex": r"c_k = \frac{a_k + b_k}{2}",
                "error_bound_latex": r"\text{Error}_k \le \frac{b_0 - a_0}{2^k}",
            },
            "charts": {
                "convergence": {
                    "labels": convergence_labels,
                    "errors": convergence_errors,
                    "theoretical": theoretical_errors,
                    "residuals": function_values,
                },
                "level_vs_time": graph_time_series,
            },
        }
