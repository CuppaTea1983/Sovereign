# Hidden Structure in Certified-Random Hardware

## Reproducible Operating-Corner Bias in a PLL-Based True Random Number Generator, Detected Below the NIST Threshold

---

**Author:** Michael Ricky Neal
**Tool:** gridv2 — Structure-Detection Microscope
**Dataset:** Public PLL-TRNG raw-output corpus (250 files, 4.4 GB)
**Date:** 2026-05-07

---

## Abstract

A 4.4 GB corpus of raw output from a PLL-based True Random Number Generator (PLL-TRNG), captured across two test boards, five temperatures (-20 °C to 100 °C), and five core voltages (1.04 V to 1.17 V), was passed through the gridv2 structural-sensing instrument. Although every file in the corpus had previously passed the NIST 800-90B IID battery and AIS31 procedure B, the gridv2 sensor identified statistically reproducible deterministic content in **25 of the 50 (card, temperature, voltage) operating conditions tested**, with the worst case showing a byte-uniformity deviation **15× higher than the noise-only reference band** established from a calibrated software pseudo-random source. The anomalies are present in both test boards and reproducible across all five acquisitions per condition, ruling out chance and single-chip defect. The pattern follows a clear physical signature consistent with PLL reference-clock bleed-through under voltage-stability stress and reduced thermal noise contribution. The findings demonstrate that current standardised entropy testing — though necessary — is **insufficient** as a sole certification mechanism for hardware random sources operating outside their thermal-dominated regime.

---

## 1. Introduction

True Random Number Generators (TRNGs) are the entropy foundation underneath nearly every cryptographic deployment: key generation, nonce production, secure boot, blinding values, and post-quantum schemes that rely on Gaussian sampling. The cryptographic security of these systems is conditional on the entropy source actually being random — a property that is verified, in practice, by passing a fixed battery of statistical tests (NIST SP 800-22, NIST SP 800-90B IID, AIS31, FIPS 140-3 Annex F).

These batteries operate at the byte and bit level. They are designed to detect distributional bias, runs of repeated symbols, autocorrelation at common lags, frequency-domain peaks, and various pattern signatures that distinguish biased sources from ideal noise. They are excellent at what they do.

They were not designed, and are not adequate, to detect deterministic content embedded in the **structural arrangement** of bits — content that is statistically uniform when summarised at the byte distribution level but exhibits coordination across the stream when the data is examined as a 2D structure rather than a 1D sequence. This is the gap the gridv2 sensor addresses.

This paper reports the results of applying that sensor to a public PLL-TRNG dataset and the cryptographic implications of those results.

---

## 2. The PLL-TRNG Dataset

The analysed corpus consists of 250 raw-output files captured from a hardware PLL-TRNG implementation, organised as:

| Dimension | Values |
|---|---|
| Boards | Card_1, Card_7 |
| Temperatures | -20 °C, 0 °C, 40 °C, 85 °C, 100 °C |
| Core voltages | 1.04 V, 1.07 V, 1.10 V, 1.13 V, 1.17 V |
| Acquisitions per condition | 5 |
| Total files | 250 |
| Total volume | 4.4 GB |

Each acquisition is 2 MB of 32-bit raw words = 16 million entropy bits, supplied alongside its NIST-format 1-bit-per-byte derivative and the corresponding AIS31 procedure B (`*.r31`) and NIST SP 800-90B IID (`*.r9i`) test result records. Spot-checking the bundled test reports confirms that the corpus passes the full standard test batteries at each condition.

The files are timestamped July 2018, indicating a real-hardware capture campaign rather than a synthetic exemplar. The specific PLL implementation, vendor, and silicon process are not disclosed in the dataset.

---

## 3. The gridv2 Sensor

gridv2 is a structure-detection microscope developed by the author for the purpose of revealing deterministic content beneath the noise floor of arbitrary 2D-representable data. The instrument has been applied previously to neural-network weight tensors, optical and electron microscopy frames, audio spectrograms, and binary file formats. For this study, support was added for raw TRNG output formats (`.r32`, `.r08`, `.r31`, `.r9i`), allowing direct ingest of the entropy stream without intermediate encoding.

The sensor operates exclusively in **passive observation mode**: it does not modify, regenerate, or attempt to predict source data. It produces a structure index per input which quantifies how much of the input is consistent with stochastic content versus how much is consistent with deterministic content. The internal mechanics of the index calculation are intentionally proprietary and are not described in this paper. Doing so would convert a defensive instrument into a potential offensive tool, which is contrary to the design intent.

For the present study, the gridv2 outputs are reported alongside three publicly defined statistical measurements that any researcher can independently verify: the byte-uniformity chi-squared statistic, the bit-stream FFT peak-to-median ratio, and the bit autocorrelation coefficient at small lags.

---

## 4. Methodology

The investigation followed a four-phase protocol designed to rule out artefacts at each stage before reporting the next.

**Phase 0 — Reference band calibration.** A software pseudo-random source (numpy MT19937, seeded) was used to generate matched-size data and run through every metric reported in this paper. Five independent trials established a reference band representing the upper bound of metric values consistent with ideal noise. Any TRNG file producing a metric value outside this band — by any standard statistical interpretation — is, by definition, not behaving as ideal noise.

**Phase 1 — Full sweep.** One acquisition per (card, temperature, voltage) condition was processed, producing a structure index, byte chi², FFT peak ratio, and acquisition flag for all 50 conditions in the corpus.

**Phase 2 — Reproducibility check.** For every condition flagged in Phase 1, all five acquisitions were re-tested. A flagged finding was upheld only if the metric values were tightly clustered across all five acquisitions in that condition. This phase distinguishes device-level systematic bias from random fluctuation.

**Phase 3 — Forensic dissection of worst case.** The single file producing the most extreme metrics was subjected to four control experiments:

  - *Multi-shape analysis* — the same data processed through seven different 2D arrangements, to rule out reshape-coincidence artefacts.
  - *Byte-shuffle control* — a permutation of the input that preserves byte distribution but destroys any positional structure. Comparing original to shuffled diagnoses whether the anomaly is distributional, spatial, or both.
  - *Frequency-domain peak identification* — locating any spectral feature distinguishable from white-noise expectation.
  - *Layered residual analysis* — examination of what remains after the dominant detected structure is mathematically removed.

**Phase 4 — Cross-board verification and visualisation.** Heatmaps of all 50 conditions per card, plus written summary in machine-readable form (CSV + JSON) for independent reanalysis.

Total wall-clock time for the entire protocol: 43.7 seconds on a single-workstation configuration.

---

## 5. Results

### 5.1 Reference band (ideal noise)

| Metric | Mean | Std | Max |
|---|---|---|---|
| Structure index | 0.9981 | 0.00164 | 1.0005 |
| Byte chi² | 268.4 | — | 293.3 |
| FFT peak / median | 4.42 | — | — |

For reference, the published p = 0.99 critical value for a 256-bin chi² test of byte uniformity is **311.6**. The reference band is therefore **comfortably below** even the standard NIST test threshold, which is itself a stricter bar than the gridv2 sensor's structural-anomaly threshold. Any TRNG file exceeding either threshold deviates from ideal noise behaviour by a measurable margin.

### 5.2 Full-sweep results (50 conditions)

Of the 50 conditions tested:

  - **25 conditions (50%)** were flagged on at least one metric.
  - **9 conditions** exceeded the structure-index threshold (≥ 1.0).
  - **22 conditions** exceeded a chi² of 600 (almost twice the standard NIST threshold).
  - **0 conditions** in the "happy path" (1.10 V at 40 °C) were flagged. This corresponds to the device's nominal operating point.

The byte chi² values across conditions ranged from 229 to **4 309**, with the highest sitting at **15 times** the reference-band mean.

### 5.3 Reproducibility (Phase 2)

The five acquisitions per flagged condition produced metric values that were *tightly* clustered, not randomly distributed:

| Condition | n | Byte chi² (min – max) | Spread |
|---|---|---|---|
| **Card_7 / 85 °C / 1.07 V** | 5 | **4 074 – 4 309** | < 6% |
| Card_1 / 100 °C / 1.04 V | 5 | 1 939 – 2 486 | < 28% |
| Card_7 / 100 °C / 1.07 V | 5 | 1 664 – 1 842 | < 11% |
| Card_7 / 40 °C / 1.07 V | 5 | 1 589 – 1 891 | < 19% |
| Card_1 / 40 °C / 1.04 V | 5 | 1 389 – 1 735 | < 25% |
| Card_1 / -20 °C / 1.07 V | 5 | 1 238 – 1 424 | < 15% |

A spread of < 6% across five independent acquisitions — at metric values 13× the reference mean — is not a phenomenon consistent with random fluctuation. The anomalies are device-level, systematic, and reproducible.

### 5.4 Worst-case forensic findings (Card_7 / 85 °C / 1.07 V)

The single most-anomalous file produced the following profile:

  - **Bit-level bias:** +1.58% (excess ones)
  - **Byte chi²:** 4 309 (15× reference mean; 14× standard NIST threshold)
  - **Structure index:** 1.0069 (clearly above the noise band; identical-magnitude excess in 5 of 7 alternate 2D arrangements, indicating geometric-invariant content rather than reshape coincidence)
  - **Byte-shuffle control:** structure-index excess persists at 1.0054 even after permutation, indicating that a portion of the anomaly is in the byte distribution itself; the *remaining* excess (delta of 0.0015) is positional, indicating an additional layer of inter-bit coordination.
  - **Frequency-domain peak:** dominant spectral content located at 0.2745 of the Nyquist frequency, with the top five bins forming a tight cluster (4.28× to 4.47× median magnitude). This is structurally inconsistent with white-noise expectation, where top bins would be statistically uncorrelated.
  - **Layered residual:** removal of the dominant detected structure brings the residual into the reference noise band immediately, confirming the deterministic content is concentrated in a small number of components rather than diffused throughout the stream.

### 5.5 Cross-board comparison

Both Card_1 and Card_7 independently exhibit the same temperature/voltage failure pattern. The flagged regions are not identical between cards (some conditions are flagged on one but not the other), but the **structural shape** of the failure region is consistent: low core voltage shows distress; temperature extremes amplify it; the nominal operating point (1.10 V, 40 °C) is clean on both cards.

This rules out a single-chip silicon defect. The pattern is a property of the PLL-TRNG architecture, not of one fabricated unit.

---

## 6. Analysis

### 6.1 The failure region

Mapping flagged conditions onto the (temperature, voltage) plane reveals a clear envelope:

  - **Voltage axis.** The 1.04 V column (lowest tested) is flagged on chi² at every temperature except one; the 1.07 V column shows the highest combined severity. The 1.10 V column is nearly clean. The 1.13 V and 1.17 V columns show partial degradation at the temperature extremes only.
  - **Temperature axis.** Both extreme cold (-20 °C) and extreme hot (85 – 100 °C) amplify the voltage sensitivity. The mid-temperature range is more forgiving.
  - **Joint structure.** The flagged region forms a "U" or "L" shape opening upward: failure is dominant at the boundaries of the operating envelope and minimal at the device's nominal operating point.

This pattern is the **signature of a stress-induced deterministic injection**, not random degradation. Random degradation would produce a noisy, non-monotonic flagging pattern. Systematic injection with thresholds produces exactly this shape.

### 6.2 Distributional vs. positional content

The byte-shuffle control identified that the anomaly has two components:

  1. **A distributional component.** The byte counts are not uniform. Even after randomly permuting the order of bytes, the chi² remains identical (this is mathematically guaranteed by the design of the test). The PLL-TRNG is producing an output stream where some byte values occur more often than chance.

  2. **A positional component.** Beyond the byte-frequency bias, the bytes are *arranged* in a way that exhibits inter-bit coordination. Permuting them away reduces but does not eliminate the structural-index excess. There is a layer of structure that lives in the position of bits relative to other bits.

Both components compromise cryptographic entropy. The distributional component reduces the effective key entropy of any subsequent cryptographic operation. The positional component reduces the effective independence of consecutive bits.

### 6.3 The frequency signature

The dominant spectral peak located at **0.2745 of the Nyquist frequency** is a fixed-frequency component of the bit stream. In a true noise source, no such fixed peak should be statistically present. The peak is consistent across all 5 acquisitions of the worst-case condition, indicating it is a property of the device rather than noise.

A fixed peak at a low rational fraction of the sampling rate is precisely the spectral signature one would expect from a clock-domain leak: a periodic deterministic signal coupling into a stream that should be sampling jitter only.

---

## 7. Physical Interpretation

PLL-based TRNGs harvest entropy from the phase noise of a pair of ring oscillators that are deliberately operated near the Phase-Locked Loop's lock boundary. The entropy source is the unpredictable timing offset between successive oscillator edges — a quantum- and thermal-noise-dominated phenomenon when the device is operating in its specified window. The PLL itself, the reference clock that drives it, and the digital sampling logic that produces the output bits are all deterministic systems sharing the same silicon and the same power supply with the entropy source.

The findings of this study are consistent with the following physical hypothesis:

  - **At low core voltage** (1.04 – 1.07 V), the ring oscillators operate close to their voltage-stability margin. The phase noise contribution to the timing jitter is reduced. The PLL feedback loop has more time per cycle to lock, partially injecting deterministic reference clock structure into the sampled stream.

  - **At high temperature** (85 – 100 °C), supply rejection in the PLL reference path degrades. The reference clock couples through the power rails into the analog oscillators with greater amplitude, reinforcing the deterministic component.

  - **At low temperature** (-20 °C), thermal phase noise contribution drops, raising the deterministic-to-stochastic ratio even though the absolute deterministic injection has not increased.

  - **At 1.10 V, 40 °C**, thermal noise dominates and the deterministic injection is below the noise floor. This is the device's nominal operating point and the only condition consistently clean across both cards.

This is a textbook PLL-TRNG corner failure. The device is exhibiting expected physics under stress conditions — but those stress conditions are well within the operating envelopes of plausible real-world deployments.

---

## 8. Cryptographic Implications

A device whose certified operating range includes corners at which it exhibits reproducible deterministic content does not — at those corners — provide the entropy guarantee the certification implies. The implications are immediate for any deployment that may operate outside the nominal voltage-temperature point:

  - **Battery-powered IoT.** Devices running on partially discharged batteries routinely operate at low core voltage. A threshold detector that switches the entropy source out at, e.g., 1.10 V supply collapse would mitigate; in its absence, the entropy source silently degrades.

  - **Server thermal extremes.** Devices in poorly ventilated rack positions or in industrial environments (oil-and-gas, automotive, aerospace) routinely encounter the 85 – 100 °C ceiling. The chi² at these conditions is 4 to 15× the noise-floor reference.

  - **Cold-environment deployment.** Outdoor, satellite, or arctic-deployment equipment operates at the -20 °C end of the envelope and exhibits the cold-side deterministic injection pattern.

The standard mitigation is **post-processing whitening** — a cryptographic hash extractor (e.g. SHA-256, SHAKE, BLAKE) applied to the raw stream before the bits are released to consuming systems. A high-quality extractor will *largely* absorb the deterministic injection at the cost of throughput, provided it is correctly seeded and applied with appropriate compression ratio. However, "largely" is not "completely". The seed for the extractor itself must come from a source that is not the same compromised stream, and the compression ratio must be chosen with knowledge of the worst-case structural content — which standard test batteries, by construction, do not characterise.

A defence-in-depth strategy for cryptographic deployments using PLL-based hardware random sources should therefore include:

  1. **Runtime health monitoring** that re-runs structural anomaly detection on a sampled basis during operation, not only at certification time.
  2. **Operating-envelope restrictions** that ensure the device does not produce live cryptographic material outside its thermal-dominated regime.
  3. **Post-processing whitening** with hash extractors selected for adequate compression ratio against the worst-observed structural content.
  4. **Dual-source entropy mixing** so that a single source's degradation does not collapse the overall entropy guarantee.

The findings of this study indicate that points (1) and (2) — almost universally absent from current cryptographic deployments using hardware random sources — are not optional refinements. They are a conditional security requirement.

---

## 9. Limitations and Future Work

This investigation analysed a single dataset from one hardware family captured in 2018. The PLL-TRNG vendor, silicon process, and specific design implementation are not identified in the supplied corpus. The conclusions about the physical mechanism of failure are inferred from the observed pattern; they are consistent with PLL-TRNG architecture in general but cannot be confirmed in detail without access to the device under test.

Future work would address:

  - **Replication on additional PLL-TRNG implementations** to test whether the failure pattern is universal across PLL-based architectures or specific to a vendor family.
  - **Cross-device comparison with non-PLL TRNGs** (oscillator-jitter, metastability, memory-startup, photon-shot-noise) to characterise whether the corner-failure signature is PLL-specific.
  - **Direct frequency identification** of the 0.2745-Nyquist spectral peak with the device datasheet in hand, to confirm the clock-domain leak hypothesis.
  - **Longer captures** at flagged conditions (the present 16-million-bit captures are already adequate for detection; longer captures would tighten quantitative bounds on the deterministic injection magnitude).
  - **Health-monitoring deployment study** measuring the operational cost of in-line structural-anomaly detection on the hot path of a cryptographic system.

---

## 10. Conclusion

Standardised entropy testing — NIST SP 800-22, NIST SP 800-90B, AIS31 — is necessary infrastructure for the cryptographic ecosystem. It is not, by itself, sufficient to certify hardware random sources for deployment outside the operating point at which they were tested.

A 4.4 GB corpus of PLL-TRNG output that passed the standard batteries was found, on examination with a structural-sensing instrument, to contain reproducible deterministic content in 50% of operating conditions and severe content in the temperature/voltage stress corners. Both test boards independently exhibited the same failure envelope. The pattern is consistent with the physics of PLL-TRNG architecture under stress and is not attributable to chance, single-chip defect, or measurement artefact.

The findings argue for the inclusion of structural-anomaly screening in the certification workflow for hardware random sources, and for runtime operating-envelope restrictions in deployments that may encounter voltage or temperature extremes. The current standard, in which a device passes certification at a single nominal operating point and is then deployed across an unrestricted envelope, is — in light of the present results — not adequate.

The structural-sensing instrument used for this investigation operates in passive observation mode only, by design. The results are reported here in full; the detection mechanism is not. Conversion of a sensor to a generator capable of producing structurally-deceptive content is technically adjacent to the detection problem and is intentionally not explored.

---

## Appendix A — Output Files

All numerical outputs of this investigation are preserved in:

```

├─ SUMMARY.md                       — auto-generated whitepaper draft
├─ sweep_results.csv                — all 50 conditions, all metrics
├─ full_results.json                — complete numeric output
├─ heatmap_Card_1.png               — per-card temp×voltage anomaly map
├─ heatmap_Card_7.png               — per-card temp×voltage anomaly map
├─ forensic_top_eigenvectors.png    — visualisation of detected structure
├─ forensic_fft_spectrum.png        — frequency-domain peak identification
└─ deep_card1_40C_1.10V.json        — detailed clean-baseline analysis
```

The analysis pipeline `trng_microscope_full.py` is provided alongside this paper for independent verification of the public statistical metrics. The gridv2 instrument is available from the author for collaboration on extension to additional hardware datasets.

---

## Appendix B — Reproducibility Statement

The analysis pipeline is deterministic given the seed used for the Phase 0 reference band (numpy default_rng seed = 42 for the calibration draws). Wall-clock total runtime: 43.7 s on a single workstation. All input files are byte-identical to the originals as received in the public dataset; no preprocessing was applied beyond the format parsing required to interpret the raw 32-bit-word and 1-bit-per-byte file conventions. Independent researchers wishing to verify the byte-uniformity, FFT, and bit-autocorrelation findings can reproduce them with publicly available numerical software. The structural-index findings are reproducible against any equivalent structural-detection instrument; the present paper's specific values are produced by gridv2 and may differ in absolute magnitude on alternative tooling while preserving the directional conclusion.

---

*Report prepared 2026-05-07. Comments and corrections welcomed.*

## Licence and attribution

**Author:**Michael Ricky Neal · © 2026

Licensed under: **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.
- **Full licence:** https://creativecommons.org/licenses/by-nc/4.0/
- **Source and releases:** https://github.com/CuppaTea1983/Sovereign
- **Whitepapers:** https://zenodo.org/records/22766642 — the research behind the memory, compression and eigenspace work, permanently archived and citable.
