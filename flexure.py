import math

# Provenance parameters
E_S_GIVEN: float = 200000.0  # MPa [GIVEN] Steel elastic modulus


def calculate_concrete_modulus(f_c_prime: float) -> float:
    """Calculate concrete elastic modulus E_c in MPa.
    
    Formula: E_c = 4700 * sqrt(f'_c) [CORRELATED: NSCP 2015 / ACI 318]
    """
    if f_c_prime <= 0:
        raise ValueError("f'_c must be positive.")
    return 4700.0 * math.sqrt(f_c_prime)


def calculate_modular_ratio(f_c_prime: float, e_s: float = E_S_GIVEN) -> float:
    """Calculate modular ratio n = E_s / E_c.
    
    [CALCULATED]
    """
    e_c = calculate_concrete_modulus(f_c_prime)
    return e_s / e_c


def calculate_neutral_axis_depth(
    b: float, d: float, a_s: float, n: float
) -> float:
    """Calculate neutral axis depth x using first moment of area equilibrium.
    
    Equilibrium formula: Q_c = Q_s -> A_c * x_c = n * A_s * x_s [CALCULATED]
    0.5 * b * x^2 = n * A_s * (d - x)
    """
    if b <= 0 or d <= 0 or a_s <= 0 or n <= 0:
        raise ValueError("All input dimensions and parameters must be positive.")
    
    n_as = n * a_s
    # Quadratic formula solution: 0.5 * b * x^2 + n_as * x - n_as * d = 0
    x = (-n_as + math.sqrt(n_as**2 + 2.0 * b * n_as * d)) / b
    return x


def self_check() -> None:
    """Run verification checks on flexure theory calculations."""
    fc = 28.0  # MPa [ASSUMED]
    ec = calculate_concrete_modulus(fc)
    expected_ec = 4700.0 * math.sqrt(28.0)
    assert math.isclose(ec, expected_ec, rel_tol=1e-6)

    n = calculate_modular_ratio(fc)
    expected_n = 200000.0 / expected_ec
    assert math.isclose(n, expected_n, rel_tol=1e-6)

    # Test neutral axis depth via Q_c = Q_s
    b, d, a_s = 300.0, 500.0, 1500.0  # mm [ASSUMED]
    x = calculate_neutral_axis_depth(b, d, a_s, n)
    q_c = (b * x) * (x / 2.0)  # Concrete moment A_c * x_c
    q_s = (n * a_s) * (d - x)  # Transformed steel moment n * A_s * x_s
    assert math.isclose(q_c, q_s, rel_tol=1e-5)

    print(
        f"Self-check passed: f'c={fc} MPa -> E_c={ec:.2f} MPa, n={n:.2f}, "
        f"x={x:.2f} mm (Q_c={q_c:.0f} mm^3, Q_s={q_s:.0f} mm^3)"
    )


if __name__ == "__main__":
    self_check()
