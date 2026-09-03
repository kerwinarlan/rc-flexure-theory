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


def self_check() -> None:
    """Run one verification check on flexure theory calculations."""
    fc = 28.0  # MPa [ASSUMED]
    ec = calculate_concrete_modulus(fc)
    expected_ec = 4700.0 * math.sqrt(28.0)
    assert math.isclose(ec, expected_ec, rel_tol=1e-6)

    n = calculate_modular_ratio(fc)
    expected_n = 200000.0 / expected_ec
    assert math.isclose(n, expected_n, rel_tol=1e-6)
    print(f"Self-check passed: f'c={fc} MPa -> E_c={ec:.2f} MPa, n={n:.2f}")


if __name__ == "__main__":
    self_check()
