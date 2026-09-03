# Basic Flexure Theory for Reinforced Concrete

Calculates fundamental elastic parameters for reinforced concrete flexure analysis under working stress design.

## About

This repository provides core equations for concrete elastic modulus, modular ratio, and neutral axis depth.
It follows NSCP 2015 (Section 419.2.2.1) and ACI 318 standards.

## Key Formulas

### Concrete Elastic Modulus ($E_c$)
$$E_c = 4700 \sqrt{f'_c}$$
* $E_c$: Modulus of elasticity of concrete (MPa) `[CORRELATED]`
* $f'_c$: Specified compressive strength of concrete (MPa) `[GIVEN/ASSUMED]`

### Modular Ratio ($n$)
$$n = \frac{E_s}{E_c}$$
* $n$: Modular ratio `[CALCULATED]`
* $E_s$: Modulus of elasticity of reinforcement steel ($200\,000 \text{ MPa}$) `[GIVEN]`

### First Moment of Area Equilibrium ($Q_c = Q_s$)
First moment of transformed area about neutral axis determines neutral axis depth ($x$):
$$Q_c = Q_s \implies A_c x_c = n A_s x_s$$
$$\frac{1}{2} b x^2 = n A_s (d - x)$$
* $A_c$: Concrete compression area ($b \cdot x$) `[CALCULATED]`
* $x_c$: Distance from concrete compression area centroid to neutral axis ($x / 2$) `[CALCULATED]`
* $A_s$: Tension steel reinforcement area `[GIVEN]`
* $x_s$: Distance from tension steel centroid to neutral axis ($d - x$) `[CALCULATED]`

## File Structure

```
rc-flexure-theory/
├── flexure.py             # Elastic modulus, modular ratio, and NA depth module
├── PARAMETER_LEDGER.md    # Parameter provenance tracking
├── .gitignore             # Git ignore patterns
└── README.md              # Project documentation
```

## Quickstart

Run the Python self-check script:

```bash
python3 flexure.py
```

Expected output:
```
Self-check passed: f'c=28.0 MPa -> E_c=24870.06 MPa, n=8.04, x=164.30 mm (Q_c=4049393 mm^3, Q_s=4049393 mm^3)
```

## Parameter Provenance

All parameters require strict provenance tagging (`GIVEN`, `MEASURED`, `CALCULATED`, `CORRELATED`, `ADOPTED`, `ASSUMED`).
See [`PARAMETER_LEDGER.md`](PARAMETER_LEDGER.md) for full details.
