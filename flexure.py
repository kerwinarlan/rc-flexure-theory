import math

# Provenance parameters
E_S_SI: float = 200000.0  # MPa [GIVEN: NSCP 2015 Sec 420.2.2.1 / ACI 318M]
E_S_US: float = 29000.0  # ksi [GIVEN: ACI 318 Sec 20.2.2.1]
EPS_U_GIVEN: float = 0.003  # [GIVEN: ACI 318 / NSCP 2015] Ultimate concrete strain


def calculate_concrete_modulus(f_c_prime: float, units: str = "US") -> float:
    """Calculate concrete elastic modulus E_c.
    
    SI (f'c in MPa -> E_c in MPa): E_c = 4700 * sqrt(f'_c) [NSCP 2015 Sec 419.2.2.1]
    US (f'c in ksi -> E_c in ksi): E_c = 57 * sqrt(f'c * 1000) / 1000 = 57 * sqrt(f'c_ksi) [ACI 318 Sec 19.2.2.1]
    """
    if f_c_prime <= 0:
        raise ValueError("f'_c must be positive.")
    if units.upper() == "SI":
        return 4700.0 * math.sqrt(f_c_prime)
    # US Customary: f'c in ksi
    f_c_psi = f_c_prime * 1000.0
    return (57000.0 * math.sqrt(f_c_psi)) / 1000.0  # Returns ksi


def calculate_modular_ratio(f_c_prime: float, units: str = "US") -> float:
    """Calculate modular ratio n = E_s / E_c.
    
    [CALCULATED: ACI 318 / NSCP 2015]
    """
    e_s = E_S_SI if units.upper() == "SI" else E_S_US
    e_c = calculate_concrete_modulus(f_c_prime, units)
    return e_s / e_c


def calculate_modulus_of_rupture(f_c_prime: float, units: str = "US") -> float:
    """Calculate concrete modulus of rupture f_r.
    
    SI (f'c in MPa -> f_r in MPa): f_r = 0.62 * sqrt(f'_c) [NSCP 2015 Sec 419.2.3.1]
    US (f'c in ksi -> f_r in ksi): f_r = 7.5 * sqrt(f'c_psi) / 1000 [ACI 318 Sec 19.2.3.1]
    """
    if units.upper() == "SI":
        return 0.62 * math.sqrt(f_c_prime)
    f_c_psi = f_c_prime * 1000.0
    return (7.5 * math.sqrt(f_c_psi)) / 1000.0  # Returns ksi


def calculate_beta_1(f_c_prime: float, units: str = "US") -> float:
    """Calculate Whitney stress block factor beta_1.
    
    [CALCULATED: ACI 318 / NSCP 2015]
    """
    fc_si = f_c_prime if units.upper() == "SI" else f_c_prime * 6.89476  # ksi -> MPa
    if fc_si <= 28.0:
        return 0.85
    beta = 0.85 - 0.05 * (fc_si - 28.0) / 7.0
    return max(0.65, min(0.85, beta))


def calculate_neutral_axis_depth(
    b: float, d: float, a_s: float, n: float
) -> float:
    """Calculate elastic neutral axis depth x using first moment of area equilibrium.
    
    Equilibrium formula: Q_c = Q_s -> A_c * x_c = n * A_s * x_s [CALCULATED]
    0.5 * b * x^2 = n * A_s * (d - x)
    """
    if b <= 0 or d <= 0 or a_s <= 0 or n <= 0:
        raise ValueError("All input dimensions and parameters must be positive.")
    
    n_as = n * a_s
    return (-n_as + math.sqrt(n_as**2 + 2.0 * b * n_as * d)) / b


def calculate_cracked_moment_of_inertia(
    b: float, d: float, a_s: float, n: float, x: float
) -> float:
    """Calculate cracked section moment of inertia I_cr in mm^4 or in^4."""
    return (1.0 / 3.0) * b * (x**3) + n * a_s * ((d - x) ** 2)


def calculate_service_stresses(
    m_service: float, b: float, d: float, a_s: float, n: float
) -> tuple[float, float]:
    """Calculate working stresses f_c and f_s under service moment M."""
    x = calculate_neutral_axis_depth(b, d, a_s, n)
    i_cr = calculate_cracked_moment_of_inertia(b, d, a_s, n, x)
    f_c = (m_service * x) / i_cr
    f_s = (n * m_service * (d - x)) / i_cr
    return f_c, f_s


def calculate_inelastic_neutral_axis(
    b: float, d: float, a_s: float, fc_prime: float, fy: float, units: str = "US"
) -> tuple[float, float, float, float]:
    """Calculate inelastic neutral axis depth c, stress block a, steel stress f_s, and strain eps_s."""
    e_s = E_S_SI if units.upper() == "SI" else E_S_US
    beta1 = calculate_beta_1(fc_prime, units)
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


def calculate_phi_factor(eps_t: float, fy: float, units: str = "US") -> float:
    """Calculate strength reduction factor phi for flexure."""
    e_s = E_S_SI if units.upper() == "SI" else E_S_US
    eps_y = fy / e_s
    if eps_t >= 0.005:
        return 0.90
    if eps_t <= eps_y:
        return 0.65
    return 0.65 + 0.25 * (eps_t - eps_y) / (0.005 - eps_y)


def calculate_inelastic_capacity(
    b: float, d: float, a_s: float, fc_prime: float, fy: float, units: str = "US"
) -> dict[str, float | str]:
    """Calculate ultimate strength flexural capacity phi*M_n in kN*m (SI) or kip-in (US)."""
    c, a, f_s, eps_s = calculate_inelastic_neutral_axis(b, d, a_s, fc_prime, fy, units)
    phi = calculate_phi_factor(eps_s, fy, units)

    # Nominal moment M_n = T * (d - a/2) = A_s * f_s * (d - a/2)
    m_n_raw = a_s * f_s * (d - a / 2.0)
    m_n_mom = m_n_raw / 1e6 if units.upper() == "SI" else m_n_raw  # N*mm -> kN*m or in-kip
    phi_m_n_mom = phi * m_n_mom

    e_s = E_S_SI if units.upper() == "SI" else E_S_US
    eps_y = fy / e_s
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
        "M_n": m_n_mom,
        "phi_M_n": phi_m_n_mom,
        "failure_mode": failure_mode,
    }


def calculate_moment_curvature(
    b: float, d: float, h: float, a_s: float, fc_prime: float, fy: float, units: str = "US"
) -> dict[str, float | list[float] | dict[str, str]]:
    """Calculate key points and 3 explicit regions on the Moment-Curvature (M - phi) response curve.
    
    Curvature unit: 1/in (US) or rad/m (SI)
    Moment unit: kip-in (US) or kN*m (SI)
    """
    is_si = units.upper() == "SI"
    e_s = E_S_SI if is_si else E_S_US
    e_c = calculate_concrete_modulus(fc_prime, units)
    n = calculate_modular_ratio(fc_prime, units)
    f_r = calculate_modulus_of_rupture(fc_prime, units)

    # Region O -> C: Uncracked Elastic Stage
    i_g = (1.0 / 12.0) * b * (h**3)
    y_t = h / 2.0
    m_cr_raw = (f_r * i_g) / y_t
    m_cr_mom = m_cr_raw / 1e6 if is_si else m_cr_raw  # kN*m or kip-in
    phi_cr = m_cr_raw / (e_c * i_g)  # 1/mm or 1/in

    # Region C -> Y: Cracked Elastic Stage
    x = calculate_neutral_axis_depth(b, d, a_s, n)
    i_cr = calculate_cracked_moment_of_inertia(b, d, a_s, n, x)
    eps_y = fy / e_s
    phi_y = eps_y / (d - x)  # 1/mm or 1/in
    m_y_raw = (fy * i_cr) / (n * (d - x))
    m_y_mom = m_y_raw / 1e6 if is_si else m_y_raw

    # Region Y -> U: Cracked Inelastic Stage
    c, a, f_s, eps_s = calculate_inelastic_neutral_axis(b, d, a_s, fc_prime, fy, units)
    m_n_raw = a_s * f_s * (d - a / 2.0)
    m_n_mom = m_n_raw / 1e6 if is_si else m_n_raw
    phi_u = EPS_U_GIVEN / c  # 1/mm or 1/in

    ductility_ratio = phi_u / phi_y if phi_y > 0 else 0.0

    # Scale curvature for plot (1/in for US, rad/m for SI)
    scale_curv = 1000.0 if is_si else 1.0
    phi_pts = [0.0, phi_cr * scale_curv, phi_y * scale_curv, phi_u * scale_curv]
    m_pts = [0.0, m_cr_mom, m_y_mom, m_n_mom]

    m_unit = "kN·m" if is_si else "kip-in"
    phi_unit = "rad/m" if is_si else "1/in"

    regions = {
        "O_C": f"Region O->C: Stresses Elastic, Section Uncracked (0 to {m_cr_mom:.1f} {m_unit})",
        "C_Y": f"Region C->Y: Stresses Elastic, Section Cracked ({m_cr_mom:.1f} to {m_y_mom:.1f} {m_unit})",
        "Y_U": f"Region Y->U: Stresses Inelastic, Section Cracked ({m_y_mom:.1f} to {m_n_mom:.1f} {m_unit})",
    }

    return {
        "M_cr": m_cr_mom,
        "phi_cr": phi_cr * scale_curv,
        "M_y": m_y_mom,
        "phi_y": phi_y * scale_curv,
        "M_n": m_n_mom,
        "phi_u": phi_u * scale_curv,
        "ductility_ratio": ductility_ratio,
        "phi_pts": phi_pts,
        "m_pts": m_pts,
        "m_unit": m_unit,
        "phi_unit": phi_unit,
        "regions": regions,
    }


def self_check() -> None:
    """Run verification checks on flexure theory calculations for US and SI units."""
    # US Customary test case: 4 ksi concrete, 60 ksi steel, b=12 in, d=20 in, h=22.5 in, As=2.37 in^2
    mc_us = calculate_moment_curvature(12.0, 20.0, 22.5, 2.37, 4.0, 60.0, units="US")
    assert mc_us["m_unit"] == "kip-in"
    assert mc_us["phi_unit"] == "1/in"
    assert mc_us["M_cr"] > 0
    assert mc_us["M_y"] > mc_us["M_cr"]
    assert mc_us["M_n"] >= mc_us["M_y"]

    # SI test case
    mc_si = calculate_moment_curvature(300.0, 500.0, 565.0, 1500.0, 28.0, 420.0, units="SI")
    assert mc_si["m_unit"] == "kN·m"
    assert mc_si["phi_unit"] == "rad/m"

    print(
        f"Self-check passed (US & SI):\n"
        f"  US Customary: M_cr={mc_us['M_cr']:.1f} kip-in, M_y={mc_us['M_y']:.1f} kip-in, M_n={mc_us['M_n']:.1f} kip-in\n"
        f"  Curvatures: phi_cr={mc_us['phi_cr']:.6f} 1/in, phi_y={mc_us['phi_y']:.6f} 1/in, phi_u={mc_us['phi_u']:.6f} 1/in\n"
        f"  Ductility Ratio (mu_phi): {mc_us['ductility_ratio']:.2f}"
    )


if __name__ == "__main__":
    self_check()
