# Basic Flexure Theory for Reinforced Concrete

Calculates fundamental elastic parameters for reinforced concrete flexure analysis under working stress design.

## About

This repository provides core equations for concrete elastic modulus and modular ratio.
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

## File Structure

```
rc-flexure-theory/
├── flexure.py             # Elastic modulus and modular ratio module
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
Self-check passed: f'c=28.0 MPa -> E_c=24870.06 MPa, n=8.04
```

## Parameter Provenance

All parameters require strict provenance tagging (`GIVEN`, `MEASURED`, `CALCULATED`, `CORRELATED`, `ADOPTED`, `ASSUMED`).
See [`PARAMETER_LEDGER.md`](PARAMETER_LEDGER.md) for full details.
