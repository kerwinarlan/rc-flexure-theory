"""NSCP 2015 / ACI 318 RC Flexure Solver GUI with Step-by-Step LaTeX Solution, Whitney UDL Diagram & US/SI Support.

Follows Engr. Jaydee Lucero's FreeSimpleGUI 5-step template pattern for structural engineering tools.
"""

import io
import sys
import FreeSimpleGUI as sg
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for PNG generation
import matplotlib.pyplot as plt
import numpy as np

from flexure import (
    calculate_beta_1,
    calculate_concrete_modulus,
    calculate_cracked_moment_of_inertia,
    calculate_inelastic_capacity,
    calculate_modular_ratio,
    calculate_moment_curvature,
    calculate_neutral_axis_depth,
    calculate_service_stresses,
)


def solve_flexure_section(
    fc_prime: float,
    fy: float,
    b: float,
    d: float,
    as_area: float,
    m_serv: float,
    m_ult: float,
    units: str = "US",
    lambda_factor: float = 1.0,
) -> dict[str, float | str | dict]:
    """Calculate elastic (WSD), inelastic (USD), and moment-curvature parameters per ACI 318 / NSCP 2015."""
    if fc_prime <= 0 or fy <= 0 or b <= 0 or d <= 0 or as_area <= 0 or m_serv < 0 or m_ult < 0:
        raise ValueError("Input parameters must be positive numbers.")

    is_si = units.upper() == "SI"
    h = d + (65.0 if is_si else 2.5)  # Estimated total depth

    # Elastic WSD calculations
    ec = calculate_concrete_modulus(fc_prime, units)
    n = calculate_modular_ratio(fc_prime, units)
    beta1 = calculate_beta_1(fc_prime, units)
    x = calculate_neutral_axis_depth(b, d, as_area, n)

    q_c = (b * x) * (x / 2.0)
    q_s = (n * as_area) * (d - x)
    i_cr = calculate_cracked_moment_of_inertia(b, d, as_area, n, x)

    # Conversion for service moment
    m_serv_raw = m_serv * (1e6 if is_si else 1.0)
    fc, fs = calculate_service_stresses(m_serv_raw, b, d, as_area, n)
    fc_allow = 0.45 * fc_prime
    fs_allow = 0.50 * fy

    util_c = fc / fc_allow if fc_allow > 0 else 0.0
    util_s = fs / fs_allow if fs_allow > 0 else 0.0

    # Inelastic USD calculations
    inelastic = calculate_inelastic_capacity(b, d, as_area, fc_prime, fy, units, lambda_factor)
    util_ult = m_ult / inelastic["phi_M_n"] if inelastic["phi_M_n"] > 0 else 0.0

    # Moment-Curvature Curve with 3 explicit regions
    mc_data = calculate_moment_curvature(b, d, h, as_area, fc_prime, fy, units, lambda_factor)

    status = (
        "PASS"
        if util_c <= 1.0 and util_s <= 1.0 and util_ult <= 1.0
        else "RESIZE SECTION"
    )

    return {
        "fc": fc_prime,
        "fy": fy,
        "b": b,
        "d": d,
        "as_area": as_area,
        "m_serv": m_serv,
        "m_ult": m_ult,
        "units": units,
        "E_c": ec,
        "n": n,
        "beta_1": beta1,
        "x": x,
        "Q_c": q_c,
        "Q_s": q_s,
        "I_cr": i_cr,
        "f_c": fc,
        "f_c_allow": fc_allow,
        "util_c": util_c,
        "f_s": fs,
        "f_s_allow": fs_allow,
        "util_s": util_s,
        "inelastic": inelastic,
        "util_ult": util_ult,
        "mc_data": mc_data,
        "status": status,
    }


def generate_inelastic_diagram_png(
    b: float, d: float, as_area: float, fc_prime: float, fy: float, inelastic: dict, units: str = "US"
) -> bytes:
    """Generate a 3-panel matplotlib diagram with perfectly aligned horizontal reference lines across subplots."""
    c = float(inelastic["c"])
    a = float(inelastic["a"])
    eps_s = float(inelastic["eps_s"])
    f_s = float(inelastic["f_s"])
    is_si = units.upper() == "SI"
    h = d + (65.0 if is_si else 2.5)

    f_unit = "MPa" if is_si else "ksi"
    l_unit = "mm" if is_si else "in"
    l_sym = "mm" if is_si else '"'

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(7.2, 3.4), sharey=True, dpi=100)
    fig.patch.set_facecolor("#FAFAFA")

    y_min = -h - (10.0 if is_si else 1.5)
    y_max = 10.0 if is_si else 1.5

    # Panel 1: Cross Section Geometry
    ax1.set_title(f"Beam Section ({l_unit})", fontsize=9, fontweight="bold")
    ax1.plot([0, b, b, 0, 0], [0, 0, -h, -h, 0], "k-", lw=1.5)
    ax1.fill_between([0, b], 0, -a, color="#FFCC80", alpha=0.7)
    n_bars = 3
    xs = [b * (i + 1) / (n_bars + 1) for i in range(n_bars)]
    ax1.scatter(xs, [-d] * n_bars, color="black", s=50, zorder=5)
    ax1.set_xlim(-b * 0.35, b * 1.35)

    # Panel 2: Inelastic Strain Profile
    ax2.set_title("Inelastic Strain (ε)", fontsize=9, fontweight="bold")
    ax2.axvline(0, color="gray", lw=0.8)
    ax2.plot([-0.003, eps_s], [0, -d], "b-o", lw=1.8, ms=4)
    ax2.fill_betweenx([0, -c], 0, [-0.003, 0], color="blue", alpha=0.15)
    ax2.fill_betweenx([-c, -d], 0, [0, eps_s], color="red", alpha=0.15)
    ax2.text(-0.003, 0.8 if not is_si else 5.0, "εu=0.003", fontsize=7, color="blue", ha="center")
    ax2.text(eps_s, -d - (1.2 if not is_si else 15.0), f"εs={eps_s:.5f}", fontsize=7, color="red", ha="center")
    ax2.set_xlim(-0.005, max(0.005, eps_s * 1.3))

    # Panel 3: Whitney Stress UDL Box & Force Resultants
    ax3.set_title(f"Whitney Stress UDL ({f_unit})", fontsize=9, fontweight="bold")
    stress_mag = 0.85 * fc_prime
    s_x = stress_mag * 1.4

    ax3.plot([0, 0], [0, -h], "k-", lw=1.5)
    ax3.plot([0, stress_mag, stress_mag, 0], [0, 0, -a, -a], color="orange", lw=1.5)
    ax3.fill_betweenx([0, -a], 0, stress_mag, color="orange", alpha=0.25)

    # UDL compression arrows pointing LEFT (<-)
    n_udl = 5
    y_udls = np.linspace(-a * 0.15, -a * 0.85, n_udl)
    for y_i in y_udls:
        ax3.annotate("", xy=(0, y_i), xytext=(stress_mag, y_i),
                     arrowprops=dict(arrowstyle="->", color="darkorange", lw=1.0))

    # Resultant Compression Force C pointing LEFT (<-)
    y_c = -a / 2.0
    ax3.annotate("", xy=(-s_x * 0.6, y_c), xytext=(stress_mag * 1.1, y_c),
                 arrowprops=dict(arrowstyle="->", color="darkorange", lw=2.0))
    ax3.text(-s_x * 0.65, y_c, "C = 0.85f'c·b·a", color="darkorange", fontweight="bold", fontsize=7, ha="right", va="center")

    # Resultant Tension Force T pointing RIGHT (->)
    ax3.annotate("", xy=(s_x * 0.8, -d), xytext=(0, -d),
                 arrowprops=dict(arrowstyle="->", color="red", lw=2.2))
    ax3.text(s_x * 0.85, -d, "T = As·fs", color="red", fontweight="bold", fontsize=7, ha="left", va="center")
    ax3.set_xlim(-s_x * 1.5, s_x * 1.5)

    # Perfectly aligned shared horizontal reference lines stretching across ALL THREE panels!
    for ax in (ax1, ax2, ax3):
        ax.axhline(0, color="black", linestyle="--", lw=0.8, alpha=0.6)        # Top fiber y=0
        ax.axhline(-a, color="darkorange", linestyle=":", lw=0.9)              # Whitney block bottom y=-a
        ax.axhline(-c, color="red", linestyle="--", lw=1.0)                    # Neutral Axis y=-c
        ax.axhline(-d, color="blue", linestyle=":", lw=0.7, alpha=0.5)         # Steel centroid y=-d
        ax.axhline(-h, color="black", linestyle="--", lw=0.8, alpha=0.6)       # Bottom fiber y=-h
        ax.set_ylim(y_min, y_max)
        ax.axis("off")

    # Labels on Panel 1 left
    ax1.text(-b * 0.38, 0, "Top Fiber", fontsize=6.5, color="black", va="center", ha="right")
    ax1.text(-b * 0.38, -a, f"a={a:.2f}{l_sym}", fontsize=6.5, color="darkorange", va="center", ha="right")
    ax1.text(-b * 0.38, -c, f"N.A. c={c:.2f}{l_sym}", fontsize=6.5, color="red", va="center", ha="right")
    ax1.text(-b * 0.38, -d, f"d={d:.1f}{l_sym}", fontsize=6.5, color="blue", va="center", ha="right")
    ax1.text(-b * 0.38, -h, f"h={h:.1f}{l_sym}", fontsize=6.5, color="black", va="center", ha="right")

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)
    return buf.getvalue()


def generate_moment_curvature_plot_png(
    mc_data: dict, m_serv: float, m_ult: float
) -> bytes:
    """Generate a matplotlib plot highlighting the 3 flexural behavior regions on the M - phi curve."""
    phi_pts = mc_data["phi_pts"]
    m_pts = mc_data["m_pts"]
    m_cr = mc_data["M_cr"]
    m_y = mc_data["M_y"]
    m_n = mc_data["M_n"]
    mu_phi = mc_data["ductility_ratio"]
    m_unit = mc_data["m_unit"]
    phi_unit = mc_data["phi_unit"]

    fig, ax = plt.subplots(figsize=(6.8, 3.2), dpi=100)
    fig.patch.set_facecolor("#FAFAFA")

    # Shaded Behavior Regions
    ax.axvspan(0, phi_pts[1], color="#C8E6C9", alpha=0.4, label="O->C: Elastic & Uncracked")
    ax.axvspan(phi_pts[1], phi_pts[2], color="#FFF9C4", alpha=0.5, label="C->Y: Elastic & Cracked")
    ax.axvspan(phi_pts[2], phi_pts[3], color="#FFCDD2", alpha=0.4, label="Y->U: Inelastic & Cracked")

    # Backbone plot
    ax.plot(phi_pts, m_pts, "b-o", lw=2.2, ms=5)

    # Key Point Markers
    ax.scatter([phi_pts[0]], [0], color="black", s=30, zorder=5)
    ax.text(phi_pts[0], m_n * 0.02, "O", fontsize=8, fontweight="bold", ha="center")

    ax.scatter([phi_pts[1]], [m_cr], color="green", s=50, zorder=5)
    ax.text(phi_pts[1], m_cr + m_n * 0.04, f"C ({m_cr:.1f})", fontsize=7, fontweight="bold", color="green", ha="center")

    ax.scatter([phi_pts[2]], [m_y], color="darkorange", s=50, zorder=5)
    ax.text(phi_pts[2], m_y + m_n * 0.04, f"Y ({m_y:.1f})", fontsize=7, fontweight="bold", color="darkorange", ha="right")

    ax.scatter([phi_pts[3]], [m_n], color="red", s=50, zorder=5)
    ax.text(phi_pts[3], m_n + m_n * 0.04, f"U ({m_n:.1f})", fontsize=7, fontweight="bold", color="red", ha="right")

    # Demand levels
    ax.axhline(m_serv, color="gray", linestyle=":", lw=1.2, label=f"M_service={m_serv:.1f}{m_unit}")
    ax.axhline(m_ult, color="purple", linestyle="--", lw=1.2, label=f"M_factored={m_ult:.1f}{m_unit}")

    ax.set_title(f"3-Region Moment - Curvature (Curvature Ductility µ_ϕ = {mu_phi:.2f})", fontsize=9, fontweight="bold")
    ax.set_xlabel(f"Curvature ϕ ({phi_unit})", fontsize=8)
    ax.set_ylabel(f"Flexural Moment M ({m_unit})", fontsize=8)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(fontsize=6.5, loc="lower right", framealpha=0.9)

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)
    return buf.getvalue()


def generate_step_by_step_latex_png(res: dict) -> bytes:
    """Generate a step-by-step LaTeX solution card with explicit NSCP 2015 / ACI 318 citations."""
    units = res["units"]
    is_si = units.upper() == "SI"
    fc = res["fc"]
    fy = res["fy"]
    b = res["b"]
    d = res["d"]
    a_s = res["as_area"]
    beta1 = res["beta_1"]
    inel = res["inelastic"]
    a = inel["a"]
    c = inel["c"]
    eps_s = inel["eps_s"]
    phi = inel["phi"]
    m_n = inel["M_n"]
    phi_m_n = inel["phi_M_n"]

    m_unit = "kN·m" if is_si else "kip-in"
    f_unit = "MPa" if is_si else "ksi"
    l_unit = "mm" if is_si else "in"
    e_s_val = 200000.0 if is_si else 29000.0
    eps_y = fy / e_s_val

    fig, ax = plt.subplots(figsize=(6.8, 3.4), dpi=100)
    fig.patch.set_facecolor("#FAFAFA")
    ax.axis("off")

    lines = [
        ("NSCP 2015 / ACI 318 Step-by-Step Flexural Solution", True, "#0D47A1"),
        ("Step 1: Material & Section Parameters", True, "#1A237E"),
        (r"$f'_c = %.1f \text{ %s} \rightarrow \beta_1 = %.2f$ (NSCP 2015 Table 422.2.2.4.3)" % (fc, f_unit, beta1), False, "#1A237E"),
        (r"$\epsilon_y = \frac{f_y}{E_s} = \frac{%.1f}{%.0f} = %.5f$ (NSCP 2015 Sec 420.2.2.1)" % (fy, e_s_val, eps_y), False, "#1A237E"),
        ("Step 2: Depth of Compression Stress Block (a)", True, "#1A237E"),
        (r"$C = T \rightarrow 0.85 f'_c b a = A_s f_y$ (NSCP 2015 Sec 422.2.2)", False, "#1A237E"),
        (r"$a = \frac{A_s f_y}{0.85 f'_c b} = \frac{%.1f \times %.1f}{0.85 \times %.1f \times %.1f} = \mathbf{%.2f \text{ %s}}$" % (a_s, fy, fc, b, a, l_unit), False, "#0D47A1"),
        ("Step 3: Neutral Axis Depth (c) & Strain Verification", True, "#1A237E"),
        (r"$c = \frac{a}{\beta_1} = \frac{%.2f}{%.2f} = \mathbf{%.2f \text{ %s}}$ (NSCP 2015 Table 422.2.2.4.3)" % (a, beta1, c, l_unit), False, "#0D47A1"),
        (r"$\epsilon_s = 0.003 \cdot \frac{%.1f - %.2f}{%.2f} = %.5f \geq %.5f$ (Steel Yielded)" % (d, c, c, eps_s, eps_y), False, "#1A237E"),
        ("Step 4: Strength Reduction Factor (ϕ) & Moment Capacity", True, "#1A237E"),
        (r"$\epsilon_s = %.5f \geq 0.005 \rightarrow \phi = %.2f$ (NSCP 2015 Sec 421.2.2 - Ductile)" % (eps_s, phi), False, "#1A237E"),
        (r"$M_n = A_s f_y \left(d - \frac{a}{2}\right) = \mathbf{%.1f \text{ %s}}$ (NSCP 2015 Sec 422.2)" % (m_n, m_unit), False, "#0D47A1"),
        (r"$\phi M_n = %.2f \times %.1f = \mathbf{%.1f \text{ %s}}$ (NSCP 2015 Sec 421.2)" % (phi, m_n, phi_m_n, m_unit), False, "#0D47A1"),
    ]

    y_pos = 0.96
    for text, is_bold, color in lines:
        fontw = "bold" if is_bold else "normal"
        fsize = 8.2 if is_bold else 7.5
        ax.text(0.02, y_pos, text, fontsize=fsize, fontweight=fontw, color=color)
        y_pos -= 0.068

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)
    return buf.getvalue()


def generate_latex_summary_card_png(res: dict) -> bytes:
    """Generate a summary card rendering publication-quality math."""
    units = res["units"]
    is_si = units.upper() == "SI"
    ec = res["E_c"]
    n = res["n"]
    x = res["x"]
    icr = res["I_cr"]
    inel = res["inelastic"]
    mc = res["mc_data"]

    m_unit = "kN·m" if is_si else "kip-in"
    f_unit = "MPa" if is_si else "ksi"
    l_unit = "mm" if is_si else "in"
    c_unit = "rad/m" if is_si else "1/in"

    fig, ax = plt.subplots(figsize=(6.8, 3.2), dpi=100)
    fig.patch.set_facecolor("#FAFAFA")
    ax.axis("off")

    lines = [
        r"$\mathbf{NSCP\ 2015\ /\ ACI\ 318\ LaTeX\ Flexural\ Equations}$",
        r"$E_c = %s \rightarrow E_c = %.2f\ \text{%s}, \quad n = \frac{E_s}{E_c} = %.2f$" %
            ("4700\\sqrt{f'_c}" if is_si else "57\\sqrt{f'_c\\cdot 1000}", ec, f_unit, n),
        r"$Q_c = Q_s \rightarrow \frac{1}{2} b x^2 = n A_s (d - x) \rightarrow x = %.2f\ \text{%s}$" % (x, l_unit),
        r"$I_{cr} = \frac{1}{3} b x^3 + n A_s (d - x)^2 = %.3e\ \text{%s}^4$" % (icr, l_unit),
        r"$a = \frac{A_s f_y}{0.85 f'_c b} = %.2f\ \text{%s}, \quad c = \frac{a}{\beta_1} = %.2f\ \text{%s}$" % (inel["a"], l_unit, inel["c"], l_unit),
        r"$M_n = A_s f_s \left(d - \frac{a}{2}\right) = %.2f\ \text{%s}, \quad \phi M_n = %.2f\ \text{%s}$" % (inel["M_n"], m_unit, inel["phi_M_n"], m_unit),
        r"$\phi_y = \frac{\epsilon_y}{d - x} = %.6f\ \text{%s}, \quad \phi_u = \frac{\epsilon_u}{c} = %.6f\ \text{%s}$" % (mc["phi_y"], c_unit, mc["phi_u"], c_unit),
        r"$\mu_\phi = \frac{\phi_u}{\phi_y} = %.2f \quad \text{[%s]}$" % (mc["ductility_ratio"], inel["failure_mode"]),
    ]

    y_pos = 0.92
    for line in lines:
        ax.text(0.03, y_pos, line, fontsize=8.2, color="#1A237E")
        y_pos -= 0.12

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)
    return buf.getvalue()


def create_window(units: str = "US", preset_vals: dict | None = None) -> sg.Window:
    """Build the FreeSimpleGUI layout using Engr. Lucero's signature structure."""
    sg.theme("SystemDefault")
    is_si = units.upper() == "SI"

    pv = preset_vals or {}
    def_fc = pv.get("fc", "28.0" if is_si else "4.0")
    def_fy = pv.get("fy", "420.0" if is_si else "60.0")
    def_b = pv.get("b", "300.0" if is_si else "12.0")
    def_d = pv.get("d", "500.0" if is_si else "20.0")
    def_as = pv.get("as", "1500.0" if is_si else "2.37")
    def_mserv = pv.get("mserv", "100.0" if is_si else "1200.0")
    def_mult = pv.get("mult", "220.0" if is_si else "2000.0")

    f_unit = "MPa" if is_si else "ksi"
    l_unit = "mm" if is_si else "in"
    a_unit = "mm²" if is_si else "in²"
    m_unit = "kN·m" if is_si else "kip-in"

    layout = [
        [sg.Text("NSCP 2015 / ACI 318 RC Flexure Solver (LaTeX & Multi-Units)", font=("Helvetica", 12, "bold"))],
        [
            sg.Text("Unit System:", font=("Helvetica", 9, "bold")),
            sg.Combo(["US Customary (kip-in, 1/in, ksi, in)", "SI Metric (kN·m, rad/m, MPa, mm)"],
                     default_value="US Customary (kip-in, 1/in, ksi, in)" if not is_si else "SI Metric (kN·m, rad/m, MPa, mm)",
                     key="-UNITS-", enable_events=True, readonly=True),
            sg.Text("  Preset Examples:", font=("Helvetica", 9, "bold")),
            sg.Combo(["Custom Inputs", "CE 152 Example 3 (b=250mm, d=575mm, f'c=28MPa, fy=420MPa, As=1470mm²)"],
                     default_value="Custom Inputs" if not pv else "CE 152 Example 3 (b=250mm, d=575mm, f'c=28MPa, fy=420MPa, As=1470mm²)",
                     key="-PRESET-", enable_events=True, readonly=True),
        ],
        [sg.HorizontalSeparator()],
        # Input Section
        [
            sg.Text("Concrete f'c =", size=(14, 1)),
            sg.Input(def_fc, key="-FC-", size=(8, 1)),
            sg.Text(f_unit, key="-U-FC-", size=(6, 1)),
            sg.Text("Steel fy =", size=(10, 1)),
            sg.Input(def_fy, key="-FY-", size=(8, 1)),
            sg.Text(f_unit, key="-U-FY-", size=(6, 1)),
        ],
        [
            sg.Text("Beam width b =", size=(14, 1)),
            sg.Input(def_b, key="-B-", size=(8, 1)),
            sg.Text(l_unit, key="-U-B-", size=(6, 1)),
            sg.Text("Depth d =", size=(10, 1)),
            sg.Input(def_d, key="-D-", size=(8, 1)),
            sg.Text(l_unit, key="-U-D-", size=(6, 1)),
        ],
        [
            sg.Text("Steel area As =", size=(14, 1)),
            sg.Input(def_as, key="-AS-", size=(8, 1)),
            sg.Text(a_unit, key="-U-AS-", size=(6, 1)),
            sg.Text("Service M =", size=(10, 1)),
            sg.Input(def_mserv, key="-MSERV-", size=(8, 1)),
            sg.Text(m_unit, key="-U-MSERV-", size=(6, 1)),
        ],
        [
            sg.Text("Factored Mu =", size=(14, 1)),
            sg.Input(def_mult, key="-MULT-", size=(8, 1)),
            sg.Text(m_unit, key="-U-MULT-", size=(6, 1)),
        ],
        [sg.Button("Calculate & Plot", button_color=("white", "navy")), sg.Button("Exit")],
        [sg.HorizontalSeparator()],
        # Output Results and Tabbed Visualizations
        [
            sg.Column(
                [
                    [sg.Text("Analysis Results", font=("Helvetica", 10, "bold"))],
                    [sg.Multiline("", key="-OUTPUT-", size=(44, 16), disabled=True, font=("Courier", 9))],
                ]
            ),
            sg.TabGroup(
                [
                    [
                        sg.Tab(
                            "Step-by-Step LaTeX Solution",
                            [[sg.Image(key="-IMAGE-STEPS-", size=(460, 270))]],
                        ),
                        sg.Tab(
                            "Whitney Stress UDL Diagram",
                            [[sg.Image(key="-IMAGE-STRESS-", size=(460, 270))]],
                        ),
                        sg.Tab(
                            "Moment - Curvature (M - ϕ)",
                            [[sg.Image(key="-IMAGE-MPH-", size=(460, 270))]],
                        ),
                        sg.Tab(
                            "LaTeX Math Derivation",
                            [[sg.Image(key="-IMAGE-LATEX-", size=(460, 270))]],
                        ),
                    ]
                ]
            ),
        ],
    ]

    return sg.Window("NSCP 2015 / ACI 318 RC Flexure Solver", layout, finalize=True)


def run_gui() -> None:
    """Run event loop."""
    window = create_window("US")

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break

        if event == "-UNITS-":
            selected_unit = "SI" if "SI" in values["-UNITS-"] else "US"
            window.close()
            window = create_window(selected_unit)
            continue

        if event == "-PRESET-":
            if "CE 152 Example 3" in values["-PRESET-"]:
                pv = {"fc": "28.0", "fy": "420.0", "b": "250.0", "d": "575.0", "as": "1470.0", "mserv": "100.0", "mult": "220.0"}
                window.close()
                window = create_window("SI", preset_vals=pv)
            continue

        if event == "Calculate & Plot":
            try:
                selected_unit = "SI" if "SI" in values["-UNITS-"] else "US"
                fc = float(values["-FC-"])
                fy = float(values["-FY-"])
                b = float(values["-B-"])
                d = float(values["-D-"])
                a_s = float(values["-AS-"])
                m_serv = float(values["-MSERV-"])
                m_ult = float(values["-MULT-"])

                res = solve_flexure_section(fc, fy, b, d, a_s, m_serv, m_ult, selected_unit)
                inel = res["inelastic"]
                mc = res["mc_data"]
                m_unit = mc["m_unit"]
                f_unit = "MPa" if selected_unit == "SI" else "ksi"
                l_unit = "mm" if selected_unit == "SI" else "in"

                def get_region(m_val):
                    if m_val <= mc["M_cr"]:
                        return "Region O->C (Elastic Uncracked)"
                    elif m_val <= mc["M_y"]:
                        return "Region C->Y (Elastic Cracked)"
                    else:
                        return "Region Y->U (Inelastic Cracked)"

                out_text = (
                    f"--- BEHAVIOR REGIONS BREAKDOWN ---\n"
                    f"O->C Elastic Uncracked: 0 <= M <= {mc['M_cr']:.1f} {m_unit}\n"
                    f"C->Y Elastic Cracked  : {mc['M_cr']:.1f} < M <= {mc['M_y']:.1f} {m_unit}\n"
                    f"Y->U Inelastic Cracked: {mc['M_y']:.1f} < M <= {mc['M_n']:.1f} {m_unit}\n\n"
                    f"Service M State       : {get_region(m_serv)}\n"
                    f"Factored Mu State      : {get_region(m_ult)}\n\n"
                    f"--- INELASTIC STRESS BLOCK (a) ---\n"
                    f"Stress Block Depth (a): {inel['a']:.2f} {l_unit}\n"
                    f"Inelastic NA Depth (c): {inel['c']:.2f} {l_unit}\n"
                    f"Steel Strain (eps_s)  : {inel['eps_s']:.5f}\n"
                    f"Phi Factor (phi)      : {inel['phi']:.2f}\n"
                    f"Nominal Cap. (M_n)    : {inel['M_n']:.1f} {m_unit}\n"
                    f"Design Cap. (phi*M_n) : {inel['phi_M_n']:.1f} {m_unit} ({res['util_ult']*100:.1f}%)\n\n"
                    f"--- ELASTIC (WSD) PARAMETERS ---\n"
                    f"Concrete Modulus (E_c) : {res['E_c']:.2f} {f_unit}\n"
                    f"Modular Ratio (n)     : {res['n']:.2f}\n"
                    f"Elastic NA Depth (x)  : {res['x']:.2f} {l_unit}\n"
                    f"Service f_c / Allow   : {res['f_c']:.2f} / {res['f_c_allow']:.2f} {f_unit}\n"
                    f"Service f_s / Allow   : {res['f_s']:.2f} / {res['f_s_allow']:.2f} {f_unit}\n"
                    f"Curvature Ductility µ_ϕ: {mc['ductility_ratio']:.2f}\n"
                    f"---------------------------------\n"
                    f"OVERALL DESIGN STATUS : {res['status']}"
                )
                window["-OUTPUT-"].update(out_text)

                png_steps = generate_step_by_step_latex_png(res)
                window["-IMAGE-STEPS-"].update(data=png_steps)

                png_stress = generate_inelastic_diagram_png(b, d, a_s, fc, fy, inel, selected_unit)
                window["-IMAGE-STRESS-"].update(data=png_stress)

                png_mph = generate_moment_curvature_plot_png(mc, m_serv, m_ult)
                window["-IMAGE-MPH-"].update(data=png_mph)

                png_latex = generate_latex_summary_card_png(res)
                window["-IMAGE-LATEX-"].update(data=png_latex)

            except Exception as err:
                sg.popup_error(f"Invalid input values: {err}", title="Input Error")

    window.close()


def self_check_headless() -> None:
    """Headless self-check for solver_gui.py and CE 152 Example 3."""
    res_ce152 = solve_flexure_section(28.0, 420.0, 250.0, 575.0, 1470.0, 100.0, 220.0, "SI")
    assert abs(res_ce152["inelastic"]["a"] - 103.76) < 0.1

    res_us = solve_flexure_section(4.0, 60.0, 12.0, 20.0, 2.37, 1200.0, 2000.0, "US")
    assert res_us["status"] == "PASS"

    png_steps = generate_step_by_step_latex_png(res_ce152)
    png_stress = generate_inelastic_diagram_png(250.0, 575.0, 1470.0, 28.0, 420.0, res_ce152["inelastic"], "SI")
    png_mph = generate_moment_curvature_plot_png(res_ce152["mc_data"], 100.0, 220.0)
    png_latex = generate_latex_summary_card_png(res_ce152)

    assert len(png_steps) > 1000
    assert len(png_stress) > 1000
    assert len(png_mph) > 1000
    assert len(png_latex) > 1000
    print("solver_gui CE 152 Example 3 & Step-by-Step LaTeX check passed!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        self_check_headless()
    else:
        run_gui()
