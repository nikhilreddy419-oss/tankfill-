"""TankFill – Water Tank Filling Time Calculator.

Main Flask Application Entry Point.
Organized using the Application Factory Pattern and Flask Blueprints.
"""

from flask import Flask, render_template
from config import get_config
from routes.home import home_bp
from routes.calculator import calculator_bp
from utils.math_helpers import format_number


def create_app(config_object=None) -> Flask:
    """Application Factory.

    Instantiates and configures the Flask application, registers blueprints,
    attaches custom Jinja filters, and configures centralized error handling.
    """
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Load configuration
    if config_object is None:
        config_object = get_config()
    app.config.from_object(config_object)

    # Register Blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(calculator_bp)

    # Register custom template filters
    @app.template_filter("format_eng")
    def format_eng_filter(value, precision=6):
        """Format number for engineering output."""
        return format_number(value, precision)

    @app.template_filter("scientific")
    def scientific_filter(value):
        """Format number in scientific notation."""
        if value is None:
            return "N/A"
        try:
            return f"{float(value):.4e}"
        except (ValueError, TypeError):
            return str(value)

    # Global context processor
    @app.context_processor
    def inject_app_metadata():
        return {
            "APP_NAME": app.config.get("APP_NAME", "TankFill"),
            "APP_SHORT_NAME": app.config.get("APP_SHORT_NAME", "TankFill"),
            "APP_VERSION": app.config.get("APP_VERSION", "2.1.0"),
            "COURSE_NAME": app.config.get("COURSE_NAME", "Computational Mathematics Laboratory"),
            "ACADEMIC_YEAR": app.config.get("ACADEMIC_YEAR", "2026-2027"),
        }

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template(
            "error.html",
            error_code=404,
            error_title="Page Not Found",
            error_message="The requested laboratory page or calculation route could not be found.",
            title="404 – Page Not Found",
        ), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template(
            "error.html",
            error_code=500,
            error_title="Computational Server Error",
            error_message="An unexpected mathematical or server exception occurred during execution.",
            title="500 – Server Error",
        ), 500

    @app.errorhandler(400)
    def bad_request(error):
        return render_template(
            "error.html",
            error_code=400,
            error_title="Bad Request",
            error_message="The submitted calculation parameters were malformed or invalid.",
            title="400 – Bad Request",
        ), 400

    return app


# Application instance for development server
app = create_app()

if __name__ == "__main__":
    print("=" * 65)
    print(" [TankFill] Water Tank Filling Time Calculator")
    print(" Computational Mathematics Laboratory Application")
    print(" Server Running at: http://127.0.0.1:5000")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5000, debug=True)
