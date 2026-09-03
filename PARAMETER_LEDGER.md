# Parameter Ledger

This ledger tracks all physical parameters for reinforced concrete flexure analysis.

| Parameter | Value | Unit | Provenance | Primary Source | Equation/Correlation | Used In |
|---|---:|---|---|---|---|---|
| $E_s$ | 200000 | MPa | GIVEN | NSCP 2015 Sec 408.5.2 | Steel elastic modulus | Modular ratio $n$ |
| $f'_c$ | 28 | MPa | ASSUMED | Standard design grade | Specified concrete strength | Concrete modulus $E_c$ |
| $E_c$ | 24870.06 | MPa | CORRELATED | NSCP 2015 Sec 419.2.2.1 | $E_c = 4700\sqrt{f'_c}$ | Modular ratio $n$ |
| $n$ | 8.04 | - | CALCULATED | Derived ratio | $n = E_s / E_c$ | Transformed section |
| $b$ | 300 | mm | ASSUMED | Example beam section | Beam width | Neutral axis depth $x$ |
| $d$ | 500 | mm | ASSUMED | Example beam section | Effective depth | Neutral axis depth $x$ |
| $A_s$ | 1500 | mm² | ASSUMED | Example rebar area | Steel area | Neutral axis depth $x$ |
| $x$ | 164.30 | mm | CALCULATED | Derived quadratic root | $\frac{1}{2} b x^2 + n A_s x - n A_s d = 0$ | Neutral axis depth |
| $Q_c$ | 4049393 | mm³ | CALCULATED | Derived moment | $A_c x_c = (b x)(x/2)$ | First moment equilibrium |
| $Q_s$ | 4049393 | mm³ | CALCULATED | Derived moment | $n A_s x_s = n A_s (d - x)$ | First moment equilibrium |
