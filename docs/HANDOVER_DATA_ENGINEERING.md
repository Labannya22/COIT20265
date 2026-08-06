# Handover: dataset and data engineering

Work package 3.0. Prepared by Labannya Barua, 7 August 2026.

Covers the scheduled work for 3–7 August, 10–14 August and 17–21 August, all
of which is complete. Week labels below follow the team work distribution
sheet (calendar dates), not the teaching-week numbering used in Assessment 1.

---

## 1. Schedule position

| Scheduled week | Assigned work | Status |
|---|---|---|
| 3–7 Aug | Download and verify UNSW-NB15; inspect columns and types; check missing, duplicate and extreme values; draft portable feature list; start data dictionary | Complete |
| 10–14 Aug | Finalise portable features; split into normal training, normal validation and mixed testing; keep attack labels out of training; begin preprocessing pipeline; produce data-quality report | Complete |
| 17–21 Aug | Complete and save preprocessing; fit scaling and encoding on training data only; document feature order; provide processed sample to the model lead | Complete |
| 24–28 Aug | Review sample Zeek fields with Arjita; start dataset-to-Zeek mapping; document available, calculated, unavailable and differently defined fields | Drafted, awaiting Arjita |

Three weeks of scheduled work is finished. The processed sample due to the
model lead in the 10–14 August week is available now, so work package 4.0 is
unblocked ahead of schedule.

The 24–28 August mapping is already drafted in `config/feature_dictionary.csv`
with all four categories populated. It cannot be closed until Arjita has Zeek
producing logs, since the mapping must be verified against real conn.log
output rather than documentation.

---

## 2. Deliverables

| Deliverable | Location |
|---|---|
| Data-quality report | `reports/data_quality_report.md` |
| Duplicate and leakage audit | `reports/duplicate_audit.md` |
| Portable feature set and Zeek mapping | `config/feature_dictionary.csv` |
| Saved preprocessing pipeline | `models/preprocessor.joblib` |
| Output column order | `config/feature_order.json` |
| Prepared datasets | `data/processed/*.npz` |
| Processed sample for the model lead | `data/lab_samples/fixture.csv` |

Two additional analyses were produced because the evidence demanded them:
`reports/sanity_check.md` and `reports/shift_analysis.md`. Neither was
scheduled; section 6 explains why they were necessary.

---

## 3. What the data looked like

**Shape.** Official partition confirmed: 175,341 training rows, 82,332 testing
rows, 45 columns.

**Duplication.** 74,072 training rows (42%) are identical except for `id` and
`attack_cat`; 28,380 in testing (34%). Duplication is concentrated in attack
records. Restricted to normal rows and the portable feature set, only 8.3% are
duplicates.

**Cross-partition leakage.** 1,193 normal testing rows are byte-identical to
normal training rows across all features; 1,337 once restricted to the 21
portable features. Reducing the feature set increases collision, so
portability and leakage interact.

**No infinities.** `rate`, `sload` and `dload` are finite throughout despite
2,657 zero-duration rows (1.52%). The dataset authors already handled this. A
guard is retained in the pipeline because the Zeek path will compute these
fields itself.

**Unseen categories.** `state` contains `ACC` and `CLO` in the testing
partition but not in training. Observed fact, not precaution, and the reason
the encoder uses `handle_unknown='ignore'`.

**Class balance differs by partition.** 31.9% normal in training, 44.9% in
testing. Report PR-AUC alongside ROC-AUC.

---

## 4. Feature selection and its cost

21 of 42 features retained. Full mapping in `config/feature_dictionary.csv`,
in four categories as the 24–28 August task requires:

- **Direct** — read from conn.log (`dur`, `spkts`, `dpkts`, `sbytes`,
  `dbytes`, `proto`, `service`)
- **Derived** — arithmetic on conn.log fields (`rate`, `sload`, `dload`,
  `smean`, `dmean`, `is_sm_ips_ports`)
- **Recomputed** — sliding-window counts that must be implemented (the seven
  `ct_*` features)
- **Not available** — 21 features, each with a stated reason

`state` maps to `conn_state` but the two use different vocabularies, so the
lookup is lossy. This is the "defined differently" case in the scheduled task
and needs agreeing with Arjita.

**What was given up.** The two most separable features in the dataset are
`sttl` (effect size 1.94) and `ct_state_ttl` (1.40). Both depend on TTL, and
conn.log carries no TTL field. Excluding them costs roughly half the available
discriminative power.

This is a deliberate trade. `sttl` separates so well because IXIA PerfectStorm
left distinctive TTL values in the generated attack traffic. A model leaning
on it scores well on the benchmark and learns nothing that transfers, which is
the cross-dataset failure Cantone et al. (2024) document. Our reported metrics
will sit below published UNSW-NB15 results, and the reason should be stated
rather than explained away.

---

## 5. Deduplication and splitting

Order matters and is not interchangeable:

```
normal rows -> drop duplicates -> split 80/20 -> train / validation
```

Splitting first would place copies of the same flow on both sides. The model
would then be validated on flows it had memorised, the calibrated threshold
would sit too low, and real traffic would exceed the stated false-positive
budget.

Result: 56,000 normal training rows became 51,331 (8.3% removed), split into
41,065 training and 10,266 validation.

The test set is **not** deduplicated. Both variants are saved and all results
must be reported against both, clearly labelled.

---

## 6. Two unscheduled findings

Neither of these was on the work distribution sheet. Both were produced
because the scheduled work surfaced questions that could not be left open
without risking later rework.

### 6.1 The portable feature set works

Untuned Isolation Forest, 200 estimators, fitted on normal training rows only.
This establishes a floor for work package 4.0, not a target.

| Metric | Value |
|---|---|
| ROC-AUC | 0.795 |
| PR-AUC | 0.845 |
| Effect size | 1.24 |

The feature set separates the classes despite excluding every TTL and
packet-level feature. Work package 4.0 can proceed.

Recall at the 1% budget is 0.282, so roughly seven attacks in ten are missed by
Isolation Forest alone. This supports rather than undermines the proposal: the
Autoencoder and hybrid score address a real gap.

### 6.2 Thresholds do not transfer between data sources

This is the finding that changes the design.

| Budget | FPR, calibrated on validation | FPR, calibrated on test normals |
|---|---|---|
| 0.5% | 0.70% | 0.50% |
| 1.0% | **2.13%** | 1.01% |
| 3.0% | **9.90%** | 3.01% |

The right-hand column is near-exact. **The percentile threshold method is
sound.** The failure is in which data it is calibrated on.

Adversarial validation gives AUC 0.641 between training and testing normal
traffic: distinguishable, moderately. Six of 41 features shifted significantly
(PSI above 0.25), all volume-related: `dload` (0.394), `dmean` (0.347),
`dbytes` (0.331), `dpkts` (0.329), `spkts` (0.300), `rate` (0.285).

The shift is in the **centre** of these distributions, not the tail: `dload`
mean moves from -0.28 to -0.77 while p99 stays at 0.63 and 0.62. Testing
normal traffic contains more small, light flows, particularly in the response
direction. Isolation Forest learned a centre of normality that the test
normals sit away from, so more of them cross the threshold.

The seven `ct_*` features are stable (PSI 0.08 to 0.09), which supports
retaining them despite the recomputation cost.

**Consequences:**

1. The false-positive budget is conditional, not a guarantee. It holds while
   traffic resembles the calibration data.
2. Calibration data must come from the same source as the traffic being
   scored. In the 21–25 September integration week the threshold must be
   recalibrated on normal GNS3 traffic; the UNSW-NB15 threshold cannot be
   carried across.
3. Recalibration is a recurring operation, not one-time setup. The dashboard
   should expose it.
4. The gap between requested budget and observed rate is a result worth
   reporting, not a defect to hide.

---

## 7. Notes for each workstream

**Rubaiyat (models and hybrid scoring)**

Your 10–14 August task is to receive the first processed sample. It is
available now in `data/processed/`.

- Load the `.npz` files directly. Do not refit the preprocessor; it is fitted
  on the training split only and refitting introduces leakage (R-04).
- Fit on `train_normal.npz` only. Calibrate on `val_normal.npz` only.
- Report every metric against both `test_full` and `test_dedup`.
- Your 7–11 September task is the 0.5%, 1% and 3% budget comparison. Section
  6.2 shows the requested budget and the observed rate diverge by a factor of
  two to three. Report the operating point by observed FPR on a held-out set,
  not by the requested budget alone.
- Isolation Forest floor is ROC-AUC 0.795 untuned.

**Arjita (GNS3 and Zeek)**

We are scheduled to review Zeek fields together in the 24–28 August week, and
to work together again on the conversion script in the 7–11 September week.

- `config/feature_dictionary.csv` lists every field your Zeek configuration
  must produce. It is drafted from documentation and needs verifying against
  real conn.log output.
- **conn.log carries no TTL.** No TTL-based feature is obtainable from the
  default log. Raise now if the team wants one, since it would require a
  custom Zeek script or packet capture.
- Use `orig_ip_bytes` and `resp_ip_bytes`, not `orig_bytes` and `resp_bytes`.
  UNSW byte counts include headers.
- `conn_state` and UNSW `state` use different vocabularies. The lookup needs
  agreeing before the topology is finalised.
- Please plan to capture enough clean normal GNS3 traffic for threshold
  recalibration, per section 6.2.

**Sinha (dashboard, explanations and severity)**

Per the work distribution sheet you own the explanation view from 24–28
August and the severity logic from 7–11 September.

- `data/lab_samples/fixture.csv` has the correct shape and column names.
- Your dashboard shows IF score, AE score, hybrid score, model agreement and
  severity. Please also display the observed false-positive rate alongside the
  configured budget, since section 6.2 shows they diverge.
- Recalibration should be an exposed action, not a hidden setup step.

**Whole team**

The `ct_*` features are recomputed, not read from conn.log. The conversion
script must use an identical window definition to the one the models were
trained on, or the same column will mean different things on the two data
sources. This needs one named owner.

---

## 8. Open items

| Item | Needs | Due |
|---|---|---|
| Verify feature dictionary against real Zeek output | Arjita's Zeek running | 24–28 Aug |
| `conn_state` to `state` lookup table | Agreement with Arjita | 24–28 Aug |
| `ct_*` window implementation | Named owner | 7–11 Sep |
| Scope of "with Labannya" in Arjita's 7–11 Sep week | Written definition | Before 7 Sep |
| Recalibration workflow | Design decision | 14–18 Sep |

The fourth item is worth settling early. Arjita's cell for that week reads
only "with labannya", and mine reads "finalise the Zeek conversion script".
Without an explicit split each of us may assume the other is doing it.

---

## 9. Reproducing this work

```bash
python src/profile_unsw.py --data-dir data/raw --out reports
python src/audit_duplicates.py --data-dir data/raw --out reports
python src/build_pipeline.py --data-dir data/raw
python src/sanity_check.py
python src/shift_analysis.py
```

Fixed seed 42 throughout. Dependencies pinned in `requirements.txt`. The
UNSW-NB15 CSVs must be placed in `data/raw/` first; they are not committed.
