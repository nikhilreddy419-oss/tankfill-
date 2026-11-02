"""Input Validation Module for TankFill Calculator.

Validates all user-supplied parameters to ensure mathematical and physical
soundness before executing the Bisection root-finding algorithm.
"""

from typing import Any, Dict, Optional, Tuple


def _parse_float(value: Any, field_name: str, errors: Dict[str, str]) -> Optional[float]:
    """Helper function to safely convert an input value to a float.

    Args:
        value: The raw input value from request form or JSON.
        field_name: The name of the field for error reporting.
        errors: Error dictionary to append error messages to.

    Returns:
        float if conversion succeeds, None otherwise.
    """
    if value is None or str(value).strip() == "":
        errors[field_name] = f"{field_name.replace('_', ' ').title()} is required."
        return None
    try:
        val = float(value)
        return val
    except (ValueError, TypeError):
        errors[field_name] = f"{field_name.replace('_', ' ').title()} must be a valid numeric value."
        return None


def _parse_int(value: Any, field_name: str, default: int, errors: Dict[str, str]) -> int:
    """Helper function to safely convert an input value to an integer."""
    if value is None or str(value).strip() == "":
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        errors[field_name] = f"{field_name.replace('_', ' ').title()} must be a valid whole integer."
        return default


def validate_tank_inputs(form_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], Dict[str, str]]:
    """Validate all inputs for water tank filling simulation.

    Args:
        form_data: Dictionary containing user input values.

    Returns:
        Tuple of (is_valid: bool, validated_data: dict, errors: dict).
    """
    errors: Dict[str, str] = {}
    validated: Dict[str, Any] = {}

    # 1. Tank Capacity
    capacity = _parse_float(form_data.get("capacity"), "tank_capacity", errors)
    if capacity is not None:
        if capacity <= 0:
            errors["tank_capacity"] = "Tank capacity must be strictly greater than 0 Litres."
        elif capacity > 10_000_000:
            errors["tank_capacity"] = "Tank capacity cannot exceed 10,000,000 Litres for simulation safety."
        else:
            validated["capacity"] = capacity

    # 2. Current Water Level
    current_level = _parse_float(form_data.get("current_level"), "current_water_level", errors)
    if current_level is not None:
        if current_level < 0:
            errors["current_water_level"] = "Current water level cannot be negative."
        else:
            validated["current_level"] = current_level

    # 3. Target Water Level
    target_level = _parse_float(form_data.get("target_level"), "target_water_level", errors)
    if target_level is not None:
        if target_level <= 0:
            errors["target_water_level"] = "Target water level must be strictly positive."
        else:
            validated["target_level"] = target_level

    # Cross-field validations for levels
    if capacity is not None and current_level is not None:
        if current_level > capacity:
            errors["current_water_level"] = (
                f"Current level ({current_level:g} L) cannot exceed total tank capacity ({capacity:g} L)."
            )

    if capacity is not None and target_level is not None:
        if target_level > capacity:
            errors["target_water_level"] = (
                f"Target level ({target_level:g} L) cannot exceed total tank capacity ({capacity:g} L)."
            )

    if current_level is not None and target_level is not None:
        if target_level < current_level:
            errors["target_water_level"] = (
                f"Target level ({target_level:g} L) must be greater than current level ({current_level:g} L). "
                "TankFill is designed for filling operations."
            )
        elif target_level == current_level:
            errors["target_water_level"] = (
                "Target level is already equal to current level. Tank filling time is 0 minutes."
            )

    # 4. Inflow Rate
    inflow_rate = _parse_float(form_data.get("inflow_rate"), "water_inflow_rate", errors)
    if inflow_rate is not None:
        if inflow_rate <= 0:
            errors["water_inflow_rate"] = "Inflow rate must be strictly greater than 0 Litres/min."
        elif inflow_rate > 500_000:
            errors["water_inflow_rate"] = "Inflow rate is unrealistically high (max 500,000 L/min)."
        else:
            validated["inflow_rate"] = inflow_rate

    # 5. Outflow / Drain Rate (Optional, defaults to 0.0)
    drain_raw = form_data.get("drain_rate", "0")
    if str(drain_raw).strip() == "":
        drain_rate = 0.0
    else:
        drain_rate = _parse_float(drain_raw, "drain_rate", errors)

    if drain_rate is not None:
        if drain_rate < 0:
            errors["drain_rate"] = "Drain rate cannot be negative."
        else:
            validated["drain_rate"] = drain_rate

        # Check net flow
        if inflow_rate is not None and inflow_rate <= drain_rate:
            errors["drain_rate"] = (
                f"Drain rate ({drain_rate:g} L/min) is greater than or equal to inflow rate ({inflow_rate:g} L/min). "
                "Net flow is non-positive; the tank will never reach the target level."
            )

    # 6. Tolerance
    tol_raw = form_data.get("tolerance", "1e-4")
    if str(tol_raw).strip() == "":
        tol = 1e-4
    else:
        tol = _parse_float(tol_raw, "tolerance", errors)

    if tol is not None:
        if tol <= 0 or tol > 0.1:
            errors["tolerance"] = "Tolerance must be between 1e-8 and 0.1 (recommended: 0.0001)."
        else:
            validated["tolerance"] = tol

    # 7. Max Iterations
    max_iter = _parse_int(form_data.get("max_iterations"), "max_iterations", 100, errors)
    if max_iter < 5 or max_iter > 500:
        errors["max_iterations"] = "Max iterations must be between 5 and 500."
    else:
        validated["max_iterations"] = max_iter

    # 8. Flow Model ('linear' or 'hydrodynamic')
    flow_model = str(form_data.get("flow_model", "linear")).strip().lower()
    if flow_model not in ("linear", "hydrodynamic"):
        flow_model = "linear"
    validated["flow_model"] = flow_model

    # 9. Custom Bracket (Optional)
    a_raw = form_data.get("bracket_a")
    b_raw = form_data.get("bracket_b")
    if a_raw is not None and str(a_raw).strip() != "":
        bracket_a = _parse_float(a_raw, "bracket_a", errors)
        if bracket_a is not None:
            if bracket_a < 0:
                errors["bracket_a"] = "Bracket lower bound 'a' cannot be negative time."
            validated["bracket_a"] = bracket_a

    if b_raw is not None and str(b_raw).strip() != "":
        bracket_b = _parse_float(b_raw, "bracket_b", errors)
        if bracket_b is not None:
            if "bracket_a" in validated and bracket_b <= validated["bracket_a"]:
                errors["bracket_b"] = "Bracket upper bound 'b' must be strictly greater than 'a'."
            validated["bracket_b"] = bracket_b

    is_valid = len(errors) == 0
    return is_valid, validated, errors
