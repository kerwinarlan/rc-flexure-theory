# Parameter Ledger (NSCP 2015)

This ledger tracks all physical parameters for reinforced concrete flexure analysis per NSCP 2015 Volume I.

| Parameter | Value | Unit | Provenance | Primary Source | Equation / Standard Provision | Used In |
|---|---:|---|---|---|---|---|
| $E_s$ | 200000 | MPa | GIVEN | NSCP 2015 Sec 420.2.2.1 | Steel elastic modulus | Modular ratio $n$ |
| $f'_c$ | 28 | MPa | ASSUMED | Standard design grade | Specified compressive strength | Concrete modulus $E_c$, $\beta_1$ |
| $E_c$ | 24870.06 | MPa | CORRELATED | NSCP 2015 Sec 419.2.2.1 | $E_c = 4700\sqrt{f'_c}$ | Modular ratio $n$ |
| $n$ | 8.04 | - | CALCULATED | NSCP 2015 Sec 424.5.2 | $n = E_s / E_c$ | Transformed section |
| $\beta_1$ | 0.85 | - | CALCULATED | NSCP 2015 Sec 422.2.2.4 | $\beta_1 = 0.85 - 0.05(f'_c - 28)/7$ | Stress block depth |
| $b$ | 300 | mm | ASSUMED | Beam design geometry | Section width | Neutral axis depth $x$, $I_{cr}$ |
| $d$ | 500 | mm | ASSUMED | Beam design geometry | Effective depth | Neutral axis depth $x$, $I_{cr}$ |
| $A_s$ | 1500 | mm² | ASSUMED | Reinforcement layout | Steel area | Neutral axis depth $x$, $I_{cr}$ |
| $x$ | 164.30 | mm | CALCULATED | NSCP 2015 Sec 424.5 | $\frac{1}{2} b x^2 + n A_s x - n A_s d = 0$ | Neutral axis depth |
| $Q_c$ | 4049393 | mm³ | CALCULATED | NSCP 2015 Sec 424.5 | $A_c x_c = (b x)(x/2)$ | First moment equilibrium |
| $Q_s$ | 4049393 | mm³ | CALCULATED | NSCP 2015 Sec 424.5 | $n A_s x_s = n A_s (d - x)$ | First moment equilibrium |
| $I_{cr}$ | $1.804 \times 10^9$ | mm⁴ | CALCULATED | NSCP 2015 Sec 424.5 | $I_{cr} = \frac{1}{3} b x^3 + n A_s (d - x)^2$ | Service stress calculation |
| $f_c$ | 9.11 | MPa | CALCULATED | NSCP 2015 Sec 424.5 | $f_c = M x / I_{cr} \le 0.45 f'_c$ | Concrete service stress |
| $f_s$ | 149.73 | MPa | CALCULATED | NSCP 2015 Sec 424.5 | $f_s = n M (d - x) / I_{cr} \le 0.50 f_y$ | Steel service stress |
