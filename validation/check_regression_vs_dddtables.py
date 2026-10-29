"""Checks that the Table 11 regression reproduces the lognormal parameters in Tables 12 and 13.
Run from the package folder:  python validation/check_regression_vs_tables.py"""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import urm_fragility as uf

# Table 11 columns for PGA and INp: gamma_0,1..5, then gamma_1..gamma_17 (None = term removed)
N = None
T11 = {
 "PGA": [6.291,6.817,7.110,7.397,8.245, -0.152,0.096,-2.415,-0.732,0.312,-0.283,-1.414,N,0.208,-0.247,-1.969,0.397,-0.291,1.093,0.096,0.775,-0.166],
 "INp": [6.950,7.506,7.812,8.114,8.905, -0.431,0.340,-2.399,-0.803,0.354,-0.384,-0.994,-0.303,0.237,N,-1.788,0.202,-0.117,0.622,0.016,0.689,-0.099],
}

def regression(im, year, Ns):
    c = [0.0 if v is None else v for v in T11[im]]
    g0, g = np.array(c[:5]), [None] + c[5:]
    a = uf.AGE_VALUES[np.searchsorted(uf.AGE_LIMITS, year)]
    n = (min(Ns, 5) - 3) / 2
    off = g[1]*a + g[2]*n + g[4]*a*n + g[7]*a**2 + g[8]*n**2 + g[10]*a**2*n + g[11]*a*n**2 + g[14]*a**2*n**2
    sl = g[3] + g[5]*a + g[6]*n + g[9]*a*n + g[12]*a**2 + g[13]*n**2 + g[15]*a**2*n + g[16]*a*n**2 + g[17]*a**2*n**2
    return -(g0 + off) / sl - np.log10(981.0), 1 / abs(sl)

for im, df in uf.TABLES.items():
    dmu, dsig = [], []
    for r in df.itertuples():
        mu, sig = regression(im, max(r.year_min, 1900), r.Ns)
        dmu.append(np.abs(mu - [r.mu_D1, r.mu_D2, r.mu_D3, r.mu_D4, r.mu_D5]).max())
        dsig.append(abs(sig - r.sigma))
    print(f"{im:4s}  max |mu diff| = {max(dmu):.4f}   max |sigma diff| = {max(dsig):.4f}")
