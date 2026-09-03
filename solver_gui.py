"""NSCP 2015 RC Flexure Solver GUI with Inelastic Stress Diagrams.

Follows Engr. Jaydee Lucero's FreeSimpleGUI 5-step template pattern for structural engineering tools.
"""

import io
import sys
import FreeSimpleGUI as sg
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for PNG generation
import matplotlib.pyplot as plt

from flexure import (
    calculate_beta_1,
    calculate_concrete_modulus,
    calculate_cracked_moment_of_inertia,
    calculate_inelastic_capacity,
    calculate_modular_ratio,
    calculate_neutral_axis_depth,
    calculate_service_stresses,
)


def solve_flexure_section(
    fc_prime: float, fy: float, b: float, d: float, as_area: float, m_serv_knm: float, m_ult_knm: float
) -> dict[str, float | str | dict]:
    """Calculate elastic (WSD) and inelastic (USD) flexural parameters per NSCP 2015."""
    if fc_prime <= 0 or fy <= 0 or b <= 0 or d <= 0 or as_area <= 0 or m_serv_knm < 0 or m_ult_knm < 0:
        raise ValueError("Input parameters must be positive numbers.")

    # Elastic WSD calculations
    ec = calculate_concrete_modulus(fc_prime)
    n = calculate_modular_ratio(fc_prime)
    beta1 = calculate_beta_1(fc_prime)
    x = calculate_neutral_axis_depth(b, d, as_area, n)

    q_c = (b * x) * (x / 2.0)
    q_s = (n * as_area) * (d - x)
    i_cr = calculate_cracked_moment_of_inertia(b, d, as_area, n, x)

    m_serv_nmm = m_serv_knm * 1e6
    fc, fs = calculate_service_stresses(m_serv_nmm, b, d, as_area, n)
    fc_allow = 0.45 * fc_prime
    fs_allow = 0.50 * fy

    util_c = fc / fc_allow if fc_allow > 0 else 0.0
    util_s = fs / fs_allow if fs_allow > 0 else 0.0

    # Inelastic USD calculations
    inelastic = calculate_inelastic_capacity(b, d, as_area, fc_prime, fy)
    util_ult = m_ult_knm / inelastic["phi_M_n_knm"] if inelastic["phi_M_n_knm"] > 0 else 0.0

    status = (
        "PASS"
        if util_c <= 1.0 and util_s <= 1.0 and util_ult <= 1.0
        else "RESIZE SECTION"
    )

    return {
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
        "status": status,
    }


def generate_inelastic_diagram_png(
    b: float, d: float, as_area: float, fc_prime: float, fy: float, inelastic: dict
) -> bytes:
    """Generate a 3-panel matplotlib diagram of the cracked section with inelastic stresses."""
    c = float(inelastic["c"])
    a = float(inelastic["a"])
    eps_s = float(inelastic["eps_s"])
    f_s = float(inelastic["f_s"])
    h = d + 65.0  # Total section depth estimate

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(7.2, 3.2), dpi=100)
    fig.patch.set_facecolor("#FAFAFA")

    # Panel 1: Cross Section Geometry
    ax1.set_title("Beam Section", fontsize=10, fontweight="bold")
    ax1.plot([0, b, b, 0, 0], [0, 0, -h, -h, 0], "k-", lw=1.5)
    # Shaded Whitney stress block
    ax1.fill_between([0, b], 0, -a, color="#FFCC80", alpha=0.7, label=f"Stress Block (a={a:.1f}mm)")
    # Neutral axis line
    ax1.axhline(-c, color="red", linestyle="--", lw=1.2, label=f"N.A. (c={c:.1f}mm)")
    # Rebar circles
    n_bars = 3
    xs = [b * (i + 1) / (n_bars + 1) for i in range(n_bars)]
    ax1.scatter(xs, [-d] * n_bars, color="black", s=60, zorder=5, label="Steel Rebar")
    ax1.set_xlim(-b * 0.2, b * 1.2)
    ax1.set_ylim(-h - 10, 10)
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.legend(loc="lower right", fontsize=7, framealpha=0.8)

    # Panel 2: Inelastic Strain Profile
    ax2.set_title("Strain Profile (ε)", fontsize=10, fontweight="bold")
    ax2.axvline(0, color="gray", lw=0.8)
    ax2.axhline(-c, color="red", linestyle="--", lw=1.0)
    # Strain line: top eps_u = 0.003 (compression left), bottom eps_s (tension right)
    ax2.plot([-0.003, eps_s], [0, -d], "b-o", lw=1.8, ms=4)
    ax2.fill_betweenx([0, -c], 0, [-0.003, 0], color="blue", alpha=0.15)
    ax2.fill_betweenx([-c, -d], 0, [0, eps_s], color="red", alpha=0.15)
    ax2.text(-0.003, 5, "εu=0.003", fontsize=8, color="blue", ha="center")
    ax2.text(eps_s, -d - 15, f"εs={eps_s:.4f}", fontsize=8, color="red", ha="center")
    ax2.set_ylim(-h - 10, 10)
    ax2.axis("off")

    # Panel 3: Inelastic Stress Profile & Force Vectors
    ax3.set_title("Inelastic Stress & Forces", fontsize=10, fontweight="bold")
    ax3.axhline(-c, color="red", linestyle="--", lw=1.0)
    # Stress block representation (0.85 f'c)
    stress_mag = 0.85 * fc_prime
    ax3.plot([0, -stress_mag, -stress_mag, 0], [0, 0, -a, -a], "orange", lw=1.5)
    ax3.fill_betweenx([0, -a], 0, -stress_mag, color="orange", alpha=0.3)
    # Concrete Resultant Force C
    ax3.annotate(
        "C = 0.85f'c·b·a",
        xy=(-stress_mag / 2, -a / 2),
        xytext=(-stress_mag * 1.2, -a / 2),
        arrowprops=dict(arrowstyle="->", color="darkorange", lw=1.5),
        fontsize=7,
        fontweight="bold",
        color="darkorange",
        ha="right",
    )
    # Steel Tension Force T
    ax3.annotate(
        "T = As·fs",
        xy=(0, -d),
        xytext=(stress_mag * 0.8, -d),
        arrowprops=dict(arrowstyle="->", color="red", lw=1.5),
        fontsize=7,
        fontweight="bold",
        color="red",
        ha="left",
    )
    ax3.set_ylim(-h - 10, 10)
    ax3.axis("off")

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)
    return buf.getvalue()


def create_window() -> sg.Window:
    """Build the FreeSimpleGUI layout using Engr. Lucero's signature structure."""
    sg.theme("SystemDefault")

    layout = [
        [sg.Text("NSCP 2015 Reinforced Concrete Flexure Solver", font=("Helvetica", 12, "bold"))],
        [sg.Text("Elastic (WSD) & Inelastic (USD Whitney Stress Block) Analysis", font=("Helvetica", 9, "italic"))],
        [sg.HorizontalSeparator()],
        # Input Section
        [
            sg.Text("Concrete f'c =", size=(14, 1)),
            sg.Input("28.0", key="-FC-", size=(8, 1)),
            sg.Text("MPa", size=(4, 1)),
            sg.Text("Steel fy =", size=(10, 1)),
            sg.Input("420.0", key="-FY-", size=(8, 1)),
            sg.Text("MPa", size=(4, 1)),
        ],
        [
            sg.Text("Beam width b =", size=(14, 1)),
            sg.Input("300.0", key="-B-", size=(8, 1)),
            sg.Text("mm", size=(4, 1)),
            sg.Text("Depth d =", size=(10, 1)),
            sg.Input("500.0", key="-D-", size=(8, 1)),
            sg.Text("mm", size=(4, 1)),
        ],
        [
            sg.Text("Steel area As =", size=(14, 1)),
            sg.Input("1500.0", key="-AS-", size=(8, 1)),
            sg.Text("mm²", size=(4, 1)),
            sg.Text("Service M =", size=(10, 1)),
            sg.Input("100.0", key="-MSERV-", size=(8, 1)),
            sg.Text("kN·m", size=(4, 1)),
        ],
        [
            sg.Text("Factored Mu =", size=(14, 1)),
            sg.Input("220.0", key="-MULT-", size=(8, 1)),
            sg.Text("kN·m", size=(4, 1)),
        ],
        [sg.Button("Calculate & Plot", button_color=("white", "navy")), sg.Button("Exit")],
        [sg.HorizontalSeparator()],
        # Output Results and Diagram
        [
            sg.Column(
                [
                    [sg.Text("Analysis Results (NSCP 2015)", font=("Helvetica", 10, "bold"))],
                    [sg.Multiline("", key="-OUTPUT-", size=(45, 15), disabled=True, font=("Courier", 9))],
                ]
            ),
            sg.Column(
                [
                    [sg.Text("Cracked Section & Inelastic Stress Diagrams", font=("Helvetica", 10, "bold"))],
                    [sg.Image(key="-IMAGE-", size=(450, 260))],
                ]
            ),
        ],
    ]

    return sg.Window("NSCP 2015 RC Flexure Solver", layout, finalize=True)


def run_gui() -> None:
    """Run event loop."""
    window = create_window()

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break

        if event == "Calculate & Plot":
            try:
                fc = float(values["-FC-"])
                fy = float(values["-FY-"])
                b = float(values["-B-"])
                d = float(values["-D-"])
                a_s = float(values["-AS-"])
                m_serv = float(values["-MSERV-"])
                m_ult = float(values["-MULT-"])

                res = solve_flexure_section(fc, fy, b, d, a_s, m_serv, m_ult)
                inel = res["inelastic"]

                out_text = (
                    f"--- ELASTIC (WSD) PARAMETERS ---\n"
                    f"Concrete Modulus (E_c) : {res['E_c']:.2f} MPa\n"
                    f"Modular Ratio (n)     : {res['n']:.2f}\n"
                    f"Elastic NA Depth (x)  : {res['x']:.2f} mm\n"
                    f"Cracked Inertia (I_cr): {res['I_cr']:.3e} mm⁴\n"
                    f"Service f_c / Allow   : {res['f_c']:.2f} / {res['f_c_allow']:.2f} MPa ({res['util_c']*100:.1f}%)\n"
                    f"Service f_s / Allow   : {res['f_s']:.2f} / {res['f_s_allow']:.2f} MPa ({res['util_s']*100:.1f}%)\n\n"
                    f"--- INELASTIC (USD) CAPACITY ---\n"
                    f"Inelastic NA Depth (c): {inel['c']:.2f} mm\n"
                    f"Stress Block Depth (a): {inel['a']:.2f} mm\n"
                    f"Steel Strain (eps_s)  : {inel['eps_s']:.5f}\n"
                    f"Phi Factor (phi)      : {inel['phi']:.2f}\n"
                    f"Nominal Cap. (M_n)    : {inel['M_n_knm']:.2f} kN·m\n"
                    f"Design Cap. (phi*M_n) : {inel['phi_M_n_knm']:.2f} kN·m\n"
                    f"Factored Demand (M_u) : {m_ult:.2f} kN·m ({res['util_ult']*100:.1f}%)\n"
                    f"Failure Mode          : {inel['failure_mode']}\n"
                    f"---------------------------------\n"
                    f"OVERALL DESIGN STATUS : {res['status']}"
                )
                window["-OUTPUT-"].update(out_text)

                png_bytes = generate_inelastic_diagram_png(b, d, a_s, fc, fy, inel)
                window["-IMAGE-"].update(data=png_bytes)

            except Exception as err:
                sg.popup_error(f"Invalid input values: {err}", title="Input Error")

    window.close()


def self_check_headless() -> None:
    """Headless self-check for solver_gui.py."""
    res = solve_flexure_section(28.0, 420.0, 300.0, 500.0, 1500.0, 100.0, 220.0)
    assert res["status"] == "PASS"
    assert abs(res["E_c"] - 24870.06) < 1.0
    assert res["inelastic"]["phi_M_n_knm"] > 220.0
    png = generate_inelastic_diagram_png(300.0, 500.0, 1500.0, 28.0, 420.0, res["inelastic"])
    assert len(png) > 1000
    print("solver_gui headless check passed!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        self_check_headless()
    else:
        run_gui()
