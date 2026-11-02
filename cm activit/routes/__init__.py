"""Routes package for TankFill application.

Registers Flask Blueprints for home and calculator controllers.
"""

from routes.home import home_bp
from routes.calculator import calculator_bp

__all__ = ["home_bp", "calculator_bp"]
