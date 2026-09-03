# Basic Flexure Theory for Reinforced Concrete (NSCP 2015)

Calculates fundamental elastic and flexural parameters for reinforced concrete beams per NSCP 2015 Volume I.

## About

This repository provides core equations for concrete elastic modulus, modular ratio, and working stresses.
All calculations follow the National Structural Code of the Philippines (NSCP 2015, 7th Edition).

## Key Formulas (NSCP 2015 References)

### Concrete Elastic Modulus ($E_c$)
$$E_c = 4700 \sqrt{f'_c} \quad \text{[NSCP 2015 Sec. 419.2.2.1]}$$
* $E_c$: Modulus of elasticity of concrete (MPa) `[CORRELATED]`
* $f'_c$: Specified compressive strength of concrete (MPa) `[GIVEN/ASSUMED]`

### Modular Ratio ($n$)
$$n = \frac{E_s}{E_c} \quad \text{[NSCP 2015 Sec. 424.5.2]}$$
* $n$: Modular ratio `[CALCULATED]`
* $E_s$: Modulus of elasticity of reinforcement steel ($200\,000 \text{ MPa}$) `[GIVEN: NSCP 2015 Sec. 420.2.2.1]`

### Stress Block Factor ($\beta_1$)
$$\beta_1 = 0.85 - 0.05 \frac{f'_c - 28}{7} \quad \text{where } 0.65 \le \beta_1 \le 0.85 \quad \text{[NSCP 2015 Sec. 422.2.2.4]}$$

### Neutral Axis Depth ($x$) via First Moment Equilibrium ($Q_c = Q_s$)
$$Q_c = Q_s \implies A_c x_c = n A_s x_s \quad \text{[NSCP 2015 Sec. 424.5]}$$
$$\frac{1}{2} b x^2 = n A_s (d - x)$$
* $A_c$: Concrete compression area ($b \cdot x$) `[CALCULATED]`
* $x_c$: Centroid distance from concrete compression area to neutral axis ($x / 2$) `[CALCULATED]`
* $A_s$: Tension steel reinforcement area `[GIVEN]`
* $x_s$: Centroid distance from tension steel to neutral axis ($d - x$) `[CALCULATED]`

### Service Stresses ($f_c, f_s$)
$$I_{cr} = \frac{1}{3} b x^3 + n A_s (d - x)^2 \quad \text{[NSCP 2015 Sec. 424.5]}$$
$$f_c = \frac{M x}{I_{cr}} \le 0.45 f'_c \quad \text{[Concrete Extreme Fiber Stress]}$$
$$f_s = \frac{n M (d - x)}{I_{cr}} \le 0.50 f_y \quad \text{[Steel Tensile Stress]}$$

## File Structure

```
rc-flexure-theory/
├── flexure.py             # Core NSCP 2015 flexure calculation module
├── PARAMETER_LEDGER.md    # Parameter provenance tracking table
├── .gitignore             # Git ignore patterns
└── README.md              # Project documentation
```

## Quickstart

Run the Python verification script:

```bash
python3 flexure.py
```

Expected output:
```
Self-check passed (NSCP 2015):
  f'c=28.0 MPa -> E_c=24870.06 MPa, n=8.04, beta_1=0.85
  NA depth x=164.30 mm (Q_c=4049393 mm^3, Q_s=4049393 mm^3)
  Service stresses for M=100 kN*m: f_c=9.11 MPa (allow=12.60 MPa), f_s=149.73 MPa
```

## Parameter Provenance

All parameters require strict provenance tagging (`GIVEN`, `MEASURED`, `CALCULATED`, `CORRELATED`, `ADOPTED`, `ASSUMED`).
See [`PARAMETER_LEDGER.md`](PARAMETER_LEDGER.md) for full details.
