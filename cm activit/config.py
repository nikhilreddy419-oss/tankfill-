"""Application Configuration Module.

Provides configuration classes for TankFill - Water Tank Filling Time Calculator.
Supports Development, Testing, and Production configurations.
"""

import os


class Config:
    """Base configuration with default parameters."""

    # Application Information
    APP_NAME = "TankFill – Water Tank Filling Time Calculator"
    APP_SHORT_NAME = "TankFill"
    APP_VERSION = "2.1.0"
    COURSE_NAME = "Computational Mathematics Laboratory"
    ACADEMIC_YEAR = "2026-2027"

    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY", "tankfill-super-secret-key-computational-math-2026")

    # Bisection Defaults
    DEFAULT_TOLERANCE = 1e-4
    MIN_TOLERANCE = 1e-8
    MAX_TOLERANCE = 1e-1
    DEFAULT_MAX_ITERATIONS = 100
    MAX_ALLOWED_ITERATIONS = 500

    # Physical Bounds
    MAX_TANK_CAPACITY = 1_000_000.0  # Litres
    MIN_TANK_CAPACITY = 1.0  # Litres
    MIN_INFLOW_RATE = 0.01  # Litres/min
    MAX_INFLOW_RATE = 100_000.0  # Litres/min

    # Server settings
    HOST = "127.0.0.1"
    PORT = 5000
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Configuration for local development."""

    DEBUG = True


class ProductionConfig(Config):
    """Configuration for production deployment."""

    DEBUG = False


class TestingConfig(Config):
    """Configuration for running automated unit tests."""

    TESTING = True
    DEBUG = True


# Mapping of environment names to configuration objects
CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Retrieve the active configuration based on the FLASK_ENV environment variable."""
    env = os.environ.get("FLASK_ENV", "development").lower()
    return CONFIG_MAP.get(env, DevelopmentConfig)
