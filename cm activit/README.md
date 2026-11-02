# TankFill – Water Tank Filling Time Calculator
### Computational Mathematics Laboratory &bull; Engineering Mini Project

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.1-black.svg)](https://flask.palletsprojects.com/)
[![Algorithm](https://img.shields.io/badge/Method-Bolzano's%20Bisection-emerald.svg)](#computational-mathematics--bisection-method)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 📌 Project Overview

**TankFill** is an interactive, full-stack engineering mini project developed for the **Computational Mathematics Laboratory**. It models transient fluid dynamics in water reservoirs and calculates the precise filling time required to transition from an initial water level to a target level using the classical **Bisection Method** (Bolzano's Root-Finding Algorithm).

The application combines rigorous numerical mathematics with modern web engineering, featuring an interactive **2D fluid visualizer**, real-time **Chart.js graphs**, complete **step-by-step iteration tables**, **dark/light theme support**, and **PDF / CSV laboratory export**.

---

## 🧮 Computational Mathematics & Bisection Method

### 1. Mathematical Formulation
Let:
- $V_{\text{max}}$ = Total Tank Capacity (Litres)
- $V_0$ = Initial / Current Water Level (Litres)
- $V_{\text{target}}$ = Target Water Level (Litres)
- $Q_{\text{in}}$ = Volumetric Inflow Rate (Litres/minute)
- $Q_{\text{out}}$ = Drain / Leak Outflow Rate (Litres/minute)
- $Q_{\text{net}} = Q_{\text{in}} - Q_{\text{out}}$ = Net volumetric inflow rate

From the hydraulic mass conservation equation:
$$\frac{dV}{dt} = Q_{\text{in}}(t) - Q_{\text{out}}(t)$$

Integrating with initial condition $V(0) = V_0$ gives the time-dependent volume function:
$$V(t) = V_0 + (Q_{\text{in}} - Q_{\text{out}}) \cdot t$$

To determine the filling time $t^*$, we define the continuous objective root-finding function $f(t)$:
$$f(t) = V(t) - V_{\text{target}} = V_0 + (Q_{\text{in}} - Q_{\text{out}}) \cdot t - V_{\text{target}} = 0$$

### 2. Nonlinear Hydrodynamic Dynamic Model (Optional)
When taking pump backpressure and hydrostatic head loss into account:
$$f(t) = V_{\text{max}} - (V_{\text{max}} - V_0) \cdot e^{-\frac{Q_{\text{net}}}{V_{\text{max}}} t} - V_{\text{target}} = 0$$

### 3. Bolzano's Intermediate Value Theorem (Root Bracketing)
If $f(t)$ is continuous on $[a, b]$ and:
$$f(a) \cdot f(b) \le 0$$
then there exists at least one root $t^* \in [a, b]$.

### 4. Bisection Iteration Algorithm
At each iteration step $k = 1, 2, \dots, N$:
1. Calculate the interval midpoint:
   $$c_k = \frac{a_k + b_k}{2}$$
2. Evaluate $f(c_k)$ and calculate the interval half-width error:
   $$\epsilon_k = \frac{b_k - a_k}{2}$$
3. Check the stopping criteria:
   $$\epsilon_k < \text{tolerance} \quad \text{or} \quad |f(c_k)| < \text{tolerance}$$
4. Update brackets:
   - If $f(a_k) \cdot f(c_k) < 0 \implies b_{k+1} = c_k, \; a_{k+1} = a_k$
   - Else $\implies a_{k+1} = c_k, \; b_{k+1} = b_k$

### 5. Theoretical Convergence Analysis & Error Bound
At each step, the search bracket is strictly halved:
$$\Delta_k = b_k - a_k = \frac{b_0 - a_0}{2^k}$$

The absolute error bound satisfies:
$$|c_k - t^*| \le \frac{b_0 - a_0}{2^{k+1}}$$

The theoretical minimum number of iterations $n$ required to achieve an error tolerance $\epsilon$ is:
$$n \ge \left\lceil \frac{\ln(b_0 - a_0) - \ln(\epsilon)}{\ln 2} \right\rceil$$

---

## 🚀 Key Features

- **Flask Modular Blueprints**: Clear separation into `home` and `calculator` blueprints following MVC design.
- **2D Fluid Dynamics Simulation**: Animated SVG / CSS wave water tank with bubbles, inflow pipe streams, and dynamic water level fill animation.
- **Interactive Chart.js Visualizations**:
  - **Water Level vs. Time**: Transient volume curve with capacity and target level markers.
  - **Convergence Error Curve**: Logarithmic interval decay line plotted against theoretical upper bounds.
- **Detailed Iteration Table**: Displays iteration step $k$, lower bound $a_k$, upper bound $b_k$, midpoint $c_k$, $f(a_k)$, $f(b_k)$, $f(c_k)$, error, sign test badges, and update actions.
- **Live Table Search Filter**: Real-time filtering of iteration steps and values.
- **One-Click Presets**: Preloaded scenarios (Residential 1,000L, Commercial 5,000L with drain, Industrial 2,500L with head loss, Lab Bench 100L).
- **Dark / Light Theme Toggle**: Seamless transition with `localStorage` persistence and dynamic chart recoloring.
- **Export & Reporting**:
  - **Download PDF Report**: Formatted print layout for lab records.
  - **Export Iteration Table as CSV**: Download raw tabular calculations.
  - **Copy Root Time**: One-click clipboard copy with toast feedback.
- **Robust Input Validation**: Strict physical constraints, cross-field checks, and graceful error handling.

---

## 📁 Project Structure

```
cm activit/
│
├── app.py                      # Flask Application Factory & Server Entry Point
├── config.py                   # Centralized Configuration (Dev, Testing, Prod)
├── requirements.txt            # Python Dependencies
├── test_app.py                 # Automated Test Suite (15 Unit Tests)
├── README.md                   # Complete Documentation & Lab Report
│
├── routes/                     # Controllers (Flask Blueprints)
│   ├── __init__.py
│   ├── home.py                 # Home & About Routes
│   └── calculator.py           # Calculator, AJAX API & CSV Export Routes
│
├── services/                   # Numerical Computing Service
│   ├── __init__.py
│   └── bisection.py            # Bisection Numerical Engine & Solvers
│
├── utils/                      # Reusable Utilities
│   ├── __init__.py
│   ├── validators.py           # Comprehensive Form & API Input Validation
│   └── math_helpers.py         # Theoretical Bounds, Unit Formats, Time Series
│
├── static/                     # Frontend Assets
│   ├── css/
│   │   ├── style.css           # Design Tokens, Typography, Themes, Print Styles
│   │   └── components.css      # Cards, 2D Tank Simulation, Iteration Table, Badges
│   ├── js/
│   │   ├── theme.js            # Dark/Light Mode Switcher & Chart Theme Dispatcher
│   │   ├── charts.js           # Chart.js Integration & Real-time Visualizers
│   │   ├── calculator.js       # AJAX Engine, Tank Animation & Search Filters
│   │   └── main.js             # Mobile Navigation & Global Accordion Handlers
│   └── images/
│       ├── logo.svg            # Hydro-Mathematical Droplet Logo
│       └── favicon.svg         # Application Favicon
│
└── templates/                  # Jinja2 Templates (No Inline CSS/JS)
    ├── base.html               # Master Layout, Header, Navigation & Footer
    ├── index.html              # Landing Page & Computational Workflow
    ├── calculator.html         # Main Dashboard, Form, Visualizer & Results
    ├── result.html             # Dedicated Full Results Report
    ├── about.html              # Theoretical Foundations & Method Comparison
    └── error.html              # Custom Error Page (400, 404, 500)
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10 or newer (tested with Python 3.13)
- `pip` package manager

### 1. Clone / Navigate to Project Directory
```bash
cd "c:\Users\nikki\OneDrive\Desktop\cm activit"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Unit Tests
```bash
python test_app.py
```
*(All 15 tests verify numerical convergence, bounds, validators, and HTTP endpoints).*

### 4. Start the Application
```bash
python app.py
```

### 5. Access the Web Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 🌐 Application Pages & Routes

| Route | HTTP Method | Description |
|---|---|---|
| `/` | `GET` | Home landing page with hero banner and workflow overview. |
| `/calculator` | `GET`, `POST` | Interactive calculator with 2D tank visualizer and results. |
| `/api/calculate` | `POST` | Asynchronous JSON API endpoint for calculations. |
| `/result` | `GET` | Dedicated laboratory numerical report view. |
| `/about` | `GET` | Comprehensive Bisection Method theory and comparisons. |
| `/export/csv` | `POST` | Download iteration table as CSV. |
| Custom 404 / 500 | `*` | Custom error handler templates with recovery navigation. |

---

## 📊 Sample Calculation Scenario

| Parameter | Value |
|---|---|
| **Tank Capacity ($V_{\text{max}}$)** | $1,000.0\text{ Litres}$ |
| **Initial Water Level ($V_0$)** | $150.0\text{ Litres}$ ($15.0\%$) |
| **Target Water Level ($V_{\text{target}}$)** | $950.0\text{ Litres}$ ($95.0\%$) |
| **Inflow Rate ($Q_{\text{in}}$)** | $25.0\text{ Litres/minute}$ |
| **Drain / Leak Rate ($Q_{\text{out}}$)** | $0.0\text{ Litres/minute}$ |
| **Tolerance ($\epsilon$)** | $10^{-4}$ ($0.0001$) |
| **Calculated Filling Time ($t^*$)** | **$32.0000\text{ minutes}$** ($32\text{ mins } 0\text{ secs}$) |
| **Total Iterations** | **$19\text{ steps}$** (Theory predicted: $19$) |
| **Final Residual Error** | **$7.6294 \times 10^{-5} < 10^{-4}$** |
| **Execution Time** | **$\approx 0.45\text{ ms}$** |

---

## 🎓 Academic Attribution

- **Course:** Computational Mathematics Laboratory
- **Algorithm:** Bolzano's Bisection Method
- **Convergence Rate:** Linear $\mathcal{O}(2^{-n})$
- **Framework:** Python Flask (MVC Pattern)
- **Year:** 2026–2027
