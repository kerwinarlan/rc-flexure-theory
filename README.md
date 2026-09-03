# Basic Flexure Theory for Reinforced Concrete (NSCP 2015 / ACI 318)

Calculates fundamental elastic (WSD), inelastic (USD), balanced reinforcement ($\rho_b, \rho_{max}$), and continuous fiber-integrated 3-region moment-curvature ($M - \phi$) flexural parameters for reinforced concrete beams per NSCP 2015 Volume I and ACI 318.

## About

This repository provides core equations for concrete elastic modulus, modular ratio, neutral axis depth, working stresses, ultimate strength capacity ($\phi M_n$), and continuous moment-curvature response.
It solves classic university flexure problems including **CE 152 Example 3** ($a=103.76\text{ mm}$), **CE 152 Slide 35 Balanced Condition** ($c_{bal}=338.24\text{ mm}, \rho_b=2.83\%$), and **CE 152 Slide 5425** ($M_{max}=2800\text{ kip-in}$ to $6200\text{ kip-in}$).
It supports both **US Customary units** ($\text{kip-in}, 1/\text{in}, \text{ksi}, \text{in}$) and **SI Metric units** ($\text{kN}\cdot\text{m}, \text{rad/m}, \text{MPa}, \text{mm}$).
The application includes a desktop solver GUI with **Interactive Parametric $M - \phi$ Variable Dropdowns** ($A_s, d, f'_c, b, f_y$), **Step-by-Step Board Solution Cards** (aligned $=$ signs), **Whitney UDL stress block diagrams** ($C \leftarrow$, $T \rightarrow$), and **LaTeX math derivation cards** built with `FreeSimpleGUI` and `matplotlib` following Engr. Jaydee Lucero's design pattern.
It also includes an **NSCP 2015 OCR Indexer System** (`nscp_indexer.py`) for cover-to-cover PDF study and knowledge extraction.

All calculations follow the National Structural Code of the Philippines (NSCP 2015, 7th Edition) and ACI 318.

## Parametric $M - \phi$ Variable Comparison ($A_s, d, f'_c, b, f_y$)

The GUI dropdown allows plotting continuous moment-curvature curves across 5 design variables:

1. **Steel Area ($A_s$)**: Increasing $A_s$ increases $M_n$ (taller curve) but reduces ultimate curvature $\phi_u$ (less ductile).
2. **Effective Depth ($d$)**: Increasing $d$ increases internal moment arm $(d - a/2)$ and flexural capacity $M_n$.
3. **Concrete Strength ($f'_c$)**: Increasing $f'_c$ reduces stress block depth $a$, increasing concrete strain margin.
4. **Beam Width ($b$)**: Increasing $b$ increases compression area, reducing stress block depth $a$.
5. **Steel Yield Strength ($f_y$)**: Increasing $f_y$ increases yield strain $\epsilon_y = f_y / E_s$ and yield moment $M_y$.

## Three Flexural Behavior Regions

The flexural behavior of a reinforced concrete section spans three distinct physical regions:

1. **Region O $\rightarrow$ C: Stresses Elastic, Section Uncracked** ($0 \le M \le M_{cr}$)
   * Concrete remains uncracked in tension. Response governed by gross flexural rigidity $E_c I_g$.
   * Cracking limit: $M_{cr} = \frac{f_r I_g}{y_t}$ where $f_r = 0.62 \sqrt{f'_c} \text{ MPa}$ ($7.5\sqrt{f'_c} \text{ psi}$) `[NSCP 2015 Sec. 419.2.3.1 / ACI 318]`.

2. **Region C $\rightarrow$ Y: Stresses Elastic, Section Cracked** ($M_{cr} < M \le M_y$)
   * Concrete cracks in tension. Response governed by transformed cracked flexural rigidity $E_c I_{cr}$.
   * Neutral axis depth $x$ determined by first moment equilibrium $Q_c = Q_s \implies \frac{1}{2} b x^2 = n A_s (d - x)$ `[NSCP 2015 Sec. 424.5]`.
   * Steel yield limit: $M_y = \frac{f_y I_{cr}}{n (d - x)}$.

3. **Region Y $\rightarrow$ U: Stresses Inelastic, Section Cracked** ($M_y < M \le M_n$)
   * Concrete enters non-linear compressive range modeled by Whitney rectangular UDL stress block ($a = \beta_1 c$).
   * Equilibrium: $C = 0.85 f'_c b a \leftarrow = T = A_s f_s \rightarrow$ `[NSCP 2015 Sec. 422.2]`.
   * Nominal capacity: $M_n = A_s f_s \left(d - \frac{a}{2}\right)$, Curvature ductility ratio: $\mu_\phi = \frac{\phi_u}{\phi_y}$.

## Balanced Condition Equations (Slide 35)

$$c_{bal} = \left( \frac{\epsilon_{cu}}{\epsilon_{cu} + \epsilon_y} \right) d = \left( \frac{600}{600 + f_y} \right) d \quad \text{[SI]}$$
$$a_{bal} = \beta_1 c_{bal}, \quad A_{s,bal} = \frac{0.85 f'_c b a_{bal}}{f_y}, \quad \rho_b = \frac{0.85 \beta_1 f'_c}{f_y} \left( \frac{600}{600 + f_y} \right)$$
$$\rho_{max} = \frac{0.85 \beta_1 f'_c}{f_y} \left( \frac{0.003}{0.003 + 0.005} \right) = 0.375 \frac{0.85 \beta_1 f'_c}{f_y} \quad \text{[Tension-Controlled]}$$

## Key Formulas (LaTeX)

### 1. Concrete Elastic Modulus ($E_c$) and Modulus of Rupture ($f_r$)
$$E_c = 4700 \sqrt{f'_c} \text{ (SI)} \quad \text{or} \quad 57\,000 \sqrt{f'_c} \text{ (US)} \quad \text{[NSCP 2015 Sec. 419.2.2.1 / ACI 318]}$$
$$f_r = 0.62 \sqrt{f'_c} \text{ (SI)} \quad \text{or} \quad 7.5 \sqrt{f'_c} \text{ (US)} \quad \text{[NSCP 2015 Sec. 419.2.3.1 / ACI 318]}$$

### 2. Modular Ratio ($n$)
$$n = \frac{E_s}{E_c} \quad \text{[NSCP 2015 Sec. 424.5.2 / ACI 318]}$$

### 3. Elastic First Moment Equilibrium ($Q_c = Q_s$)
$$\frac{1}{2} b x^2 = n A_s (d - x) \quad \text{[NSCP 2015 Sec. 424.5 / ACI 318]}$$

### 4. Inelastic Whitney Stress Block ($a = \beta_1 c$)
$$C = 0.85 f'_c b a \leftarrow \quad = T = A_s f_s \rightarrow \quad \text{[NSCP 2015 Sec. 422.2 / ACI 318]}$$

### 5. Ultimate Flexural Strength ($\phi M_n$)
$$M_n = A_s f_s \left(d - \frac{a}{2}\right) \quad \text{[NSCP 2015 Sec. 422.2 / ACI 318]}$$

### 6. Moment - Curvature ($M - \phi$) Response and Ductility ($\mu_\phi$)
$$M_{cr} = \frac{f_r I_g}{y_t}, \quad \phi_{cr} = \frac{M_{cr}}{E_c I_g} \quad \text{[Region O->C]}$$
$$M_y = \frac{f_y I_{cr}}{n (d - x)}, \quad \phi_y = \frac{\epsilon_y}{d - x} \quad \text{[Region C->Y]}$$
$$\phi_u = \frac{\epsilon_u}{c} = \frac{0.003}{c}, \quad \mu_\phi = \frac{\phi_u}{\phi_y} \quad \text{[Region Y->U]}$$

## File Structure

```
rc-flexure-theory/
├── flexure.py                 # Core NSCP 2015 / ACI 318 flexure & fiber module (US/SI)
├── solver_gui.py              # FreeSimpleGUI solver GUI with Parametric M-phi plots
├── nscp_indexer.py            # NSCP 2015 PDF OCR study & search tool
├── NSCP_AGENT_PROTOCOL.md     # Agent study protocol & review guidelines
├── PARAMETER_LEDGER.md        # Parameter provenance tracking table
├── nscp2015_knowledge_base/   # OCR-extracted Markdown knowledge base
├── .gitignore                 # Git ignore patterns
└── README.md                  # Project documentation
```

## Quickstart

### Launch Desktop Solver GUI
```bash
python3 solver_gui.py
```

### Search NSCP 2015 PDF Knowledge Base
```bash
python3 nscp_indexer.py --search "flexure"
```

### Run Automated Headless Verification
```bash
python3 solver_gui.py --test
python3 flexure.py
```

Expected headless output:
```
Self-check passed:
  CE 152 Example 3 : a = 103.76 mm (expected 103.76 mm), c = 122.08 mm
  CE 152 Slide 35   : c_bal = 338.24 mm, rho_b = 2.83%
  Continuous M-phi : 59 points, M_n=2596.2 kip-in
  Ductility Ratio   : 4.76
solver_gui CE 152 Slide 5425 & Continuous Fiber M-phi check passed!
```

## Parameter Provenance

All parameters require strict provenance tagging (`GIVEN`, `MEASURED`, `CALCULATED`, `CORRELATED`, `ADOPTED`, `ASSUMED`).
See [`PARAMETER_LEDGER.md`](PARAMETER_LEDGER.md) for full details.
