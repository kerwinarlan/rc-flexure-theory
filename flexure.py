import math

# Provenance parameters [NSCP 2015 Section 420.2.2.1]
E_S_GIVEN: float = 200000.0  # MPa [GIVEN] Steel elastic modulus


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
    """Calculate neutral axis depth x using first moment of area equilibrium.
    
    Equilibrium formula: Q_c = Q_s -> A_c * x_c = n * A_s * x_s [CALCULATED: NSCP 2015 Sec 424.5]
    0.5 * b * x^2 = n * A_s * (d - x)
    """
    if b <= 0 or d <= 0 or a_s <= 0 or n <= 0:
        raise ValueError("All input dimensions and parameters must be positive.")
    
    n_as = n * a_s
    # Solution to quadratic: 0.5 * b * x^2 + n_as * x - n_as * d = 0
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
    f_c = (M * x) / I_cr
    f_s = (n * M * (d - x)) / I_cr
    """
    x = calculate_neutral_axis_depth(b, d, a_s, n)
    i_cr = calculate_cracked_moment_of_inertia(b, d, a_s, n, x)
    f_c = (m_service * x) / i_cr
    f_s = (n * m_service * (d - x)) / i_cr
    return f_c, f_s


def self_check() -> None:
    """Run verification checks on flexure theory calculations against NSCP 2015."""
    fc = 28.0  # MPa [ASSUMED]
    ec = calculate_concrete_modulus(fc)
    expected_ec = 4700.0 * math.sqrt(28.0)
    assert math.isclose(ec, expected_ec, rel_tol=1e-6)

    n = calculate_modular_ratio(fc)
    expected_n = 200000.0 / expected_ec
    assert math.isclose(n, expected_n, rel_tol=1e-6)

    beta1 = calculate_beta_1(fc)
    assert beta1 == 0.85

    # Check beta_1 reduction for fc = 35 MPa
    beta1_35 = calculate_beta_1(35.0)
    assert math.isclose(beta1_35, 0.80, rel_tol=1e-6)

    # Test neutral axis depth via Q_c = Q_s
    b, d, a_s = 300.0, 500.0, 1500.0  # mm [ASSUMED]
    x = calculate_neutral_axis_depth(b, d, a_s, n)
    q_c = (b * x) * (x / 2.0)  # Concrete moment A_c * x_c
    q_s = (n * a_s) * (d - x)  # Transformed steel moment n * A_s * x_s
    assert math.isclose(q_c, q_s, rel_tol=1e-5)

    # Test service stresses for M = 100 kN*m = 100e6 N*mm
    m_serv = 100e6  # N*mm [ASSUMED]
    f_c, f_s = calculate_service_stresses(m_serv, b, d, a_s, n)
    fc_allow = 0.45 * fc  # NSCP 2015 allowable concrete stress (12.6 MPa)
    
    assert f_c < fc_allow  # Elastic range check

    print(
        f"Self-check passed (NSCP 2015):\n"
        f"  f'c={fc} MPa -> E_c={ec:.2f} MPa, n={n:.2f}, beta_1={beta1:.2f}\n"
        f"  NA depth x={x:.2f} mm (Q_c={q_c:.0f} mm^3, Q_s={q_s:.0f} mm^3)\n"
        f"  Service stresses for M=100 kN*m: f_c={f_c:.2f} MPa (allow={fc_allow:.2f} MPa), f_s={f_s:.2f} MPa"
    )


if __name__ == "__main__":
    self_check()
