import math
import numpy as np

# Provenance parameters
E_S_SI: float = 200000.0  # MPa [GIVEN: NSCP 2015 Sec 420.2.2.1 / ACI 318M]
E_S_US: float = 29000.0  # ksi [GIVEN: ACI 318 Sec 20.2.2.1]
EPS_U_GIVEN: float = 0.003  # [GIVEN: ACI 318 / NSCP 2015] Ultimate concrete strain


def calculate_concrete_modulus(f_c_prime: float, units: str = "US") -> float:
    """Calculate concrete elastic modulus E_c.
    
    SI (f'c in MPa -> E_c in MPa): E_c = 4700 * sqrt(f'_c) [NSCP 2015 Sec 419.2.2.1]
    US (f'c in ksi -> E_c in ksi): E_c = 57 * sqrt(f'c * 1000) / 1000 [ACI 318 Sec 19.2.2.1]
    """
    if f_c_prime <= 0:
        raise ValueError("f'_c must be positive.")
    if units.upper() == "SI":
        return 4700.0 * math.sqrt(f_c_prime)
    f_c_psi = f_c_prime * 1000.0
    return (57000.0 * math.sqrt(f_c_psi)) / 1000.0


def calculate_modular_ratio(f_c_prime: float, units: str = "US") -> float:
    """Calculate modular ratio n = E_s / E_c."""
    e_s = E_S_SI if units.upper() == "SI" else E_S_US
    e_c = calculate_concrete_modulus(f_c_prime, units)
    return e_s / e_c


def calculate_modulus_of_rupture(f_c_prime: float, units: str = "US") -> float:
    """Calculate concrete modulus of rupture f_r."""
    if units.upper() == "SI":
        return 0.62 * math.sqrt(f_c_prime)
    f_c_psi = f_c_prime * 1000.0
    return (7.5 * math.sqrt(f_c_psi)) / 1000.0


def calculate_beta_1(f_c_prime: float, units: str = "US") -> float:
    """Calculate Whitney stress block factor beta_1 per NSCP 2015 Table 422.2.2.4.3 / ACI 318."""
    fc_si = f_c_prime if units.upper() == "SI" else f_c_prime * 6.89476
    if fc_si <= 28.0:
        return 0.85
    beta = 0.85 - 0.05 * (fc_si - 28.0) / 7.0
    return max(0.65, min(0.85, beta))


def calculate_neutral_axis_depth(
    b: float, d: float, a_s: float, n: float
) -> float:
    """Calculate elastic neutral axis depth x using first moment of area equilibrium."""
    if b <= 0 or d <= 0 or a_s <= 0 or n <= 0:
        raise ValueError("All input dimensions and parameters must be positive.")
    
    n_as = n * a_s
    return (-n_as + math.sqrt(n_as**2 + 2.0 * b * n_as * d)) / b


def calculate_cracked_moment_of_inertia(
    b: float, d: float, a_s: float, n: float, x: float
) -> float:
    """Calculate cracked section moment of inertia I_cr."""
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
    b: float, d: float, a_s: float, fc_prime: float, fy: float, units: str = "US", lambda_factor: float = 1.0
) -> tuple[float, float, float, float]:
    """Calculate inelastic neutral axis depth c, stress block a, steel stress f_s, and strain eps_s."""
    e_s = E_S_SI if units.upper() == "SI" else E_S_US
    beta1 = calculate_beta_1(fc_prime, units)
    eps_y = fy / e_s

    a_yield = (a_s * fy) / (0.85 * lambda_factor * fc_prime * b)
    c_yield = a_yield / beta1
    eps_s_yield = EPS_U_GIVEN * (d - c_yield) / c_yield

    if eps_s_yield >= eps_y:
        return c_yield, a_yield, fy, eps_s_yield

    k1 = 0.85 * lambda_factor * fc_prime * b * beta1
    k2 = EPS_U_GIVEN * a_s * e_s
    c = (-k2 + math.sqrt(k2**2 + 4.0 * k1 * k2 * d)) / (2.0 * k1)
    a = beta1 * c
    eps_s = EPS_U_GIVEN * (d - c) / c
    f_s = e_s * eps_s
    return c, a, f_s, eps_s


def calculate_balanced_condition(
    b: float, d: float, fc_prime: float, fy: float, units: str = "US", lambda_factor: float = 1.0
) -> dict[str, float]:
    """Calculate balanced condition parameters (c_bal, a_bal, A_s_bal, rho_b, rho_max) per NSCP 2015 Sec 422 / Slide 35."""
    is_si = units.upper() == "SI"
    e_s = E_S_SI if is_si else E_S_US
    beta1 = calculate_beta_1(fc_prime, units)
    eps_y = fy / e_s

    c_bal = (EPS_U_GIVEN / (EPS_U_GIVEN + eps_y)) * d
    a_bal = beta1 * c_bal
    a_s_bal = (0.85 * lambda_factor * fc_prime * b * a_bal) / fy
    rho_b = a_s_bal / (b * d)

    c_max = (EPS_U_GIVEN / (EPS_U_GIVEN + 0.005)) * d
    a_max = beta1 * c_max
    a_s_max = (0.85 * lambda_factor * fc_prime * b * a_max) / fy
    rho_max = a_s_max / (b * d)

    return {
        "c_bal": c_bal,
        "a_bal": a_bal,
        "A_s_bal": a_s_bal,
        "rho_b": rho_b,
        "c_max": c_max,
        "a_max": a_max,
        "A_s_max": a_s_max,
        "rho_max": rho_max,
    }


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
    b: float, d: float, a_s: float, fc_prime: float, fy: float, units: str = "US", lambda_factor: float = 1.0
) -> dict[str, float | str]:
    """Calculate ultimate strength flexural capacity phi*M_n and stress block depth a."""
    c, a, f_s, eps_s = calculate_inelastic_neutral_axis(b, d, a_s, fc_prime, fy, units, lambda_factor)
    phi = calculate_phi_factor(eps_s, fy, units)

    m_n_raw = a_s * f_s * (d - a / 2.0)
    m_n_mom = m_n_raw / 1e6 if units.upper() == "SI" else m_n_raw
    phi_m_n_mom = phi * m_n_mom

    e_s = E_S_SI if units.upper() == "SI" else E_S_US
    eps_y = fy / e_s
    if eps_s >= 0.005:
        failure_mode = "Tension-controlled (Ductile)"
    elif eps_s <= eps_y:
        failure_mode = "Compression-controlled (Brittle)"
    else:
        failure_mode = "Transition Region"

    bal = calculate_balanced_condition(b, d, fc_prime, fy, units, lambda_factor)

    return {
        "c": c,
        "a": a,
        "f_s": f_s,
        "eps_s": eps_s,
        "phi": phi,
        "M_n": m_n_mom,
        "phi_M_n": phi_m_n_mom,
        "failure_mode": failure_mode,
        "lambda": lambda_factor,
        "balanced": bal,
    }


def calculate_moment_curvature(
    b: float, d: float, h: float, a_s: float, fc_prime: float, fy: float, units: str = "US", lambda_factor: float = 1.0
) -> dict[str, float | list[float] | dict[str, str] | np.ndarray]:
    """Calculate key points, 3 regions, and continuous fiber-integrated Moment-Curvature (M - phi) response."""
    is_si = units.upper() == "SI"
    e_s = E_S_SI if is_si else E_S_US
    e_c = calculate_concrete_modulus(fc_prime, units)
    n = calculate_modular_ratio(fc_prime, units)
    f_r = calculate_modulus_of_rupture(fc_prime, units) * lambda_factor

    # Key Limit Points
    i_g = (1.0 / 12.0) * b * (h**3)
    y_t = h / 2.0
    m_cr_raw = (f_r * i_g) / y_t
    m_cr_mom = m_cr_raw / 1e6 if is_si else m_cr_raw
    phi_cr = m_cr_raw / (e_c * i_g)

    x = calculate_neutral_axis_depth(b, d, a_s, n)
    i_cr = calculate_cracked_moment_of_inertia(b, d, a_s, n, x)
    eps_y = fy / e_s
    phi_y = eps_y / (d - x)
    m_y_raw = (fy * i_cr) / (n * (d - x))
    m_y_mom = m_y_raw / 1e6 if is_si else m_y_raw

    c, a, f_s, eps_s = calculate_inelastic_neutral_axis(b, d, a_s, fc_prime, fy, units, lambda_factor)
    m_n_raw = a_s * f_s * (d - a / 2.0)
    m_n_mom = m_n_raw / 1e6 if is_si else m_n_raw
    phi_u = EPS_U_GIVEN / c

    ductility_ratio = phi_u / phi_y if phi_y > 0 else 0.0

    scale_curv = 1000.0 if is_si else 1.0
    phi_pts = [0.0, phi_cr * scale_curv, phi_y * scale_curv, phi_u * scale_curv]
    m_pts = [0.0, m_cr_mom, m_y_mom, m_n_mom]

    m_unit = "kN·m" if is_si else "kip-in"
    phi_unit = "rad/m" if is_si else "1/in"

    # Continuous Fiber Integration for smooth curves (like Slide 5425)
    def solve_c_fiber(phi_val):
        def force_diff(c_val):
            eps_c = phi_val * c_val
            eps_s_val = phi_val * (d - c_val)
            y_fibers = np.linspace(0, c_val, 50)
            dy = c_val / 50.0
            eps_fibers = phi_val * y_fibers
            eps_0 = 0.002
            stresses = np.where(
                eps_fibers <= eps_0,
                fc_prime * (2.0 * (eps_fibers / eps_0) - (eps_fibers / eps_0)**2),
                fc_prime
            )
            stresses = np.maximum(0.0, stresses)
            C_force = np.sum(stresses * b * dy) * lambda_factor
            fs_val = min(fy, e_s * eps_s_val) if eps_s_val > 0 else e_s * eps_s_val
            T_force = a_s * fs_val
            return C_force - T_force, C_force, stresses, y_fibers, dy

        c_low, c_high = 0.01 * d, d
        for _ in range(25):
            c_mid = (c_low + c_high) / 2.0
            diff, C_force, stresses, y_fibers, dy = force_diff(c_mid)
            if diff < 0:
                c_low = c_mid
            else:
                c_high = c_mid
        diff, C_force, stresses, y_fibers, dy = force_diff(c_mid)

        if C_force > 0:
            y_centroid = np.sum(stresses * y_fibers * dy) / np.sum(stresses * dy)
            arm = d - (c_mid - y_centroid)
            M_val = C_force * arm
        else:
            M_val = 0.0
        return c_mid, M_val, phi_val * c_mid

    phi_max = EPS_U_GIVEN / (a_s * fy / (0.85 * fc_prime * b * 0.85)) if (0.85 * fc_prime * b) > 0 else 0.001
    phi_cracked_samples = np.linspace(0, phi_max * 1.15, 60)
    
    phi_continuous = []
    m_continuous = []
    for p_val in phi_cracked_samples:
        if p_val <= phi_cr:
            M_val = e_c * i_g * p_val
            eps_c_val = p_val * y_t
        else:
            c_mid, M_val, eps_c_val = solve_c_fiber(p_val)

        if eps_c_val > EPS_U_GIVEN * 1.05:
            break

        phi_continuous.append(p_val * scale_curv)
        m_continuous.append(M_val / (1e6 if is_si else 1.0))

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
        "phi_continuous": np.array(phi_continuous),
        "m_continuous": np.array(m_continuous),
        "m_unit": m_unit,
        "phi_unit": phi_unit,
        "regions": regions,
    }


def self_check() -> None:
    """Run verification checks on flexure theory calculations for US, SI, CE 152 Example 3, and Slide 35."""
    # CE 152 Example 3 verification
    res_ce152 = calculate_inelastic_capacity(250.0, 575.0, 1470.0, 28.0, 420.0, units="SI")
    assert abs(res_ce152["a"] - 103.76) < 0.1
    assert abs(res_ce152["c"] - 122.08) < 0.1

    # CE 152 Slide 35 Balanced Condition verification
    bal_slide35 = calculate_balanced_condition(250.0, 575.0, 28.0, 420.0, units="SI")
    assert abs(bal_slide35["c_bal"] - 338.24) < 0.1
    assert abs(bal_slide35["rho_b"] - 0.02833) < 0.001

    # US Customary continuous moment-curvature check
    mc_us = calculate_moment_curvature(12.0, 20.0, 22.5, 2.37, 4.0, 60.0, units="US")
    assert len(mc_us["phi_continuous"]) > 20
    assert mc_us["m_unit"] == "kip-in"

    print(
        f"Self-check passed:\n"
        f"  CE 152 Example 3 : a = {res_ce152['a']:.2f} mm (expected 103.76 mm), c = {res_ce152['c']:.2f} mm\n"
        f"  CE 152 Slide 35   : c_bal = {bal_slide35['c_bal']:.2f} mm, rho_b = {bal_slide35['rho_b']*100:.2f}%\n"
        f"  Continuous M-phi : {len(mc_us['phi_continuous'])} points, M_n={mc_us['M_n']:.1f} kip-in\n"
        f"  Ductility Ratio   : {mc_us['ductility_ratio']:.2f}"
    )


if __name__ == "__main__":
    self_check()
