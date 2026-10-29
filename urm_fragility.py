"""
Fragility curves for URM buildings (Monteferrante et al. 2025, EESD 54:2927-2946).

Intensity values are in g. Curves are lognormal in base 10:
    P(D >= Dk) = norm.cdf((log10(IM) - mu_k) / sigma)

IM names: "PGA", "INp", "Sa_avg" (average Sa over 0.1-0.5 s), "Sa_0.3", "Sa_0.75", "Sa_1.5"
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm

DATA = Path(__file__).resolve().parent / "data"
TABLES = {"PGA": pd.read_csv(DATA / "fragility_params_PGA.csv"),
          "INp": pd.read_csv(DATA / "fragility_params_INp.csv")}

SA_MODELS = ["Sa_avg", "Sa_0.3", "Sa_0.75", "Sa_1.5"]
LABELS = {"PGA": "PGA [g]", "INp": "INp [g]", "Sa_avg": "Average Sa, 0.1-0.5 s [g]",
          "Sa_0.3": "Sa(0.3 s) [g]", "Sa_0.75": "Sa(0.75 s) [g]", "Sa_1.5": "Sa(1.5 s) [g]"}

# Regression coefficients from paper Table 11 (columns follow SA_MODELS)
THRESHOLDS = np.array([[7.607, 7.530, 6.257, 5.646],
                       [8.168, 8.052, 6.721, 6.171],
                       [8.483, 8.355, 7.006, 6.470],
                       [8.801, 8.672, 7.312, 6.764],
                       [9.612, 9.468, 8.068, 7.603]])
OFFSET = np.array([[ 1.233, -0.454, -0.384, -0.040],
                   [-1.577,  0.334,  0.420, -0.100],
                   [ 0.000, -1.434, -1.461, -0.803],
                   [-1.718, -1.675, -1.523, -1.588],
                   [-0.555, -0.102,  0.158, -0.210],
                   [ 0.000, -1.097, -0.740, -0.395],
                   [-3.575, -1.182, -1.748, -1.559],
                   [-0.957,  1.597,  0.428,  1.088]])
SLOPE = np.array([[-2.588, -2.588, -2.410, -2.529],
                  [-0.231,  0.381,  0.421,  0.300],
                  [ 0.325, -0.347, -0.477, -0.188],
                  [-0.108,  0.439,  0.524,  0.267],
                  [ 0.440,  0.440,  0.468,  0.589],
                  [ 0.000, -0.222, -0.320, -0.138],
                  [ 0.020,  0.418,  0.346,  0.250],
                  [ 1.258,  0.413,  0.000,  0.653],
                  [ 0.530, -0.332,  0.639, -0.274]])

AGE_VALUES = [-1.044, -0.756, -0.289, 0.000, 0.244, 0.467, 0.689, 0.822, 0.956]   # Table 6
AGE_LIMITS = [1918, 1945, 1960, 1970, 1980, 1990, 2000, 2005]


def get_fragility_parameters(year, Ns, im):
    """Returns mu (5 values, D1-D5, log10 g) and sigma (one value)."""
    Ns = min(int(Ns), 5)
    if im in TABLES:
        df = TABLES[im]
        row = df[(df.year_min <= year) & (df.year_max >= year) & (df.Ns == Ns)].iloc[0]
        return row[["mu_D1", "mu_D2", "mu_D3", "mu_D4", "mu_D5"]].to_numpy(float), float(row.sigma)

    j = SA_MODELS.index(im)
    age = AGE_VALUES[np.searchsorted(AGE_LIMITS, year)]
    st = (Ns - 3) / 2
    terms = np.array([age, st, age*st, age**2, st**2, age**2*st, age*st**2, age**2*st**2])
    offset = terms @ OFFSET[:, j]
    slope = SLOPE[0, j] + terms @ SLOPE[1:, j]
    mu = -(THRESHOLDS[:, j] + offset) / slope - np.log10(981.0)   # regression is in cm/s2
    return mu, 1 / abs(slope)


def exceedance_probabilities(year, Ns, im_value, im):
    """Probability of reaching or exceeding D1-D5 (array of 5). im_value is in g."""
    mu, sigma = get_fragility_parameters(year, Ns, im)
    return norm.cdf((np.log10(im_value) - mu) / sigma)


def plot_fragility(year, Ns, im, mark=None, x_max=1.5):
    import matplotlib.pyplot as plt
    mu, sigma = get_fragility_parameters(year, Ns, im)
    x = np.linspace(0.001, x_max, 400)
    for k in range(5):
        plt.plot(x, norm.cdf((np.log10(x) - mu[k]) / sigma), label=f"D{k+1}")
    if mark is not None:
        plt.axvline(mark, ls="--", color="k")
    plt.xlabel(LABELS[im]); plt.ylabel("Probability of exceedance")
    plt.title(f"Built {year}, {Ns} storeys")
    plt.xlim(0, x_max); plt.ylim(0, 1); plt.grid(alpha=0.3); plt.legend()
    


