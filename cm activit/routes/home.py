"""Home Blueprint Module.

Handles informational and theoretical pages:
- Home Landing Page ('/')
- About Bisection Method ('/about')
"""

from flask import Blueprint, render_template

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    """Render the application landing page.

    Features hero section, methodology overview, key project capabilities,
    and direct quick links to the calculator.
    """
    return render_template("index.html", title="Home – TankFill Calculator")


@home_bp.route("/about")
def about():
    """Render the detailed computational mathematics guide.

    Explains Bolzano's Intermediate Value Theorem, derivation of Bisection,
    error bounding formulas, algorithm comparison table, and engineering context.
    """
    return render_template("about.html", title="About Bisection Method – Theory & Mechanics")
