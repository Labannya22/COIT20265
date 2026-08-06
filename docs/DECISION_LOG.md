# Decision log

Decisions affecting interfaces, datasets, scope or thresholds. Newest first.
Anything that changes what another workstream consumes goes here **before**
it is implemented.

Dates follow the team work distribution sheet.

| # | Date | Decision | Rationale | Raised by | Affects |
|---|---|---|---|---|---|
| 9 | 7 Aug | Explainability and severity logic confirmed as Sinha's, not Labannya's | Work distribution sheet assigns the explanation view (24–28 Aug) and severity logic (7–11 Sep) to Sinha. Resolves the conflict between the Assessment 1 task-leads table and the RACI matrix | Labannya | WP 6.0, 8.0 |
| 8 | 7 Aug | Recalibration becomes a recurring operation exposed in the dashboard, not one-time setup | Thresholds do not transfer between data sources; 1% budget produced 2.13% actual | Labannya | WP 5.0, 8.0 |
| 7 | 7 Aug | Threshold must be recalibrated on normal GNS3 traffic during integration | Adversarial AUC 0.641 between partitions; six features shifted significantly | Labannya | WP 5.0, 7.0 |
| 6 | 7 Aug | Test set reported in two variants, official and deduplicated | 1,337 normal test rows identical to normal training rows | Labannya | WP 4.0, 5.0, 10.0 |
| 5 | 6 Aug | Deduplicate normal rows before the train/validation split, not after | 42% duplication would place copies on both sides, biasing threshold calibration | Labannya | WP 3.0, 4.0 |
| 4 | 6 Aug | Seven `ct_*` features retained despite requiring recomputation | Five of the top ten portable features; PSI 0.08 to 0.09, stable across partitions | Labannya | WP 3.0, 7.0 |
| 3 | 6 Aug | Exclude all TTL and packet-level features from the portable set | conn.log carries neither; benchmark and lab must share one feature set | Labannya | WP 3.0, 4.0, 7.0 |
| 2 | 5 Aug | UNSW-NB15 official partition, not the four raw CSVs | Raw files lack generated flow features | Labannya | WP 3.0 |
| 1 | 5 Aug | `id` and `attack_cat` dropped at load; `label` held separately | R-04, structural rather than remembered | Labannya | WP 3.0, 4.0 |
