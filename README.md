# Basic Flexure Theory for Reinforced Concrete (NSCP 2015)

Calculates fundamental elastic (WSD), inelastic (USD), and moment-curvature ($M - \phi$) flexural behavior across 3 regions for reinforced concrete beams per NSCP 2015 Volume I.

## About

This repository provides core equations for concrete elastic modulus, modular ratio, neutral axis depth, working stresses, ultimate strength capacity ($\phi M_n$), and 3-region moment-curvature response.
The application includes a desktop solver GUI built with `FreeSimpleGUI` and `matplotlib` following Engr. Jaydee Lucero's design pattern.
All calculations follow the National Structural Code of the Philippines (NSCP 2015, 7th Edition).

## Three Flexural Behavior Regions

The flexural behavior of a reinforced concrete section spans three distinct physical regions:

1. **Region O $\rightarrow$ C: Stresses Elastic, Section Uncracked** ($0 \le M \le M_{cr}$)
   * Concrete remains uncracked in tension. Response governed by gross section flexural rigidity $E_c I_g$.
   * Cracking limit: $M_{cr} = \frac{f_r I_g}{y_t}$ where $f_r = 0.62 \sqrt{f'_c}$ `[NSCP 2015 Sec. 419.2.3.1]`.

2. **Region C $\rightarrow$ Y: Stresses Elastic, Section Cracked** ($M_{cr} < M \le M_y$)
   * Concrete cracks in tension. Response governed by transformed cracked flexural rigidity $E_c I_{cr}$.
   * Neutral axis depth $x$ determined by first moment equilibrium $Q_c = Q_s \implies \frac{1}{2} b x^2 = n A_s (d - x)$ `[NSCP 2015 Sec. 424.5]`.
   * Steel yield limit: $M_y = \frac{f_y I_{cr}}{n (d - x)}$.

3. **Region Y $\rightarrow$ U: Stresses Inelastic, Section Cracked** ($M_y < M \le M_n$)
   * Concrete enters non-linear compressive range modeled by Whitney rectangular stress block ($a = \beta_1 c$).
   * Equilibrium: $C = 0.85 f'_c b a = T = A_s f_s$ `[NSCP 2015 Sec. 422.2]`.
   * Nominal capacity: $M_n = A_s f_s \left(d - \frac{a}{2}\right)$, Curvature ductility ratio: $\mu_\phi = \frac{\phi_u}{\phi_y}$.

## Key Formulas (NSCP 2015 References)

### 1. Concrete Elastic Modulus ($E_c$) and Modulus of Rupture ($f_r$)
$$E_c = 4700 \sqrt{f'_c} \quad \text{[NSCP 2015 Sec. 419.2.2.1]}$$
$$f_r = 0.62 \sqrt{f'_c} \quad \text{[NSCP 2015 Sec. 419.2.3.1]}$$

### 2. Modular Ratio ($n$)
$$n = \frac{E_s}{E_c} \quad \text{[NSCP 2015 Sec. 424.5.2]}$$

### 3. Elastic First Moment Equilibrium ($Q_c = Q_s$)
$$\frac{1}{2} b x^2 = n A_s (d - x) \quad \text{[NSCP 2015 Sec. 424.5]}$$

### 4. Inelastic Whitney Stress Block ($a = \beta_1 c$)
$$C = 0.85 f'_c b a = T = A_s f_s \quad \text{[NSCP 2015 Sec. 422.2]}$$
$$\beta_1 = 0.85 - 0.05 \frac{f'_c - 28}{7} \quad \text{where } 0.65 \le \beta_1 \le 0.85 \quad \text{[NSCP 2015 Sec. 422.2.2.4]}$$

### 5. Ultimate Flexural Strength ($\phi M_n$)
$$M_n = A_s f_s \left(d - \frac{a}{2}\right) \quad \text{[NSCP 2015 Sec. 422.2]}$$
$$\phi = \begin{cases} 0.90 & \text{if } \epsilon_t \ge 0.005 \text{ (Tension-controlled)} \\ 0.65 & \text{if } \epsilon_t \le \epsilon_y \text{ (Compression-controlled)} \\ 0.65 + 0.25 \frac{\epsilon_t - \epsilon_y}{0.005 - \epsilon_y} & \text{if } \epsilon_y < \epsilon_t < 0.005 \text{ (Transition)} \end{cases} \quad \text{[NSCP 2015 Sec. 421.2]}$$

### 6. Moment - Curvature ($M - \phi$) Response and Ductility ($\mu_\phi$)
$$M_{cr} = \frac{f_r I_g}{y_t}, \quad \phi_{cr} = \frac{M_{cr}}{E_c I_g} \quad \text{[Region O->C]}$$
$$M_y = \frac{f_y I_{cr}}{n (d - x)}, \quad \phi_y = \frac{\epsilon_y}{d - x} \quad \text{[Region C->Y]}$$
$$\phi_u = \frac{\epsilon_u}{c} = \frac{0.003}{c}, \quad \mu_\phi = \frac{\phi_u}{\phi_y} \quad \text{[Region Y->U]}$$

## File Structure

```
rc-flexure-theory/
├── flexure.py             # Core NSCP 2015 elastic, inelastic, and 3-region M-phi flexure module
├── solver_gui.py          # FreeSimpleGUI solver GUI with 3-region M-phi & stress plots
├── PARAMETER_LEDGER.md    # Parameter provenance tracking table
├── .gitignore             # Git ignore patterns
└── README.md              # Project documentation
```

## Quickstart

### Launch Desktop Solver GUI
```bash
python3 solver_gui.py
```

### Run Automated Headless Verification
```bash
python3 solver_gui.py --test
python3 flexure.py
```

Expected headless output:
```
Self-check passed (NSCP 2015):
  Region O->C (Elastic Uncracked): M_cr=52.36 kN*m, phi_cr=0.000 rad/m
  Region C->Y (Elastic Cracked)  : M_y=280.50 kN*m, phi_y=0.006 rad/m
  Region Y->U (Inelastic Cracked): M_n=287.21 kN*m, phi_u=0.029 rad/m
  Ductility Ratio (mu_phi): 4.62
solver_gui headless check passed!
```

## Parameter Provenance

All parameters require strict provenance tagging (`GIVEN`, `MEASURED`, `CALCULATED`, `CORRELATED`, `ADOPTED`, `ASSUMED`).
See [`PARAMETER_LEDGER.md`](PARAMETER_LEDGER.md) for full details.
