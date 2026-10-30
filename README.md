# URM fragility curves

Code to get fragility curves for **unreinforced masonry (URM) buildings**, from:

> Monteferrante C., Salamida G., Mazzotti C., Buratti N. (2025). *Observational Seismic Fragility Models for Unreinforced Masonry Buildings Based on Building-by-Building Damage Data From the 2012 Emilia Earthquakes.* Earthquake Engineering & Structural Dynamics 54:2927-2946. https://doi.org/10.1002/eqe.70009

## What it does

You give it:
* the **construction year** of a building
* the **number of storeys**
* an **intensity measure** (a measure of how strong the shaking is) and its value in g

It gives you:
* the **fragility parameters** (`mu` and `sigma`)
* the **probability of damage**: how likely the building is to reach each damage state, from D1 (slight damage) to D5 (partial or total collapse)
* a **plot** of the fragility curves

It does not calculate the shaking itself. That value comes from your own hazard analysis.

## How to use it

1. Install the packages: `pip install -r requirements.txt`
2. Open the notebook: `jupyter notebook notebooks/fragility_curves.ipynb`

The notebook explains every step. To use the code directly:

```python
import urm_fragility as uf

# a 1940 building with 3 storeys, using PGA
mu, sigma = uf.get_fragility_parameters(1940, 3, "PGA")
P = uf.exceedance_probabilities(1940, 3, 0.25, "PGA")   # PGA = 0.25 g
uf.plot_fragility(1940, 3, "PGA")
```

## Intensity measures

| Name | What it is |
|---|---|
| `PGA` | Peak ground acceleration |
| `Sa_0.3`, `Sa_0.75`, `Sa_1.5` | Spectral acceleration at **one** period (0.3, 0.75 or 1.5 s) |
| `Sa_avg` | **Average** spectral acceleration over periods 0.1 to 0.5 s |

Use each one with its own name. `Sa_avg` is not the same as the single-period Sa values.

## Things to watch out for

* Intensity values must be in **g**.
* 5 or more storeys count as 5.
* Results are the probability of damage **given** a shaking level. They are not annual probabilities.
* The curves come from the 2012 Emilia earthquakes (northern Italy) and URM buildings only.

## Files

* `urm_fragility.py`: the code
* `data/`: the PGA fragility parameters from the paper (Table 13)
* `notebooks/fragility_curves.ipynb`: worked example

For PGA, the parameters come straight from the paper. For the Sa measures, the paper gives a regression model instead, and `urm_fragility.py` calculates the parameters from it.

## Validation

The paper prints fragility parameters (`mu` and `sigma`) for PGA, but not for the Sa measures. For Sa it gives a regression model (Table 11), and the parameters in this code are calculated from that model.

To check the method, the same regression equations were applied to **PGA**, where the paper's printed parameters (Table 13) are known, and the results were compared with the table. This was done for all 45 building classes (9 construction-age classes × 5 storey classes). The largest differences were about 0.004 for `mu` and 0.001 for `sigma`. The small differences come from the paper rounding its regression coefficients to 3 decimal places.

This confirms the method (the regression equations, the age and storey variables, the unit conversion and the log base 10 convention). The Sa results use the same equations with the Sa coefficients, so they are supported by this check. However, the paper has no printed Sa parameters, so the Sa results could not be compared against a table directly.
