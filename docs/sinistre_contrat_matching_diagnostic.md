# IRISv2 Sinistre-To-Contrat Matching Diagnostic

Generated at: 2026-06-17T11:05:51

This diagnostic is read-only. It reads Silver sinistres and `iris_dw.dim_contrat`; it does not write to PostgreSQL.

- ETL run id: `3115080d-c2c0-488b-9447-7554d88eeed1`
- input_count: `381893`

## 1) Exact Key Match

- matched rows: `68740`
- unmatched rows: `313153`
- matched distinct contracts: `32577`
- unmatched distinct contracts: `157970`

## 2) NUMCNT Only Match

- rows where NUMCNT exists in dim_contrat: `381604`
- rows where NUMCNT does not exist: `289`
- distinct NUMCNT missing: `102`
- average number of dim_contrat rows per NUMCNT: `1.31`

## 3) NUMCNT + NUMAVT Match

- matched rows: `371190`
- unmatched rows: `10703`

## 4) Date-Effective Match Candidate

- rows matchable by NUMCNT + DTSURV effective period: `267`
- rows still unmatched: `312886`
- rows with multiple candidate contracts: `58`

## 5) Best Fallback Candidate

- deterministic_fallback_count: `209`
- ambiguous_count: `58`
- no_candidate_count: `312886`

## 6) Samples

| NUMSNT | GRNTSINI | NUMCNT | NUMAVT | NUMMAJ | DTSURV | contrat_business_key | numcnt_exists_in_dim_contrat | candidate_contracts_by_numcnt | date_effective_candidate_contracts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S16511000004056 | IDA | 20165.0400315/9 | 0 | 0 | 2016-03-14 | 20165.0400315/9\|0\|0 | True | 2 | 0 |
| S16511000012866 | CAS | 20165.0400315/9 | 0 | 0 | 2016-05-17 | 20165.0400315/9\|0\|0 | True | 2 | 0 |
| S16511000030807 | CAS | 20165.0400315/9 | 0 | 0 | 2016-11-29 | 20165.0400315/9\|0\|0 | True | 2 | 0 |
| S16511000030807 | TR | 20165.0400315/9 | 0 | 0 | 2016-11-29 | 20165.0400315/9\|0\|0 | True | 2 | 0 |
| S16511000036412 | RCM | 20165.0400315/9 | 0 | 0 | 2016-05-17 | 20165.0400315/9\|0\|0 | True | 2 | 0 |
| S17511000003111 | ASR | 20165.0400315/9 | 1 | 0 | 2017-02-08 | 20165.0400315/9\|1\|0 | True | 2 | 0 |
| S17511000003111 | CAS | 20165.0400315/9 | 1 | 0 | 2017-02-08 | 20165.0400315/9\|1\|0 | True | 2 | 0 |
| S17511000003111 | RCM | 20165.0400315/9 | 1 | 0 | 2017-02-08 | 20165.0400315/9\|1\|0 | True | 2 | 0 |
| S17511000022208 | CAS | 20165.0400315/9 | 1 | 0 | 2017-08-02 | 20165.0400315/9\|1\|0 | True | 2 | 0 |
| S17511000022208 | TR | 20165.0400315/9 | 1 | 0 | 2017-08-02 | 20165.0400315/9\|1\|0 | True | 2 | 0 |
| S17511000028563 | CAS | 20165.0400315/9 | 1 | 0 | 2017-09-14 | 20165.0400315/9\|1\|0 | True | 2 | 0 |
| S17511000028563 | IDA | 20165.0400315/9 | 1 | 0 | 2017-09-14 | 20165.0400315/9\|1\|0 | True | 2 | 0 |
| S17511000033318 | CAS | 20165.0400315/9 | 1 | 0 | 2017-11-13 | 20165.0400315/9\|1\|0 | True | 2 | 0 |
| S17511000033318 | TR | 20165.0400315/9 | 1 | 0 | 2017-11-13 | 20165.0400315/9\|1\|0 | True | 2 | 0 |
| S17511000035169 | ASR | 20165.0400315/9 | 1 | 0 | 2017-11-28 | 20165.0400315/9\|1\|0 | True | 2 | 0 |
| S17511000035169 | CAS | 20165.0400315/9 | 1 | 0 | 2017-11-28 | 20165.0400315/9\|1\|0 | True | 2 | 0 |
| S17511000038821 | CAS | 20165.0400315/9 | 1 | 0 | 2017-12-24 | 20165.0400315/9\|1\|0 | True | 2 | 0 |
| S17511000038821 | TR | 20165.0400315/9 | 1 | 0 | 2017-12-24 | 20165.0400315/9\|1\|0 | True | 2 | 0 |
| S17511000039492 | TR | 20165.0400315/9 | 1 | 0 | 2017-12-30 | 20165.0400315/9\|1\|0 | True | 2 | 0 |
| S17521000018983 | RCM | 20165.0400315/9 | 1 | 0 | 2017-06-07 | 20165.0400315/9\|1\|0 | True | 2 | 0 |
