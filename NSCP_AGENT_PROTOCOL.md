# NSCP 2015 Study Agent & Reviewer Protocol

This protocol defines the study guidelines, indexing workflow, and engineering review rules for the **NSCP 2015 Code Agent**.

## 1. Primary Source & Location

* **Primary Code Document**: National Structural Code of the Philippines (NSCP 2015, Volume I: Buildings, Towers, and Other Vertical Structures, 7th Edition).
* **PDF File Location**: `/Users/kerwinarlan/Downloads/PDFs/NSCP-2015.pdf` (1,008 pages, scanned PDF).
* **Knowledge Base Directory**: `/Users/kerwinarlan/github/rc-flexure-theory/nscp2015_knowledge_base/`
* **Extraction Tool**: `nscp_indexer.py` (PyMuPDF + Tesseract OCR pipeline).

## 2. Chapter Map & Code Provisions

| Chapter | Title | Key Engineering Provisions |
|---|---|---|
| **Chapter 1** | General Requirements | Structural occupancy categories, inspection, design documentation. |
| **Chapter 2** | Minimum Design Loads | Load combinations (Sec 203), Dead/Live loads (Sec 204/205), Wind loads (Sec 207), Seismic loads (Sec 208 ELF procedure). |
| **Chapter 3** | Earthworks & Foundations | Allowable bearing capacities, shallow rafts, deep piles, seismic hazards. |
| **Chapter 4** | Structural Concrete | Material properties ($E_c = 4700\sqrt{f'_c}$, $f_r = 0.62\sqrt{f'_c}$ Sec 419), Flexure (USD Sec 422, WSD Sec 424), Shear (Sec 411/422), Seismic detailing (Sec 418/18). |
| **Chapter 5** | Structural Steel | AISC 360 alignment, tension, compression, flexure, connections. |

## 3. Study & Indexing Workflow

To study and index specific chapters cover-to-cover:

```bash
# Extract pages 100-150 into the knowledge base
python3 nscp_indexer.py --extract 100 150 chapter_2_loads.md

# Search indexed knowledge base for specific terms or section numbers
python3 nscp_indexer.py --search "flexure"
python3 nscp_indexer.py --search "419.2.2.1"
```

## 4. Agent Execution & Review Rules

When acting as the **NSCP 2015 Specialist Agent**:

1. **Exact Section Citation**:
   Every code claim or equation must cite its specific NSCP 2015 provision (e.g. `NSCP 2015 Sec. 419.2.2.1`, `NSCP 2015 Sec. 422.2.2.4`, `NSCP 2015 Table 208-11A`).

2. **Parameter Provenance Tagging**:
   Every numerical parameter must use explicit provenance tags (`GIVEN`, `MEASURED`, `CALCULATED`, `CORRELATED`, `ADOPTED`, `ASSUMED`). Never present orphan numbers.

3. **Dual Unit Discipline**:
   Support both SI Metric ($E_c = 4700\sqrt{f'_c} \text{ MPa}$, $\text{kN}\cdot\text{m}$, $\text{rad/m}$) and US Customary ($E_c = 57\sqrt{f'_c} \text{ ksi}$, $\text{kip-in}$, $1/\text{in}$).

4. **Classroom & Defense Rigor**:
   Present calculations in step-by-step order:
   * Step 1: Material & Section Parameters
   * Step 2: Uncracked Elastic Stage (Region O->C)
   * Step 3: Cracked Elastic Stage (Region C->Y)
   * Step 4: Inelastic Ultimate Strength Stage (Region Y->U)
   * Step 5: Curvature Ductility Ratio ($\mu_\phi = \phi_u / \phi_y$)

5. **Self-Check & Verification Gate**:
   Every script or module must include a runnable headless self-check (`self_check()`) verifying calculations against known hand-derived values.
