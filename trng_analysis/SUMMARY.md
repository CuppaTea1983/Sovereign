# PLL-TRNG SVD-Microscope Analysis Summary

Generated: 2026-05-07 03:55:18

## Phase 0 — PRNG Baseline (numpy MT19937)

- ratio: mean=0.9981, std=0.00164, max=1.0005
- chi²:  mean=268.4, max=293.3
- fft peak/median: mean=4.42

This is the noise-only reference. ANY TRNG file falling outside this band on any of these metrics deviates from ideal random behaviour.

## Phase 1 — Sweep Results

- Total conditions analysed: 50
- Conditions exceeding any flag threshold: 25
- Threshold definitions: ratio >= 1.0, chi² >= 600.0, fft_peak/median >= 8.0

### Flagged conditions:

| Condition | ratio | n above edge | chi² | fft peak/med |
|-----------|-------|--------------|------|--------------|
| Card_7/85C/1.07V | 0.9953 | 0 | 4122 | 4.57 |
| Card_1/100C/1.04V | 1.0053 | 1 | 2486 | 4.60 |
| Card_1/100C/1.07V | 0.9964 | 0 | 2121 | 4.41 |
| Card_1/85C/1.10V | 0.9922 | 0 | 2121 | 4.53 |
| Card_1/85C/1.17V | 0.9954 | 0 | 2055 | 4.94 |
| Card_7/0C/1.04V | 1.0004 | 1 | 2039 | 4.39 |
| Card_7/100C/1.13V | 0.9987 | 0 | 2003 | 4.99 |
| Card_7/100C/1.07V | 1.0006 | 1 | 1751 | 4.42 |
| Card_7/40C/1.07V | 1.0008 | 1 | 1589 | 4.53 |
| Card_1/40C/1.04V | 0.9971 | 0 | 1544 | 4.71 |
| Card_1/100C/1.17V | 0.9988 | 0 | 1504 | 4.60 |
| Card_7/100C/1.04V | 0.9965 | 0 | 1453 | 4.52 |
| Card_7/85C/1.10V | 0.9932 | 0 | 1330 | 4.53 |
| Card_7/85C/1.04V | 0.9924 | 0 | 1284 | 4.74 |
| Card_1/-20C/1.07V | 1.0016 | 1 | 1238 | 5.07 |
| Card_1/85C/1.04V | 1.0020 | 1 | 1224 | 4.48 |
| Card_1/0C/1.07V | 1.0016 | 1 | 1136 | 4.63 |
| Card_7/100C/1.10V | 0.9979 | 0 | 1064 | 4.39 |
| Card_7/-20C/1.04V | 0.9981 | 0 | 1047 | 4.54 |
| Card_1/-20C/1.10V | 0.9999 | 0 | 1019 | 5.31 |
| Card_7/85C/1.13V | 0.9985 | 0 | 961 | 4.94 |
| Card_7/0C/1.17V | 0.9957 | 0 | 904 | 4.48 |
| Card_7/100C/1.17V | 0.9949 | 0 | 746 | 4.44 |
| Card_1/40C/1.17V | 0.9964 | 0 | 694 | 4.55 |
| Card_1/100C/1.13V | 1.0001 | 1 | 343 | 4.78 |

## Phase 2 — Reproducibility check

For each flagged condition, all acquisition files were re-tested.
If the anomaly is reproducible across acquisitions, it's a
device-level effect (not random fluctuation).

| Condition | n files | ratio min..max | chi² min..max |
|-----------|---------|----------------|----------------|
| Card_1/-20C/1.07V | 5 | 0.9964..1.0016 | 1238..1424 |
| Card_1/-20C/1.10V | 5 | 0.9932..0.9999 | 950..1084 |
| Card_1/0C/1.07V | 5 | 0.9950..1.0016 | 1098..1181 |
| Card_1/100C/1.04V | 5 | 0.9966..1.0053 | 1939..2486 |
| Card_1/100C/1.07V | 5 | 0.9912..1.0024 | 2073..2276 |
| Card_1/100C/1.13V | 5 | 0.9931..1.0001 | 303..414 |
| Card_1/100C/1.17V | 5 | 0.9955..0.9988 | 1358..1504 |
| Card_1/40C/1.04V | 5 | 0.9954..0.9986 | 1389..1735 |
| Card_1/40C/1.17V | 5 | 0.9896..0.9964 | 608..694 |
| Card_1/85C/1.04V | 5 | 0.9926..1.0020 | 1119..1311 |
| Card_1/85C/1.10V | 5 | 0.9922..0.9984 | 1970..2121 |
| Card_1/85C/1.17V | 5 | 0.9954..1.0040 | 2055..2270 |
| Card_7/-20C/1.04V | 5 | 0.9924..1.0026 | 944..1047 |
| Card_7/0C/1.04V | 5 | 0.9935..1.0004 | 1891..2205 |
| Card_7/0C/1.17V | 5 | 0.9921..0.9998 | 810..920 |
| Card_7/100C/1.04V | 5 | 0.9942..0.9991 | 1174..1585 |
| Card_7/100C/1.07V | 5 | 0.9915..1.0006 | 1664..1842 |
| Card_7/100C/1.10V | 5 | 0.9907..1.0021 | 1064..1370 |
| Card_7/100C/1.13V | 5 | 0.9957..0.9993 | 1792..2303 |
| Card_7/100C/1.17V | 5 | 0.9932..0.9989 | 746..808 |
| Card_7/40C/1.07V | 5 | 0.9957..1.0008 | 1589..1891 |
| Card_7/85C/1.04V | 5 | 0.9916..1.0037 | 1145..1288 |
| Card_7/85C/1.07V | 5 | 0.9953..1.0069 | 4074..4309 |
| Card_7/85C/1.10V | 5 | 0.9932..1.0025 | 1136..1349 |
| Card_7/85C/1.13V | 5 | 0.9957..1.0014 | 961..1168 |

## Phase 3 — Forensic dissection

Worst file: **Card_7/85C/1.07V**

`F:\Backup\raw data output from PLL-TRNG\Card_7\85C\1.07V\acq_20180716143130_4.r32`

### Multi-shape SVD

Same data, different reshape geometries. If anomaly
survives across shapes, it's content not coincidence.

| shape | ratio | above edge | chi² |
|-------|-------|------------|------|
| 2000×1000 | 1.0069 | 1 | 4309 |
| 1000×2000 | 0.9939 | 0 | 4309 |
| 500×4000 | 1.0009 | 1 | 4309 |
| 4000×500 | 1.0040 | 1 | 4309 |
| 250×8000 | 1.0010 | 1 | 4309 |
| 8000×250 | 1.0095 | 1 | 4309 |
| 200×10000 | 0.9959 | 0 | 4309 |

### Byte-shuffle control

Shuffling preserves byte distribution but destroys
spatial/positional structure. Comparing original to
shuffled diagnoses what *kind* of anomaly we have.

- Shuffled mean ratio: 1.0054
- Shuffled mean chi²:  4309
- Interpretation: SPATIAL: anomaly dies on shuffle

### FFT bleed-through detection

- Peak bin: 274525 of 1000000
- Peak as fraction of Nyquist: 0.274525
- Peak / median: 4.47

### Residual SVD (fractal depth)

Remove top-k components, look at what remains. If
residual ratio approaches 1.0, all structure was in top-k.

| k removed | residual std | residual top SV | residual ratio |
|-----------|--------------|-----------------|----------------|
| 1 | 73.801 | 5620.3 | 0.9975 |
| 2 | 73.694 | 5575.5 | 0.9910 |
| 3 | 73.589 | 5553.8 | 0.9886 |
| 4 | 73.485 | 5544.0 | 0.9882 |
| 5 | 73.380 | 5530.5 | 0.9872 |
| 6 | 73.276 | 5515.5 | 0.9859 |
| 7 | 73.172 | 5492.7 | 0.9832 |
| 8 | 73.069 | 5482.3 | 0.9828 |

## Output files

- `Card_1_40C_1.10V_acq0_svd.png`
- `cross_condition_sweep.json`
- `deep_card1_40C_1.10V.json`
- `forensic_fft_spectrum.png`
- `forensic_top_eigenvectors.png`
- `heatmap_Card_1.png`
- `heatmap_Card_7.png`
- `SUMMARY.md`
- `sweep_results.csv`
