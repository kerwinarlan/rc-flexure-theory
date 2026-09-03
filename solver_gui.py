"""NSCP 2015 RC Flexure Solver GUI.

Follows Engr. Jaydee Lucero's FreeSimpleGUI 5-step template pattern for structural engineering tools.
"""

import sys
import FreeSimpleGUI as sg
from flexure import (
    calculate_beta_1,
    calculate_concrete_modulus,
    calculate_cracked_moment_of_inertia,
    calculate_modular_ratio,
    calculate_neutral_axis_depth,
    calculate_service_stresses,
)


def solve_flexure_section(
    fc_prime: float, fy: float, b: float, d: float, as_area: float, m_serv_knm: float
) -> dict[str, float | str]:
    """Calculate all elastic section and flexural stress parameters per NSCP 2015."""
    if fc_prime <= 0 or fy <= 0 or b <= 0 or d <= 0 or as_area <= 0 or m_serv_knm < 0:
        raise ValueError("Input parameters must be positive numbers.")

    ec = calculate_concrete_modulus(fc_prime)
    n = calculate_modular_ratio(fc_prime)
    beta1 = calculate_beta_1(fc_prime)
    x = calculate_neutral_axis_depth(b, d, as_area, n)

    q_c = (b * x) * (x / 2.0)
    q_s = (n * as_area) * (d - x)
    i_cr = calculate_cracked_moment_of_inertia(b, d, as_area, n, x)

    m_serv_nmm = m_serv_knm * 1e6  # Convert kN*m to N*mm
    fc, fs = calculate_service_stresses(m_serv_nmm, b, d, as_area, n)

    fc_allow = 0.45 * fc_prime  # NSCP 2015 allowable concrete stress
    fs_allow = 0.50 * fy  # NSCP 2015 allowable steel stress

    util_c = fc / fc_allow if fc_allow > 0 else 0.0
    util_s = fs / fs_allow if fs_allow > 0 else 0.0

    status = "PASS" if util_c <= 1.0 and util_s <= 1.0 else "RESIZE SECTION"

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
        "status": status,
    }


def create_window() -> sg.Window:
    """Build the FreeSimpleGUI layout using Engr. Lucero's signature structure."""
    sg.theme("SystemDefault")

    layout = [
        [sg.Text("NSCP 2015 Reinforced Concrete Flexure Solver", font=("Helvetica", 12, "bold"))],
        [sg.Text("Working Stress Design (WSD) / Elastic Transformed Section", font=("Helvetica", 9, "italic"))],
        [sg.Separator()],
        # Inputs
        [
            sg.Text("Concrete strength", size=(18, 1)),
            sg.Text("f'c =", size=(5, 1), justification="r"),
            sg.Input("28.0", key="-FC-", size=(10, 1)),
            sg.Text("MPa", size=(5, 1)),
        ],
        [
            sg.Text("Steel yield strength", size=(18, 1)),
            sg.Text("fy =", size=(5, 1), justification="r"),
            sg.Input("420.0", key="-FY-", size=(10, 1)),
            sg.Text("MPa", size=(5, 1)),
        ],
        [
            sg.Text("Beam width", size=(18, 1)),
            sg.Text("b =", size=(5, 1), justification="r"),
            sg.Input("300.0", key="-B-", size=(10, 1)),
            sg.Text("mm", size=(5, 1)),
        ],
        [
            sg.Text("Effective depth", size=(18, 1)),
            sg.Text("d =", size=(5, 1), justification="r"),
            sg.Input("500.0", key="-D-", size=(10, 1)),
            sg.Text("mm", size=(5, 1)),
        ],
        [
            sg.Text("Tension steel area", size=(18, 1)),
            sg.Text("As =", size=(5, 1), justification="r"),
            sg.Input("1500.0", key="-AS-", size=(10, 1)),
            sg.Text("mm²", size=(5, 1)),
        ],
        [
            sg.Text("Service moment", size=(18, 1)),
            sg.Text("M =", size=(5, 1), justification="r"),
            sg.Input("100.0", key="-M-", size=(10, 1)),
            sg.Text("kN·m", size=(5, 1)),
        ],
        [sg.Button("Calculate", button_color=("white", "navy")), sg.Button("Exit")],
        [sg.Separator()],
        # Results
        [sg.Text("Output Results (NSCP 2015)", font=("Helvetica", 10, "bold"))],
        [sg.Multiline("", key="-OUTPUT-", size=(52, 12), disabled=True, font=("Courier", 9))],
    ]

    return sg.Window("NSCP 2015 RC Flexure Solver", layout, finalize=True)


def run_gui() -> None:
    """Run event loop."""
    window = create_window()

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break

        if event == "Calculate":
            try:
                fc = float(values["-FC-"])
                fy = float(values["-FY-"])
                b = float(values["-B-"])
                d = float(values["-D-"])
                a_s = float(values["-AS-"])
                m_serv = float(values["-M-"])

                res = solve_flexure_section(fc, fy, b, d, a_s, m_serv)

                out_text = (
                    f"Concrete Modulus (E_c) : {res['E_c']:.2f} MPa\n"
                    f"Modular Ratio (n)     : {res['n']:.2f}\n"
                    f"Stress Block (beta_1) : {res['beta_1']:.2f}\n"
                    f"Neutral Axis Depth (x): {res['x']:.2f} mm\n"
                    f"First Moments (Q_c)   : {res['Q_c']:.0f} mm³\n"
                    f"First Moments (Q_s)   : {res['Q_s']:.0f} mm³\n"
                    f"Cracked Moment (I_cr) : {res['I_cr']:.3e} mm⁴\n"
                    f"-----------------------------------------\n"
                    f"Concrete Stress (f_c) : {res['f_c']:.2f} MPa / {res['f_c_allow']:.2f} MPa ({res['util_c']*100:.1f}%)\n"
                    f"Steel Stress (f_s)    : {res['f_s']:.2f} MPa / {res['f_s_allow']:.2f} MPa ({res['util_s']*100:.1f}%)\n"
                    f"Design Status         : {res['status']}"
                )
                window["-OUTPUT-"].update(out_text)

            except Exception as err:
                sg.popup_error(f"Invalid input values: {err}", title="Input Error")

    window.close()


def self_check_headless() -> None:
    """Headless self-check for solver_gui.py."""
    res = solve_flexure_section(28.0, 420.0, 300.0, 500.0, 1500.0, 100.0)
    assert res["status"] == "PASS"
    assert abs(res["E_c"] - 24870.06) < 1.0
    assert abs(res["n"] - 8.04) < 0.1
    print("solver_gui headless check passed!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        self_check_headless()
    else:
        run_gui()
