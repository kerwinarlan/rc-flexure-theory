# Parameter Ledger

This ledger tracks all physical parameters for reinforced concrete flexure analysis.

| Parameter | Value | Unit | Provenance | Primary Source | Equation/Correlation | Used In |
|---|---:|---|---|---|---|---|
| $E_s$ | 200000 | MPa | GIVEN | NSCP 2015 Sec 408.5.2 | Steel elastic modulus | Modular ratio $n$ |
| $f'_c$ | 28 | MPa | ASSUMED | Standard design grade | Specified concrete strength | Concrete modulus $E_c$ |
| $E_c$ | 24870.06 | MPa | CORRELATED | NSCP 2015 Sec 419.2.2.1 | $E_c = 4700\sqrt{f'_c}$ | Modular ratio $n$ |
| $n$ | 8.04 | - | CALCULATED | Derived ratio | $n = E_s / E_c$ | Transformed section |
