"""Automated Test Suite for TankFill Application.

Tests:
1. Bisection solver accuracy & mathematical convergence
2. Theoretical iteration bounds
3. Input validation logic
4. Flask Blueprints and routes (HTTP 200, 400, 404)
5. JSON API calculation endpoint
"""

import unittest
from app import create_app
from config import TestingConfig
from services.bisection import BisectionSolver
from utils.validators import validate_tank_inputs
from utils.math_helpers import calculate_theoretical_iterations, format_duration


class TestBisectionSolver(unittest.TestCase):
    """Test mathematical engine and numerical convergence."""

    def test_linear_filling_convergence(self):
        """Test Bisection on ideal linear tank filling."""
        # 1000L tank, 150L current, 950L target, 25 L/min inflow, 0 drain
        # Analytical root: (950 - 150) / 25 = 32.0 minutes
        solver = BisectionSolver(
            capacity=1000.0,
            current_level=150.0,
            target_level=950.0,
            inflow_rate=25.0,
            drain_rate=0.0,
            tolerance=1e-4,
            max_iterations=100,
            flow_model="linear",
        )
        result = solver.solve()

        self.assertTrue(result["success"])
        self.assertAlmostEqual(result["root_time"], 32.0, places=3)
        self.assertLess(result["final_error"], 1e-4)
        self.assertGreater(result["total_iterations"], 0)
        self.assertGreater(len(result["iterations"]), 0)

    def test_filling_with_drain(self):
        """Test Bisection when net inflow is reduced by bottom drain valve."""
        # Net flow = 50 - 10 = 40 L/min. Target - Current = 5000 - 1000 = 4000L.
        # Analytical root: 4000 / 40 = 100.0 minutes
        solver = BisectionSolver(
            capacity=6000.0,
            current_level=1000.0,
            target_level=5000.0,
            inflow_rate=50.0,
            drain_rate=10.0,
            tolerance=1e-5,
            flow_model="linear",
        )
        result = solver.solve()
        self.assertTrue(result["success"])
        self.assertAlmostEqual(result["root_time"], 100.0, places=3)

    def test_hydrodynamic_model(self):
        """Test nonlinear exponential saturation model."""
        solver = BisectionSolver(
            capacity=2000.0,
            current_level=200.0,
            target_level=1500.0,
            inflow_rate=30.0,
            drain_rate=0.0,
            tolerance=1e-4,
            flow_model="hydrodynamic",
        )
        result = solver.solve()
        self.assertTrue(result["success"])
        self.assertGreater(result["root_time"], 0)

    def test_theoretical_iterations_calculation(self):
        """Test error bound formula n >= (ln(b-a) - ln(tol))/ln(2)."""
        # If interval span is 64, tol is 1 => n = 6 (since 64 / 2^6 = 1)
        iters = calculate_theoretical_iterations(0.0, 64.0, 1.0)
        self.assertEqual(iters, 6)

    def test_duration_formatting(self):
        """Test human readable time formatting."""
        duration = format_duration(65.5)  # 1 hr 5 mins 30 secs
        self.assertEqual(duration["hours"], 1)
        self.assertEqual(duration["minutes"], 5)
        self.assertAlmostEqual(duration["seconds"], 30.0, places=1)


class TestValidators(unittest.TestCase):
    """Test user input validation constraints."""

    def test_valid_inputs(self):
        form_data = {
            "capacity": "1000",
            "current_level": "200",
            "target_level": "800",
            "inflow_rate": "20",
            "drain_rate": "0",
        }
        is_valid, validated, errors = validate_tank_inputs(form_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        self.assertEqual(validated["capacity"], 1000.0)

    def test_invalid_target_less_than_current(self):
        form_data = {
            "capacity": "1000",
            "current_level": "800",
            "target_level": "200",
            "inflow_rate": "20",
        }
        is_valid, _, errors = validate_tank_inputs(form_data)
        self.assertFalse(is_valid)
        self.assertIn("target_water_level", errors)

    def test_target_exceeding_capacity(self):
        form_data = {
            "capacity": "1000",
            "current_level": "200",
            "target_level": "1500",
            "inflow_rate": "20",
        }
        is_valid, _, errors = validate_tank_inputs(form_data)
        self.assertFalse(is_valid)
        self.assertIn("target_water_level", errors)

    def test_drain_greater_than_inflow(self):
        form_data = {
            "capacity": "1000",
            "current_level": "200",
            "target_level": "800",
            "inflow_rate": "15",
            "drain_rate": "20",
        }
        is_valid, _, errors = validate_tank_inputs(form_data)
        self.assertFalse(is_valid)
        self.assertIn("drain_rate", errors)


class TestFlaskRoutes(unittest.TestCase):
    """Test Flask web controllers and API endpoints."""

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Water Tank Filling Time Calculator", response.data)

    def test_about_page(self):
        response = self.client.get("/about")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Bolzano", response.data)

    def test_calculator_get(self):
        response = self.client.get("/calculator")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hydraulic", response.data)

    def test_calculator_post_valid(self):
        response = self.client.post("/calculator", data={
            "capacity": "1000",
            "current_level": "150",
            "target_level": "950",
            "inflow_rate": "25",
            "drain_rate": "0",
            "tolerance": "0.0001",
            "max_iterations": "100",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Results", response.data)
        self.assertIn(b"Estimated Filling Time", response.data)

    def test_api_calculate_json(self):
        response = self.client.post(
            "/api/calculate",
            json={
                "capacity": 1000,
                "current_level": 150,
                "target_level": 950,
                "inflow_rate": 25,
                "tolerance": 0.0001,
            },
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data["success"])
        self.assertAlmostEqual(json_data["result"]["root_time"], 32.0, places=2)

    def test_404_error_page(self):
        response = self.client.get("/non-existent-page-url")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"404", response.data)


if __name__ == "__main__":
    unittest.main()
