# IRISv2 Contrat Pair Uniqueness Diagnostic

Generated at: 2026-06-17T11:13:21

This diagnostic is read-only. It reads Silver sinistres and `iris_dw.dim_contrat`; it does not write to PostgreSQL.

- ETL run id: `3115080d-c2c0-488b-9447-7554d88eeed1`
- input_count: `381893`

## 1) Pair Uniqueness In dim_contrat

- total distinct pair_key: `585474`
- pair_key with exactly one dim_contrat row: `585449`
- pair_key with multiple dim_contrat rows: `25`
| pair_key | dim_contrat_rows | distinct_num_mise_a_jour | num_mise_a_jour_values |
| --- | --- | --- | --- |
| 201950000034217\|4 | 6 | 6 | 0; 6; 7; 8; 9; 10 |
| 202350000007088\|0 | 5 | 5 | 1; 2; 3; 4; 5 |
| 202450000100655\|0 | 4 | 4 | 1; 2; 3; 4 |
| 202150000001097\|4 | 4 | 4 | 0; 1; 2; 3 |
| 202450000100826\|1 | 3 | 3 | 4; 5; 6 |
| 202350000008679\|1 | 3 | 3 | 1; 2; 3 |
| 201750000102537\|6 | 3 | 3 | 1; 2; 3 |
| 201650000066804\|0 | 3 | 3 | 0; 1; 2 |
| 202550000101709\|0 | 2 | 2 | 0; 1 |
| 202550000101316\|0 | 2 | 2 | 0; 1 |
| 202550000100761\|1 | 2 | 2 | 0; 1 |
| 202450000101227\|0 | 2 | 2 | 0; 1 |
| 202450000100826\|0 | 2 | 2 | 1; 2 |
| 202450000100499\|2 | 2 | 2 | 0; 1 |
| 202350000008673\|0 | 2 | 2 | 0; 1 |
| 202350000008173\|0 | 2 | 2 | 0; 1 |
| 202350000002944\|0 | 2 | 2 | 0; 1 |
| 202350000002844\|0 | 2 | 2 | 0; 1 |
| 202250000033955\|0 | 2 | 2 | 0; 1 |
| 202150000037362\|2 | 2 | 2 | 1; 5 |

## 2) Impact On Exact-Unmatched Sinistres

- exact_unmatched_rows: `313153`
- rows with no pair candidate: `10703`
- rows with exactly one pair candidate: `302390`
- rows with multiple pair candidates: `60`

## 3) Candidate Deterministic Rule

- deterministic fallback using max numeric num_mise_a_jour: `60`
| NUMSNT | GRNTSINI | NUMCNT | NUMAVT | NUMMAJ | candidate_num_mise_a_jour_list | selected_max_num_mise_a_jour | selected_contrat_sk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S24511000002780 | CAS | 201750000102040 | 6 | 2 | 0; 1 | 1 | 189503 |
| S24511000002780 | IDA | 201750000102040 | 6 | 2 | 0; 1 | 1 | 189503 |
| S24511000005053 | CAS | 201750000102040 | 6 | 3 | 0; 1 | 1 | 189503 |
| S24511000005053 | IDA | 201750000102040 | 6 | 3 | 0; 1 | 1 | 189503 |
| S25531000010967 | RCM | 202150000001097 | 4 | 9 | 0; 1; 2; 3 | 3 | 395590 |
| S25511000021863 | RCM | 202150000001097 | 4 | 18 | 0; 1; 2; 3 | 3 | 395590 |
| S24511000011478 | CAS | 202150000037362 | 2 | 0 | 1; 5 | 5 | 432746 |
| S24511000011478 | TR | 202150000037362 | 2 | 0 | 1; 5 | 5 | 432746 |
| S24511000009923 | CAS | 202150000037362 | 2 | 9 | 1; 5 | 5 | 432746 |
| S24511000009923 | IDA | 202150000037362 | 2 | 9 | 1; 5 | 5 | 432746 |
| S24511000009830 | CAS | 202150000037362 | 2 | 11 | 1; 5 | 5 | 432746 |
| S24511000009830 | IDA | 202150000037362 | 2 | 11 | 1; 5 | 5 | 432746 |
| S24511000019227 | CAS | 202150000037362 | 2 | 11 | 1; 5 | 5 | 432746 |
| S24511000019227 | IDA | 202150000037362 | 2 | 11 | 1; 5 | 5 | 432746 |
| S24511000016772 | CAS | 202150000036667 | 2 | 12 | 0; 1 | 1 | 431984 |
| S24511000016772 | DOC | 202150000036667 | 2 | 12 | 0; 1 | 1 | 431984 |
| S24511000016772 | RCM | 202150000036667 | 2 | 12 | 0; 1 | 1 | 431984 |
| S24511000009503 | CAS | 202150000036667 | 2 | 25 | 0; 1 | 1 | 431984 |
| S24511000009503 | TR | 202150000036667 | 2 | 25 | 0; 1 | 1 | 431984 |
| S24511000014516 | CAS | 202150000036667 | 2 | 32 | 0; 1 | 1 | 431984 |

## 4) Compare Match Coverage

- exact only matched rows: `68740`
- exact + pair unique fallback matched rows: `371130`
- exact + pair max-nummaj fallback matched rows: `371190`
- remaining unmatched rows: `10703`
