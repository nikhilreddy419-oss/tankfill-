"""Calculator Controller Blueprint Module.

Handles computation requests, user input processing, validation,
results rendering, JSON API endpoints, and CSV export.
"""

import io
import csv
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    Response,
    session,
)

from utils.validators import validate_tank_inputs
from services.bisection import BisectionSolver

calculator_bp = Blueprint("calculator", __name__)

# Preset configurations for user convenience
PRESETS = {
    "residential": {
        "name": "Residential Overhead Tank (1,000 L)",
        "capacity": 1000.0,
        "current_level": 150.0,
        "target_level": 950.0,
        "inflow_rate": 25.0,
        "drain_rate": 0.0,
        "tolerance": 1e-4,
        "max_iterations": 100,
        "flow_model": "linear",
    },
    "commercial": {
        "name": "Commercial Reservoir with Drain (5,000 L)",
        "capacity": 5000.0,
        "current_level": 500.0,
        "target_level": 4800.0,
        "inflow_rate": 60.0,
        "drain_rate": 10.0,
        "tolerance": 1e-4,
        "max_iterations": 100,
        "flow_model": "linear",
    },
    "hydrodynamic": {
        "name": "Industrial Tank with Head Loss (2,500 L)",
        "capacity": 2500.0,
        "current_level": 200.0,
        "target_level": 2200.0,
        "inflow_rate": 45.0,
        "drain_rate": 0.0,
        "tolerance": 1e-5,
        "max_iterations": 120,
        "flow_model": "hydrodynamic",
    },
    "lab_test": {
        "name": "Laboratory Precision Bench (100 L)",
        "capacity": 100.0,
        "current_level": 10.0,
        "target_level": 90.0,
        "inflow_rate": 8.0,
        "drain_rate": 1.5,
        "tolerance": 1e-6,
        "max_iterations": 150,
        "flow_model": "linear",
    },
}


@calculator_bp.route("/calculator", methods=["GET", "POST"])
def calculator():
    """Render the calculator interface or process standard form submission."""
    if request.method == "POST":
        form_data = request.form.to_dict()
        is_valid, validated_data, errors = validate_tank_inputs(form_data)

        if not is_valid:
            return render_template(
                "calculator.html",
                title="Calculator – TankFill",
                form_data=form_data,
                errors=errors,
                presets=PRESETS,
            ), 400

        try:
            solver = BisectionSolver(
                capacity=validated_data["capacity"],
                current_level=validated_data["current_level"],
                target_level=validated_data["target_level"],
                inflow_rate=validated_data["inflow_rate"],
                drain_rate=validated_data.get("drain_rate", 0.0),
                tolerance=validated_data.get("tolerance", 1e-4),
                max_iterations=validated_data.get("max_iterations", 100),
                bracket_a=validated_data.get("bracket_a"),
                bracket_b=validated_data.get("bracket_b"),
                flow_model=validated_data.get("flow_model", "linear"),
            )
            result = solver.solve()
            return render_template(
                "result.html",
                title="Calculation Results – TankFill",
                result=result,
            )
        except Exception as exc:
            errors["general"] = str(exc)
            return render_template(
                "calculator.html",
                title="Calculator – TankFill",
                form_data=form_data,
                errors=errors,
                presets=PRESETS,
            ), 400

    # GET request - populate default form data
    default_data = PRESETS["residential"]
    return render_template(
        "calculator.html",
        title="Calculator – TankFill",
        form_data=default_data,
        errors={},
        presets=PRESETS,
    )


@calculator_bp.route("/api/calculate", methods=["POST"])
def api_calculate():
    """JSON API endpoint for asynchronous AJAX calculations.

    Accepts JSON or form-encoded POST payload and returns JSON results
    with full iteration table, Chart.js datasets, and solution metrics.
    """
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form.to_dict()

    is_valid, validated_data, errors = validate_tank_inputs(data)

    if not is_valid:
        return jsonify({
            "success": False,
            "errors": errors,
            "message": "Input validation failed. Please check the marked fields.",
        }), 400

    try:
        solver = BisectionSolver(
            capacity=validated_data["capacity"],
            current_level=validated_data["current_level"],
            target_level=validated_data["target_level"],
            inflow_rate=validated_data["inflow_rate"],
            drain_rate=validated_data.get("drain_rate", 0.0),
            tolerance=validated_data.get("tolerance", 1e-4),
            max_iterations=validated_data.get("max_iterations", 100),
            bracket_a=validated_data.get("bracket_a"),
            bracket_b=validated_data.get("bracket_b"),
            flow_model=validated_data.get("flow_model", "linear"),
        )
        result = solver.solve()
        return jsonify({
            "success": True,
            "result": result,
        }), 200

    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc),
            "errors": {"general": str(exc)},
        }), 400


@calculator_bp.route("/result")
def result_view():
    """Direct route for results view.

    Runs default baseline simulation to ensure page renders smoothly
    if user navigates directly without submitting the form first.
    """
    default_preset = PRESETS["residential"]
    solver = BisectionSolver(
        capacity=default_preset["capacity"],
        current_level=default_preset["current_level"],
        target_level=default_preset["target_level"],
        inflow_rate=default_preset["inflow_rate"],
        drain_rate=default_preset["drain_rate"],
        tolerance=default_preset["tolerance"],
        max_iterations=default_preset["max_iterations"],
        flow_model=default_preset["flow_model"],
    )
    result = solver.solve()
    return render_template(
        "result.html",
        title="Sample Results – TankFill",
        result=result,
        is_sample=True,
    )


@calculator_bp.route("/export/csv", methods=["POST"])
def export_csv():
    """Export the Bisection iteration table as a downloadable CSV file."""
    form_data = request.form.to_dict()
    is_valid, validated_data, _ = validate_tank_inputs(form_data)

    if not is_valid:
        return redirect(url_for("calculator.calculator"))

    try:
        solver = BisectionSolver(
            capacity=validated_data["capacity"],
            current_level=validated_data["current_level"],
            target_level=validated_data["target_level"],
            inflow_rate=validated_data["inflow_rate"],
            drain_rate=validated_data.get("drain_rate", 0.0),
            tolerance=validated_data.get("tolerance", 1e-4),
            max_iterations=validated_data.get("max_iterations", 100),
            bracket_a=validated_data.get("bracket_a"),
            bracket_b=validated_data.get("bracket_b"),
            flow_model=validated_data.get("flow_model", "linear"),
        )
        result = solver.solve()

        output = io.StringIO()
        writer = csv.writer(output)

        # Metadata Header
        writer.writerow(["# TankFill – Water Tank Filling Time Calculator"])
        writer.writerow(["# Computational Mathematics Laboratory Report"])
        writer.writerow(["# Tank Capacity (L)", validated_data["capacity"]])
        writer.writerow(["# Initial Level (L)", validated_data["current_level"]])
        writer.writerow(["# Target Level (L)", validated_data["target_level"]])
        writer.writerow(["# Inflow Rate (L/min)", validated_data["inflow_rate"]])
        writer.writerow(["# Drain Rate (L/min)", validated_data.get("drain_rate", 0.0)])
        writer.writerow(["# Convergence Tolerance", validated_data.get("tolerance", 1e-4)])
        writer.writerow(["# Root Filling Time (mins)", result["root_time"]])
        writer.writerow(["# Formatted Duration", result["duration"]["human_readable"]])
        writer.writerow(["# Total Iterations", result["total_iterations"]])
        writer.writerow(["# Final Absolute Error", result["final_error"]])
        writer.writerow([])

        # Table Column Headers
        writer.writerow([
            "Iteration (k)",
            "Lower Bound a_k",
            "Upper Bound b_k",
            "Midpoint c_k",
            "f(a_k)",
            "f(b_k)",
            "f(c_k)",
            "Absolute Error |b-a|/2",
            "Theoretical Bound",
            "Sign Test",
            "Update Action",
        ])

        for row in result["iterations"]:
            writer.writerow([
                row["iteration"],
                f"{row['a']:.8f}",
                f"{row['b']:.8f}",
                f"{row['c']:.8f}",
                f"{row['fa']:.8f}",
                f"{row['fb']:.8f}",
                f"{row['fc']:.8f}",
                f"{row['error']:.8e}",
                f"{row['theoretical_bound']:.8e}",
                row["sign_test"],
                row["action"],
            ])

        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=tankfill_bisection_report.csv"},
        )
    except Exception as exc:
        return redirect(url_for("calculator.calculator"))
