# Duplicate and leakage audit

Follow-up to the data-quality report. Observation only.

## 1. Do identical feature vectors carry conflicting labels?

**Training partition**

- Distinct feature vectors: 101,040
- Vectors appearing more than once: 9,748
- Vectors carrying BOTH labels: 229
- Rows affected by label conflict: 940 (0.54%)

  These rows are unlearnable: the same flow is labelled normal in one record and attack in another. They place a ceiling on achievable precision.

**Testing partition**

- Distinct feature vectors: 53,946
- Vectors appearing more than once: 6,318
- Vectors carrying BOTH labels: 6
- Rows affected by label conflict: 14 (0.02%)

  These rows are unlearnable: the same flow is labelled normal in one record and attack in another. They place a ceiling on achievable precision.

## 2. Does the testing partition overlap the training partition?

- Testing rows whose feature vector also appears in training: **8,541 of 82,332 (10.37%)**

| Test label | Overlapping rows | Share of that class in test |
|---|---|---|
| Normal (0) | 1,472 | 3.98% |
| Attack (1) | 7,069 | 15.59% |

## 3. Leakage into the normal-only training path

Our models are fitted on normal training rows only, so the case that inflates results is a normal test row that is identical to a normal training row.

- Normal test rows identical to a normal training row: **1,193 of 37,000 (3.22%)**

- Attack test rows identical to a training attack row: 7,052 of 45,332 (15.56%)

Attack overlap does not leak into our training path, because attack rows are never used for fitting. It is recorded here for completeness and because it affects how optimistic the benchmark comparison is in general.

## 4. Where the duplication is concentrated

| Attack category | Rows | Duplicated rows | Share duplicated |
|---|---|---|---|
| Normal | 56,000 | 6,047 | 10.8% |
| Generic | 40,000 | 39,169 | 97.9% |
| Exploits | 33,393 | 16,596 | 49.7% |
| Fuzzers | 18,184 | 4,649 | 25.6% |
| DoS | 12,264 | 9,822 | 80.1% |
| Reconnaissance | 10,491 | 4,617 | 44.0% |
| Analysis | 2,000 | 1,708 | 85.4% |
| Backdoor | 1,746 | 1,346 | 77.1% |
| Shellcode | 1,133 | 82 | 7.2% |
| Worms | 130 | 13 | 10.0% |

- Largest single repeat count: 415 identical rows

## 5. What this evidence supports

1. **Cross-partition leakage is present.** 3.2% of normal test rows are byte-identical to normal training rows. Performance measured on the untouched official test set will be optimistic. We will additionally report results on a deduplicated test set and present both figures, rather than reporting only the favourable one.
2. Deduplicate the normal training set before fitting. Repeated identical flows distort the learned normal profile by weighting some behaviours far above their true frequency, which directly shifts the score distribution the threshold is calibrated against.
3. Do NOT deduplicate the test set silently. Report both figures and state which is which.
4. Record the deduplication decision in the feature dictionary so the same rule is applied to Zeek records in Week 9.