# Basic Flexure Theory for Reinforced Concrete (NSCP 2015 / ACI 318)

Calculates fundamental elastic (WSD), inelastic (USD), and 3-region moment-curvature ($M - \phi$) flexural parameters for reinforced concrete beams per NSCP 2015 Volume I and ACI 318.

## About

This repository provides core equations for concrete elastic modulus, modular ratio, neutral axis depth, working stresses, ultimate strength capacity ($\phi M_n$), and 3-region moment-curvature response.
It solves classic university flexure problems including **CE 152 Example 3** ($b=250\text{ mm}, d=575\text{ mm}, f'_c=28\text{ MPa}, f_y=420\text{ MPa}, A_s=1470\text{ mm}^2 \rightarrow a=103.76\text{ mm}$).
It supports both **US Customary units** ($\text{kip-in}, 1/\text{in}, \text{ksi}, \text{in}$) and **SI Metric units** ($\text{kN}\cdot\text{m}, \text{rad/m}, \text{MPa}, \text{mm}$).
The application includes a desktop solver GUI with **Step-by-Step LaTeX Solution Cards**, **Whitney UDL stress block diagrams** ($C \leftarrow$, $T \rightarrow$), and **LaTeX math derivation cards** built with `FreeSimpleGUI` and `matplotlib` following Engr. Jaydee Lucero's design pattern.
It also includes an **NSCP 2015 OCR Indexer System** (`nscp_indexer.py`) for cover-to-cover PDF study and knowledge extraction.

All calculations follow the National Structural Code of the Philippines (NSCP 2015, 7th Edition) and ACI 318.

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
├── flexure.py                 # Core NSCP 2015 / ACI 318 flexure module (US/SI)
├── solver_gui.py              # FreeSimpleGUI solver GUI with Step-by-Step LaTeX cards
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
  CE 152 Example 3: a = 103.76 mm (expected 103.76 mm), c = 122.08 mm
  US Customary: M_cr=480.3 kip-in, M_n=2596.2 kip-in
  Ductility Ratio (mu_phi): 4.76
solver_gui CE 152 Example 3 & Step-by-Step LaTeX check passed!
```

## Parameter Provenance

All parameters require strict provenance tagging (`GIVEN`, `MEASURED`, `CALCULATED`, `CORRELATED`, `ADOPTED`, `ASSUMED`).
See [`PARAMETER_LEDGER.md`](PARAMETER_LEDGER.md) for full details.
