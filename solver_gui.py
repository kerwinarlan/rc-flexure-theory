"""NSCP 2015 / ACI 318 RC Flexure Solver GUI with Continuous Fiber M-phi Curves, Parametric Variable Dropdowns, Board Solutions & Multi-Units.

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
    calculate_balanced_condition,
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
    """Calculate elastic (WSD), inelastic (USD), balanced, and moment-curvature parameters per ACI 318 / NSCP 2015."""
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

    # Balanced condition calculations
    bal = calculate_balanced_condition(b, d, fc_prime, fy, units, lambda_factor)

    # Moment-Curvature Curve with continuous fiber integration
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
        "h": h,
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
        "balanced": bal,
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
    """Generate a continuous matplotlib plot highlighting the 3 flexural behavior regions on the M - phi curve."""
    phi_pts = mc_data["phi_pts"]
    m_pts = mc_data["m_pts"]
    phi_cont = mc_data["phi_continuous"]
    m_cont = mc_data["m_continuous"]
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

    # Continuous Backbone plot
    ax.plot(phi_cont, m_cont, "b-", lw=2.2, label="M - ϕ Response")

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


def generate_parametric_moment_curvature_plot_png(res: dict, param_key: str = "Steel Area (As)") -> bytes:
    """Generate a parametric Moment-Curvature plot comparing variations of As, d, f'c, b, or fy."""
    b_base = res["b"]
    d_base = res["d"]
    h_base = res["h"]
    fc_base = res["fc"]
    fy_base = res["fy"]
    as_base = res["as_area"]
    units = res["units"]
    bal = res["balanced"]

    l_unit = "mm²" if units.upper() == "SI" else "in²"
    m_unit = "kN·m" if units.upper() == "SI" else "kip-in"
    phi_unit = "rad/m" if units.upper() == "SI" else "1/in"
    f_unit = "MPa" if units.upper() == "SI" else "ksi"
    d_unit = "mm" if units.upper() == "SI" else "in"

    fig, ax = plt.subplots(figsize=(6.8, 3.2), dpi=100)
    fig.patch.set_facecolor("#FAFAFA")

    if "As" in param_key or "Steel Area" in param_key:
        as_bal = bal["A_s_bal"]
        as_max = bal["A_s_max"]
        as_variations = [
            (as_base * 0.5, f"0.5x As ({as_base*0.5:.2f} {l_unit})", "green", ":"),
            (as_base, f"Current As ({as_base:.2f} {l_unit})", "blue", "-"),
            (as_max, f"As,max ({as_max:.2f} {l_unit})", "purple", "-."),
            (as_base * 1.5, f"1.5x As ({as_base*1.5:.2f} {l_unit})", "orange", "--"),
            (as_bal, f"As,bal ({as_bal:.2f} {l_unit})", "red", "-."),
        ]
        title_str = "Parametric M - ϕ vs Steel Area (As) [Tradeoff: Strength vs Ductility]"
        note_str = "↑ As -> Higher M_n (taller curve), but ↓ phi_u (shorter curvature length = reduced ductility µ_ϕ)"
        for as_val, label, col, ls in as_variations:
            mc = calculate_moment_curvature(b_base, d_base, h_base, as_val, fc_base, fy_base, units)
            ax.plot(mc["phi_continuous"], mc["m_continuous"], color=col, linestyle=ls, lw=1.8,
                    label=f"{label} [µ_ϕ={mc['ductility_ratio']:.1f}]")

    elif "d" in param_key or "Depth" in param_key:
        d_variations = [
            (d_base * 0.8, f"0.8x d ({d_base*0.8:.1f} {d_unit})", "green", ":"),
            (d_base * 0.9, f"0.9x d ({d_base*0.9:.1f} {d_unit})", "cyan", "--"),
            (d_base, f"Current d ({d_base:.1f} {d_unit})", "blue", "-"),
            (d_base * 1.1, f"1.1x d ({d_base*1.1:.1f} {d_unit})", "orange", "-."),
            (d_base * 1.2, f"1.2x d ({d_base*1.2:.1f} {d_unit})", "red", "--"),
        ]
        title_str = "Parametric M - ϕ vs Effective Depth (d) [Moment Arm Scaling]"
        note_str = "↑ Depth d -> Increases moment arm (d - a/2) -> Higher M_n & stiffer elastic cracked slope"
        for d_val, label, col, ls in d_variations:
            h_val = d_val + (65.0 if units.upper() == "SI" else 2.5)
            mc = calculate_moment_curvature(b_base, d_val, h_val, as_base, fc_base, fy_base, units)
            ax.plot(mc["phi_continuous"], mc["m_continuous"], color=col, linestyle=ls, lw=1.8,
                    label=f"{label} [M_n={mc['M_n']:.1f}{m_unit}]")

    elif "f'c" in param_key or "Concrete" in param_key:
        fc_list = [21.0, 28.0, 35.0, 42.0] if units.upper() == "SI" else [3.0, 4.0, 5.0, 6.0]
        colors = ["green", "blue", "orange", "purple"]
        title_str = "Parametric M - ϕ vs Concrete Strength (f'c)"
        note_str = "↑ Concrete f'c -> Reduces stress block depth a = As*fy / (0.85*f'c*b) -> Increases strain margin & ductility"
        for idx, fc_val in enumerate(fc_list):
            mc = calculate_moment_curvature(b_base, d_base, h_base, as_base, fc_val, fy_base, units)
            ax.plot(mc["phi_continuous"], mc["m_continuous"], color=colors[idx % len(colors)], lw=1.8,
                    label=f"f'c={fc_val:.0f} {f_unit} [µ_ϕ={mc['ductility_ratio']:.1f}]")

    elif "b" in param_key or "Width" in param_key:
        b_variations = [
            (b_base * 0.8, f"0.8x b ({b_base*0.8:.0f} {d_unit})", "green", ":"),
            (b_base, f"Current b ({b_base:.0f} {d_unit})", "blue", "-"),
            (b_base * 1.2, f"1.2x b ({b_base*1.2:.0f} {d_unit})", "orange", "--"),
            (b_base * 1.5, f"1.5x b ({b_base*1.5:.0f} {d_unit})", "red", "-."),
        ]
        title_str = "Parametric M - ϕ vs Beam Width (b)"
        note_str = "↑ Beam Width (b) -> Increases concrete compression area -> Reduces stress block depth a & neutral axis c"
        for b_val, label, col, ls in b_variations:
            mc = calculate_moment_curvature(b_val, d_base, h_base, as_base, fc_base, fy_base, units)
            ax.plot(mc["phi_continuous"], mc["m_continuous"], color=col, linestyle=ls, lw=1.8,
                    label=f"{label} [M_n={mc['M_n']:.1f}{m_unit}]")

    else:  # fy
        fy_list = [280.0, 420.0, 520.0] if units.upper() == "SI" else [40.0, 60.0, 75.0]
        colors = ["green", "blue", "red"]
        title_str = "Parametric M - ϕ vs Steel Yield Strength (fy)"
        note_str = "↑ Yield fy -> Increases yield strain eps_y = fy/E_s & yield moment M_y"
        for idx, fy_val in enumerate(fy_list):
            mc = calculate_moment_curvature(b_base, d_base, h_base, as_base, fc_base, fy_val, units)
            ax.plot(mc["phi_continuous"], mc["m_continuous"], color=colors[idx % len(colors)], lw=1.8,
                    label=f"fy={fy_val:.0f} {f_unit} [M_n={mc['M_n']:.1f}{m_unit}]")

    ax.set_title(title_str, fontsize=9, fontweight="bold")
    ax.set_xlabel(f"Curvature ϕ ({phi_unit})", fontsize=8)
    ax.set_ylabel(f"Flexural Moment M ({m_unit})", fontsize=8)
    ax.grid(True, linestyle="--", alpha=0.5)

    ax.text(0.02, 0.92, note_str, transform=ax.transAxes, fontsize=7.2, color="#0D47A1", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#E3F2FD", edgecolor="#1E88E5", alpha=0.9))

    ax.legend(fontsize=6.5, loc="lower right", framealpha=0.9)

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)
    return buf.getvalue()


def generate_step_by_step_latex_png(res: dict) -> bytes:
    """Generate a board-exam aligned step-by-step LaTeX solution card with high readability."""
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

    fig, ax = plt.subplots(figsize=(7.5, 5.2), dpi=120)
    fig.patch.set_facecolor("#FAFAFA")
    ax.axis("off")

    ax.text(0.02, 0.96, "CE BOARD EXAM / NSCP 2015 STEP-BY-STEP SOLUTION", fontsize=10.5, fontweight="bold", color="#0D47A1")

    steps = [
        ("STEP 1: Material & Section Parameters", [
            (r"$f'_c$", r"$= %.1f \text{ %s}$" % (fc, f_unit), f"(NSCP 2015 Table 422.2.2.4.3 -> beta_1 = {beta1:.2f})"),
            (r"$\epsilon_y$", r"$= \frac{f_y}{E_s} = \frac{%.1f}{%.0f} = %.5f$" % (fy, e_s_val, eps_y), "(NSCP 2015 Sec 420.2.2.1)"),
        ]),
        ("STEP 2: Compression Stress Block Depth (a)", [
            (r"$C$", r"$= T$", "(Equilibrium)"),
            (r"$0.85 f'_c b a$", r"$= A_s f_y$", "(NSCP 2015 Sec 422.2.2)"),
            (r"$a$", r"$= \frac{A_s f_y}{0.85 f'_c b}$", ""),
            ("", r"$= \frac{%.1f \times %.1f}{0.85 \times %.1f \times %.1f}$" % (a_s, fy, fc, b), ""),
            (r"$a$", r"$= \mathbf{%.2f \text{ %s}}$" % (a, l_unit), "[ANSWER: STRESS BLOCK DEPTH]"),
        ]),
        ("STEP 3: Neutral Axis Depth (c) & Strain Verification", [
            (r"$c$", r"$= \frac{a}{\beta_1} = \frac{%.2f}{%.2f}$" % (a, beta1), ""),
            (r"$c$", r"$= \mathbf{%.2f \text{ %s}}$" % (c, l_unit), "(NSCP 2015 Table 422.2.2.4.3)"),
            (r"$\epsilon_s$", r"$= 0.003 \cdot \frac{d - c}{c}$", ""),
            ("", r"$= 0.003 \cdot \frac{%.1f - %.2f}{%.2f}$" % (d, c, c), ""),
            (r"$\epsilon_s$", r"$= %.5f \geq %.5f$" % (eps_s, eps_y), "(Steel Yielded & Tension-Controlled, phi = 0.90)"),
        ]),
        ("STEP 4: Nominal & Design Flexural Capacities", [
            (r"$M_n$", r"$= A_s f_y \left(d - \frac{a}{2}\right)$", "(NSCP 2015 Sec 422.2)"),
            ("", r"$= %.1f \times %.1f \times \left(%.1f - \frac{%.2f}{2}\right) \times 10^{-6}$" % (a_s, fy, d, a) if is_si else r"$= %.2f \times %.1f \times \left(%.1f - \frac{%.2f}{2}\right)$" % (a_s, fy, d, a), ""),
            (r"$M_n$", r"$= \mathbf{%.1f \text{ %s}}$" % (m_n, m_unit), "[NOMINAL MOMENT]"),
            (r"$\phi M_n$", r"$= %.2f \times %.1f = \mathbf{%.1f \text{ %s}}$" % (phi, m_n, phi_m_n, m_unit), "[DESIGN CAPACITY - NSCP 2015 Sec 421.2]"),
        ]),
    ]

    y_pos = 0.89
    for header, lines in steps:
        ax.text(0.02, y_pos, header, fontsize=8.8, fontweight="bold", color="#1A237E")
        y_pos -= 0.038
        for lhs, rhs, cite in lines:
            if lhs:
                ax.text(0.18, y_pos, lhs, fontsize=8.2, color="#0D47A1", ha="right")
            if rhs:
                is_result = "[ANSWER" in cite or "[NOMINAL" in cite or "[DESIGN" in cite or "%.2f" % a in rhs or "%.1f" % phi_m_n in rhs
                col = "#B71C1C" if is_result else "#1A237E"
                ax.text(0.20, y_pos, rhs, fontsize=8.2, color=col, ha="left")
            if cite:
                col_cite = "#B71C1C" if "[" in cite else "#5C6BC0"
                ax.text(0.98, y_pos, cite, fontsize=7.2, fontweight="bold" if "[" in cite else "normal", color=col_cite, ha="right")
            y_pos -= 0.036
        y_pos -= 0.012

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
    plt.close(fig)
    return buf.getvalue()


def generate_latex_summary_card_png(res: dict) -> bytes:
    """Generate a step-by-step LaTeX formula summary card rendering publication-quality math."""
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

    preset_options = [
        "Custom Inputs",
        "CE 152 Example 3 (b=250mm, d=575mm, f'c=28MPa, fy=420MPa, As=1470mm²)",
        "CE 152 Slide 35 Balanced Condition (b=250mm, d=575mm, f'c=28MPa, fy=420MPa)",
        "CE 152 Slide 5425 (b=12in, d=20in, f'c=4ksi, fy=60ksi, As=2.50in²)",
    ]

    default_preset = "Custom Inputs"
    if pv.get("preset") == "ex3":
        default_preset = preset_options[1]
    elif pv.get("preset") == "slide35":
        default_preset = preset_options[2]
    elif pv.get("preset") == "slide5425":
        default_preset = preset_options[3]

    plot_view_options = [
        "Step-by-Step Board Solution",
        "Parametric M - ϕ vs Variable",
        "Whitney Stress UDL Diagram",
        "3-Region Moment - Curvature (M - ϕ)",
        "LaTeX Math Derivation",
    ]

    param_var_options = [
        "Steel Area (As)",
        "Effective Depth (d)",
        "Concrete Strength (f'c)",
        "Beam Width (b)",
        "Steel Yield Strength (fy)",
    ]

    layout = [
        [sg.Text("NSCP 2015 / ACI 318 RC Flexure Solver (LaTeX & Multi-Units)", font=("Helvetica", 12, "bold"))],
        [
            sg.Text("Unit System:", font=("Helvetica", 9, "bold")),
            sg.Combo(["US Customary (kip-in, 1/in, ksi, in)", "SI Metric (kN·m, rad/m, MPa, mm)"],
                     default_value="US Customary (kip-in, 1/in, ksi, in)" if not is_si else "SI Metric (kN·m, rad/m, MPa, mm)",
                     key="-UNITS-", enable_events=True, readonly=True),
            sg.Text("  Preset Examples:", font=("Helvetica", 9, "bold")),
            sg.Combo(preset_options, default_value=default_preset, key="-PRESET-", enable_events=True, readonly=True),
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
        # Output Results and Interactive Plot Selector
        [
            sg.Column(
                [
                    [sg.Text("Analysis Results", font=("Helvetica", 10, "bold"))],
                    [sg.Multiline("", key="-OUTPUT-", size=(44, 16), disabled=True, font=("Courier", 9))],
                ]
            ),
            sg.Column(
                [
                    [
                        sg.Text("Diagram View:", font=("Helvetica", 9, "bold")),
                        sg.Combo(plot_view_options, default_value=plot_view_options[0], key="-PLOT-VIEW-", enable_events=True, readonly=True),
                        sg.Text(" Param Variable:", font=("Helvetica", 9, "bold")),
                        sg.Combo(param_var_options, default_value=param_var_options[0], key="-PARAM-VAR-", enable_events=True, readonly=True),
                    ],
                    [sg.Image(key="-IMAGE-DISPLAY-", size=(460, 270))],
                ]
            ),
        ],
    ]

    return sg.Window("NSCP 2015 / ACI 318 RC Flexure Solver", layout, finalize=True)


def run_gui() -> None:
    """Run event loop."""
    window = create_window("US")
    cached_data = {}

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break

        if event == "-UNITS-":
            selected_unit = "SI" if "SI" in values["-UNITS-"] else "US"
            window.close()
            window = create_window(selected_unit)
            cached_data = {}
            continue

        if event == "-PRESET-":
            if "CE 152 Example 3" in values["-PRESET-"]:
                pv = {"fc": "28.0", "fy": "420.0", "b": "250.0", "d": "575.0", "as": "1470.0", "mserv": "100.0", "mult": "220.0", "preset": "ex3"}
                window.close()
                window = create_window("SI", preset_vals=pv)
                cached_data = {}
            elif "CE 152 Slide 35" in values["-PRESET-"]:
                pv = {"fc": "28.0", "fy": "420.0", "b": "250.0", "d": "575.0", "as": "4072.9", "mserv": "100.0", "mult": "220.0", "preset": "slide35"}
                window.close()
                window = create_window("SI", preset_vals=pv)
                cached_data = {}
            elif "CE 152 Slide 5425" in values["-PRESET-"]:
                pv = {"fc": "4.0", "fy": "60.0", "b": "12.0", "d": "20.0", "as": "2.50", "mserv": "1200.0", "mult": "2000.0", "preset": "slide5425"}
                window.close()
                window = create_window("US", preset_vals=pv)
                cached_data = {}
            continue

        if event in ("-PLOT-VIEW-", "-PARAM-VAR-") and cached_data:
            selected_view = values["-PLOT-VIEW-"]
            if selected_view == "Parametric M - ϕ vs Variable":
                param_var = values["-PARAM-VAR-"]
                png_bytes = generate_parametric_moment_curvature_plot_png(cached_data["res"], param_var)
                window["-IMAGE-DISPLAY-"].update(data=png_bytes)
            else:
                if selected_view in cached_data["images"]:
                    window["-IMAGE-DISPLAY-"].update(data=cached_data["images"][selected_view])
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
                bal = res["balanced"]
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
                    f"--- BALANCED CONDITION (SLIDE 35) ---\n"
                    f"Balanced NA Depth c_bal: {bal['c_bal']:.2f} {l_unit}\n"
                    f"Balanced Block a_bal : {bal['a_bal']:.2f} {l_unit}\n"
                    f"Balanced Steel As_bal: {bal['A_s_bal']:.1f} {l_unit}²\n"
                    f"Balanced Ratio rho_b : {bal['rho_b']*100:.2f}%\n"
                    f"Max Tens-Ctrl rho_max : {bal['rho_max']*100:.2f}%\n\n"
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
                    f"Nominal Cap. (M_n)    : {inel['M_n']:.1f} {m_unit}\n"
                    f"Design Cap. (phi*M_n) : {inel['phi_M_n']:.1f} {m_unit} ({res['util_ult']*100:.1f}%)\n"
                    f"---------------------------------\n"
                    f"OVERALL DESIGN STATUS : {res['status']}"
                )
                window["-OUTPUT-"].update(out_text)

                images = {
                    "Step-by-Step Board Solution": generate_step_by_step_latex_png(res),
                    "Whitney Stress UDL Diagram": generate_inelastic_diagram_png(b, d, a_s, fc, fy, inel, selected_unit),
                    "3-Region Moment - Curvature (M - ϕ)": generate_moment_curvature_plot_png(mc, m_serv, m_ult),
                    "LaTeX Math Derivation": generate_latex_summary_card_png(res),
                }

                cached_data = {"res": res, "images": images}

                selected_view = values.get("-PLOT-VIEW-", "Step-by-Step Board Solution")
                if selected_view == "Parametric M - ϕ vs Variable":
                    param_var = values.get("-PARAM-VAR-", "Steel Area (As)")
                    png_bytes = generate_parametric_moment_curvature_plot_png(res, param_var)
                else:
                    png_bytes = images.get(selected_view, images["Step-by-Step Board Solution"])

                window["-IMAGE-DISPLAY-"].update(data=png_bytes)

            except Exception as err:
                sg.popup_error(f"Invalid input values: {err}", title="Input Error")

    window.close()


def self_check_headless() -> None:
    """Headless self-check for solver_gui.py, CE 152 Example 3, Slide 35, and Slide 5425."""
    res_ce152 = solve_flexure_section(28.0, 420.0, 250.0, 575.0, 1470.0, 100.0, 220.0, "SI")
    assert abs(res_ce152["inelastic"]["a"] - 103.76) < 0.1
    assert abs(res_ce152["balanced"]["c_bal"] - 338.24) < 0.1

    res_5425 = solve_flexure_section(4.0, 60.0, 12.0, 20.0, 2.50, 1200.0, 2000.0, "US")
    assert res_5425["status"] == "PASS"

    png_steps = generate_step_by_step_latex_png(res_ce152)
    png_as_param = generate_parametric_moment_curvature_plot_png(res_ce152)
    png_stress = generate_inelastic_diagram_png(250.0, 575.0, 1470.0, 28.0, 420.0, res_ce152["inelastic"], "SI")
    png_mph = generate_moment_curvature_plot_png(res_ce152["mc_data"], 100.0, 220.0)
    png_latex = generate_latex_summary_card_png(res_ce152)

    assert len(png_steps) > 1000
    assert len(png_as_param) > 1000
    assert len(png_stress) > 1000
    assert len(png_mph) > 1000
    assert len(png_latex) > 1000
    print("solver_gui CE 152 Slide 5425 & Continuous Fiber M-phi check passed!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        self_check_headless()
    else:
        run_gui()
