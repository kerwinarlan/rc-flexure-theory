# Basic Flexure Theory for Reinforced Concrete (NSCP 2015)

Calculates fundamental elastic (WSD) and inelastic (USD) flexural parameters for reinforced concrete beams per NSCP 2015 Volume I.

## About

This repository provides core equations for concrete elastic modulus, modular ratio, neutral axis depth, working stresses, and ultimate strength capacity ($\phi M_n$).
The application includes a desktop solver GUI built with `FreeSimpleGUI` and `matplotlib` following Engr. Jaydee Lucero's design pattern.
All calculations follow the National Structural Code of the Philippines (NSCP 2015, 7th Edition).

## Key Formulas (NSCP 2015 References)

### 1. Concrete Elastic Modulus ($E_c$)
$$E_c = 4700 \sqrt{f'_c} \quad \text{[NSCP 2015 Sec. 419.2.2.1]}$$

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

## File Structure

```
rc-flexure-theory/
├── flexure.py             # Core NSCP 2015 elastic and inelastic flexure module
├── solver_gui.py          # FreeSimpleGUI solver GUI with Matplotlib stress diagrams
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
  f'c=28.0 MPa -> E_c=24870.06 MPa, n=8.04, beta_1=0.85
  Elastic NA x=164.30 mm | Inelastic c=103.81 mm, a=88.24 mm
  Nominal M_n=287.21 kN*m, Design phi*M_n=258.49 kN*m (phi=0.90)
solver_gui headless check passed!
```

## Parameter Provenance

All parameters require strict provenance tagging (`GIVEN`, `MEASURED`, `CALCULATED`, `CORRELATED`, `ADOPTED`, `ASSUMED`).
See [`PARAMETER_LEDGER.md`](PARAMETER_LEDGER.md) for full details.
