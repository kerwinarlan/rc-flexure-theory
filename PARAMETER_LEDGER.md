# Parameter Ledger (NSCP 2015)

This ledger tracks all physical parameters for reinforced concrete flexure analysis per NSCP 2015 Volume I.

| Parameter | Value | Unit | Provenance | Primary Source | Equation / Standard Provision | Used In |
|---|---:|---|---|---|---|---|
| $E_s$ | 200000 | MPa | GIVEN | NSCP 2015 Sec 420.2.2.1 | Steel elastic modulus | Modular ratio $n$, $\epsilon_y$ |
| $\epsilon_u$ | 0.003 | - | GIVEN | NSCP 2015 Sec 422.2.2.1 | Ultimate concrete compressive strain | Inelastic strain distribution |
| $f'_c$ | 28 | MPa | ASSUMED | Standard design grade | Specified compressive strength | Concrete modulus $E_c$, $\beta_1$, Whitney block |
| $f_y$ | 420 | MPa | ASSUMED | Grade 420 steel | Specified yield strength | Nominal capacity $M_n$, $\epsilon_y$ |
| $E_c$ | 24870.06 | MPa | CORRELATED | NSCP 2015 Sec 419.2.2.1 | $E_c = 4700\sqrt{f'_c}$ | Modular ratio $n$ |
| $n$ | 8.04 | - | CALCULATED | NSCP 2015 Sec 424.5.2 | $n = E_s / E_c$ | Transformed elastic section |
| $\beta_1$ | 0.85 | - | CALCULATED | NSCP 2015 Sec 422.2.2.4 | $\beta_1 = 0.85 - 0.05(f'_c - 28)/7$ | Whitney stress block depth |
| $b$ | 300 | mm | ASSUMED | Beam design geometry | Section width | Neutral axis $x, c$, $I_{cr}$, $M_n$ |
| $d$ | 500 | mm | ASSUMED | Beam design geometry | Effective depth | Neutral axis $x, c$, $I_{cr}$, $M_n$ |
| $A_s$ | 1500 | mm² | ASSUMED | Reinforcement layout | Tension steel area | Neutral axis $x, c$, $I_{cr}$, $M_n$ |
| $x$ | 164.30 | mm | CALCULATED | NSCP 2015 Sec 424.5 | $\frac{1}{2} b x^2 + n A_s x - n A_s d = 0$ | Elastic neutral axis depth |
| $Q_c$ | 4049393 | mm³ | CALCULATED | NSCP 2015 Sec 424.5 | $A_c x_c = (b x)(x/2)$ | First moment equilibrium |
| $Q_s$ | 4049393 | mm³ | CALCULATED | NSCP 2015 Sec 424.5 | $n A_s x_s = n A_s (d - x)$ | First moment equilibrium |
| $I_{cr}$ | $1.804 \times 10^9$ | mm⁴ | CALCULATED | NSCP 2015 Sec 424.5 | $I_{cr} = \frac{1}{3} b x^3 + n A_s (d - x)^2$ | Service stress calculation |
| $f_c$ | 9.11 | MPa | CALCULATED | NSCP 2015 Sec 424.5 | $f_c = M x / I_{cr} \le 0.45 f'_c$ | Concrete service stress |
| $f_s$ | 149.73 | MPa | CALCULATED | NSCP 2015 Sec 424.5 | $f_s = n M (d - x) / I_{cr} \le 0.50 f_y$ | Steel service stress |
| $c$ | 103.81 | mm | CALCULATED | NSCP 2015 Sec 422.2 | $0.85 f'_c b \beta_1 c = A_s f_s$ | Inelastic neutral axis depth |
| $a$ | 88.24 | mm | CALCULATED | NSCP 2015 Sec 422.2.2.4 | $a = \beta_1 c$ | Whitney stress block depth |
| $\epsilon_s$ | 0.01145 | - | CALCULATED | NSCP 2015 Sec 422.2 | $\epsilon_s = 0.003(d - c)/c$ | Tension steel net strain |
| $\phi$ | 0.90 | - | CALCULATED | NSCP 2015 Sec 421.2.2 | $\phi = 0.90 \text{ for } \epsilon_t \ge 0.005$ | Flexural strength reduction factor |
| $M_n$ | 287.21 | kN·m | CALCULATED | NSCP 2015 Sec 422.2 | $M_n = A_s f_s (d - a/2)$ | Nominal flexural strength |
| $\phi M_n$ | 258.49 | kN·m | CALCULATED | NSCP 2015 Sec 421.2 | $\phi M_n = \phi \cdot M_n$ | Design flexural strength |
