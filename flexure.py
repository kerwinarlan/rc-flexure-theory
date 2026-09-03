import math

# Provenance parameters [NSCP 2015 Section 420.2.2.1]
E_S_GIVEN: float = 200000.0  # MPa [GIVEN] Steel elastic modulus
EPS_U_GIVEN: float = 0.003  # [GIVEN: NSCP 2015 Section 422.2.2.1] Ultimate concrete strain


def calculate_concrete_modulus(f_c_prime: float) -> float:
    """Calculate concrete elastic modulus E_c in MPa.
    
    Formula: E_c = 4700 * sqrt(f'_c) [CORRELATED: NSCP 2015 Sec 419.2.2.1]
    """
    if f_c_prime <= 0:
        raise ValueError("f'_c must be positive.")
    return 4700.0 * math.sqrt(f_c_prime)


def calculate_modular_ratio(f_c_prime: float, e_s: float = E_S_GIVEN) -> float:
    """Calculate modular ratio n = E_s / E_c.
    
    [CALCULATED: NSCP 2015 Sec 424.5.2]
    """
    e_c = calculate_concrete_modulus(f_c_prime)
    return e_s / e_c


def calculate_modulus_of_rupture(f_c_prime: float) -> float:
    """Calculate concrete modulus of rupture f_r in MPa.
    
    Formula: f_r = 0.62 * sqrt(f'_c) [CORRELATED: NSCP 2015 Sec 419.2.3.1]
    """
    return 0.62 * math.sqrt(f_c_prime)


def calculate_beta_1(f_c_prime: float) -> float:
    """Calculate Whitney stress block factor beta_1.
    
    [CALCULATED: NSCP 2015 Sec 422.2.2.4]
    """
    if f_c_prime <= 28.0:
        return 0.85
    beta = 0.85 - 0.05 * (f_c_prime - 28.0) / 7.0
    return max(0.65, min(0.85, beta))


def calculate_neutral_axis_depth(
    b: float, d: float, a_s: float, n: float
) -> float:
    """Calculate elastic neutral axis depth x using first moment of area equilibrium.
    
    Equilibrium formula: Q_c = Q_s -> A_c * x_c = n * A_s * x_s [CALCULATED: NSCP 2015 Sec 424.5]
    0.5 * b * x^2 = n * A_s * (d - x)
    """
    if b <= 0 or d <= 0 or a_s <= 0 or n <= 0:
        raise ValueError("All input dimensions and parameters must be positive.")
    
    n_as = n * a_s
    return (-n_as + math.sqrt(n_as**2 + 2.0 * b * n_as * d)) / b


def calculate_cracked_moment_of_inertia(
    b: float, d: float, a_s: float, n: float, x: float
) -> float:
    """Calculate cracked transformed section moment of inertia I_cr in mm^4.
    
    Formula: I_cr = (1/3) * b * x^3 + n * A_s * (d - x)^2 [CALCULATED: NSCP 2015 Sec 424.5]
    """
    return (1.0 / 3.0) * b * (x**3) + n * a_s * ((d - x) ** 2)


def calculate_service_stresses(
    m_service: float, b: float, d: float, a_s: float, n: float
) -> tuple[float, float]:
    """Calculate working stresses f_c and f_s under service moment M in N*mm.
    
    Returns (f_c, f_s) in MPa [CALCULATED: NSCP 2015 Sec 424.5]
    """
    x = calculate_neutral_axis_depth(b, d, a_s, n)
    i_cr = calculate_cracked_moment_of_inertia(b, d, a_s, n, x)
    f_c = (m_service * x) / i_cr
    f_s = (n * m_service * (d - x)) / i_cr
    return f_c, f_s


def calculate_inelastic_neutral_axis(
    b: float, d: float, a_s: float, fc_prime: float, fy: float, e_s: float = E_S_GIVEN
) -> tuple[float, float, float, float]:
    """Calculate inelastic neutral axis depth c, stress block a, steel stress f_s, and strain eps_s.
    
    [CALCULATED: NSCP 2015 Sec 422.2]
    """
    beta1 = calculate_beta_1(fc_prime)
    eps_y = fy / e_s

    # Assume steel yields
    a_yield = (a_s * fy) / (0.85 * fc_prime * b)
    c_yield = a_yield / beta1
    eps_s_yield = EPS_U_GIVEN * (d - c_yield) / c_yield

    if eps_s_yield >= eps_y:
        return c_yield, a_yield, fy, eps_s_yield

    # Steel did not yield
    k1 = 0.85 * fc_prime * b * beta1
    k2 = EPS_U_GIVEN * a_s * e_s
    c = (-k2 + math.sqrt(k2**2 + 4.0 * k1 * k2 * d)) / (2.0 * k1)
    a = beta1 * c
    eps_s = EPS_U_GIVEN * (d - c) / c
    f_s = e_s * eps_s
    return c, a, f_s, eps_s


def calculate_phi_factor(eps_t: float, fy: float, e_s: float = E_S_GIVEN) -> float:
    """Calculate strength reduction factor phi for flexure.
    
    [CALCULATED: NSCP 2015 Sec 421.2.2]
    """
    eps_y = fy / e_s
    if eps_t >= 0.005:
        return 0.90
    if eps_t <= eps_y:
        return 0.65
    return 0.65 + 0.25 * (eps_t - eps_y) / (0.005 - eps_y)


def calculate_inelastic_capacity(
    b: float, d: float, a_s: float, fc_prime: float, fy: float
) -> dict[str, float | str]:
    """Calculate ultimate strength flexural capacity phi*M_n per NSCP 2015 Sec 422."""
    c, a, f_s, eps_s = calculate_inelastic_neutral_axis(b, d, a_s, fc_prime, fy)
    phi = calculate_phi_factor(eps_s, fy)

    m_n_nmm = a_s * f_s * (d - a / 2.0)
    m_n_knm = m_n_nmm / 1e6
    phi_m_n_knm = phi * m_n_knm

    eps_y = fy / E_S_GIVEN
    if eps_s >= 0.005:
        failure_mode = "Tension-controlled (Ductile)"
    elif eps_s <= eps_y:
        failure_mode = "Compression-controlled (Brittle)"
    else:
        failure_mode = "Transition Region"

    return {
        "c": c,
        "a": a,
        "f_s": f_s,
        "eps_s": eps_s,
        "phi": phi,
        "M_n_knm": m_n_knm,
        "phi_M_n_knm": phi_m_n_knm,
        "failure_mode": failure_mode,
    }


def calculate_moment_curvature(
    b: float, d: float, h: float, a_s: float, fc_prime: float, fy: float
) -> dict[str, float | list[float]]:
    """Calculate key points on the Moment-Curvature (M - phi) response curve.
    
    Returns M_cr, phi_cr, M_y, phi_y, M_n, phi_u, ductility_ratio, and (phi_points, M_points).
    [CALCULATED: NSCP 2015 / ACI 318 Flexural Mechanics]
    """
    e_c = calculate_concrete_modulus(fc_prime)
    n = calculate_modular_ratio(fc_prime)
    f_r = calculate_modulus_of_rupture(fc_prime)

    # 1. Cracking Stage
    i_g = (1.0 / 12.0) * b * (h**3)  # Gross moment of inertia
    y_t = h / 2.0
    m_cr_nmm = (f_r * i_g) / y_t
    m_cr_knm = m_cr_nmm / 1e6
    phi_cr = m_cr_nmm / (e_c * i_g)  # 1/mm

    # 2. Yield Stage
    x = calculate_neutral_axis_depth(b, d, a_s, n)
    i_cr = calculate_cracked_moment_of_inertia(b, d, a_s, n, x)
    eps_y = fy / E_S_GIVEN
    phi_y = eps_y / (d - x)  # 1/mm
    m_y_nmm = (fy * i_cr) / (n * (d - x))
    m_y_knm = m_y_nmm / 1e6

    # 3. Ultimate Inelastic Stage
    c, a, f_s, eps_s = calculate_inelastic_neutral_axis(b, d, a_s, fc_prime, fy)
    m_n_knm = (a_s * f_s * (d - a / 2.0)) / 1e6
    phi_u = EPS_U_GIVEN / c  # 1/mm

    ductility_ratio = phi_u / phi_y if phi_y > 0 else 0.0

    # Points for plotting (Curvature in rad/m = 1000 * 1/mm, Moment in kN*m)
    phi_pts = [0.0, phi_cr * 1000.0, phi_y * 1000.0, phi_u * 1000.0]
    m_pts = [0.0, m_cr_knm, m_y_knm, m_n_knm]

    return {
        "M_cr_knm": m_cr_knm,
        "phi_cr_rad_m": phi_cr * 1000.0,
        "M_y_knm": m_y_knm,
        "phi_y_rad_m": phi_y * 1000.0,
        "M_n_knm": m_n_knm,
        "phi_u_rad_m": phi_u * 1000.0,
        "ductility_ratio": ductility_ratio,
        "phi_pts": phi_pts,
        "m_pts": m_pts,
    }


def self_check() -> None:
    """Run verification checks on flexure theory calculations against NSCP 2015."""
    fc = 28.0  # MPa [ASSUMED]
    ec = calculate_concrete_modulus(fc)
    expected_ec = 4700.0 * math.sqrt(28.0)
    assert math.isclose(ec, expected_ec, rel_tol=1e-6)

    n = calculate_modular_ratio(fc)
    expected_n = 200000.0 / expected_ec
    assert math.isclose(n, expected_n, rel_tol=1e-6)

    # Test moment-curvature calculation
    b, d, h, a_s, fy = 300.0, 500.0, 565.0, 1500.0, 420.0  # mm, MPa [ASSUMED]
    mc = calculate_moment_curvature(b, d, h, a_s, fc, fy)
    assert mc["M_cr_knm"] > 0
    assert mc["M_y_knm"] > mc["M_cr_knm"]
    assert mc["M_n_knm"] >= mc["M_y_knm"]
    assert mc["phi_u_rad_m"] > mc["phi_y_rad_m"]

    print(
        f"Self-check passed (NSCP 2015):\n"
        f"  M-phi Curve: M_cr={mc['M_cr_knm']:.2f} kN*m, M_y={mc['M_y_knm']:.2f} kN*m, M_n={mc['M_n_knm']:.2f} kN*m\n"
        f"  Curvatures: phi_cr={mc['phi_cr_rad_m']:.3f} rad/m, phi_y={mc['phi_y_rad_m']:.3f} rad/m, phi_u={mc['phi_u_rad_m']:.3f} rad/m\n"
        f"  Curvature Ductility Ratio (mu_phi): {mc['ductility_ratio']:.2f}"
    )


if __name__ == "__main__":
    self_check()
