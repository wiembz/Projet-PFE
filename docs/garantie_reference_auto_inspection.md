# IRISv2 Automobile Garantie Reference Inspection

Generated at: 2026-06-17T16:03:26

This inspection is read-only. It reads local reference Excel files only; it does not write to PostgreSQL, update `iris_dw`, modify loaders, scoring, marts, or create tables.


## 1. Console Summary

- reference_file: `data\reference\correspondance garantie.xlsx`
- sheet_count: `1`
- target_code_count: `25`
- matched_unique_count: `1`
- duplicate_same_label_count: `12`
- missing_count: `4`
- duplicate_conflicting_count: `8`
- validation_status: `FAIL`

## 2. Sheet Inventory

| sheet_name | row_count | column_count | columns | candidate_code_columns | candidate_label_columns |
| --- | --- | --- | --- | --- | --- |
| Feuil1 | 1839 | 6 | CODPROD, CODFORMU, GRNTSINI, CODGRNT, LIBGRNSIN, COLUMN_6 | CODPROD, CODFORMU, GRNTSINI, CODGRNT | LIBGRNSIN |

## 3. Candidate Pair Evaluation

- recommended_sheet: `Feuil1`
- recommended_code_column: `GRNTSINI`
- recommended_label_column: `LIBGRNSIN`
| sheet_name | code_column | label_column | matched_unique_count | duplicate_same_label_count | missing_count | duplicate_conflicting_count | safe_label_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Feuil1 | GRNTSINI | LIBGRNSIN | 1 | 12 | 4 | 8 | 13 |
| Feuil1 | CODGRNT | LIBGRNSIN | 1 | 9 | 12 | 3 | 10 |
| Feuil1 | CODPROD | LIBGRNSIN | 0 | 0 | 25 | 0 | 0 |
| Feuil1 | CODFORMU | LIBGRNSIN | 0 | 0 | 25 | 0 | 0 |

## 4. Target Automobile Guarantee Code Results

| target_code | status | label | distinct_label_count | match_row_count | sheet_name | code_column | label_column |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CAS | duplicate_conflicting_label | CAS; Contre assurance spéciale | 2 | 104 | Feuil1 | GRNTSINI | LIBGRNSIN |
| RCM | duplicate_conflicting_label | RESP. CIVILE MATERIELLE; RESP. CIVILE MATERIELLE OITS; Responsabilité Civile | 3 | 105 | Feuil1 | GRNTSINI | LIBGRNSIN |
| IDA | duplicate_conflicting_label | Contre assurance spéciale; IDA; Indem. directe des assurés | 3 | 106 | Feuil1 | GRNTSINI | LIBGRNSIN |
| BG | duplicate_same_label | BRIS DE GLACE | 1 | 99 | Feuil1 | GRNTSINI | LIBGRNSIN |
| REM | missing |  | 0 | 0 | Feuil1 | GRNTSINI | LIBGRNSIN |
| ASR | duplicate_conflicting_label | ASR; Avance sur recours; CAS; CONTRE ASSURANCE SPECIAL; Responsabilité Civile | 5 | 104 | Feuil1 | GRNTSINI | LIBGRNSIN |
| RCC | duplicate_conflicting_label | RESP. CIVILE CORPOREL; RESP. CIVILE CORPORELLE; RESP. CIVILE CORPORELLEAGES; Responsabilité Civile | 4 | 102 | Feuil1 | GRNTSINI | LIBGRNSIN |
| TR | duplicate_conflicting_label | TR; Tous risques | 2 | 99 | Feuil1 | GRNTSINI | LIBGRNSIN |
| RCDE | duplicate_same_label | RESPONSABILITE CIVILE_DROITS | 1 | 103 | Feuil1 | GRNTSINI | LIBGRNSIN |
| DOC | duplicate_same_label | Dommage Collision | 1 | 99 | Feuil1 | GRNTSINI | LIBGRNSIN |
| INC | duplicate_conflicting_label | INC; INCENDIE | 2 | 98 | Feuil1 | GRNTSINI | LIBGRNSIN |
| DEPC | missing |  | 0 | 0 | Feuil1 | GRNTSINI | LIBGRNSIN |
| VOL | duplicate_same_label | VOL | 1 | 100 | Feuil1 | GRNTSINI | LIBGRNSIN |
| EXT | missing |  | 0 | 0 | Feuil1 | GRNTSINI | LIBGRNSIN |
| DEPA | missing |  | 0 | 0 | Feuil1 | GRNTSINI | LIBGRNSIN |
| RCR | duplicate_conflicting_label | RESP. CIVILE_RENTE MATHEMAT.; RESPONSABILITE CIVILE_RENTE | 2 | 103 | Feuil1 | GRNTSINI | LIBGRNSIN |
| RCA | duplicate_same_label | RESPONSAB. CIVILE_ARRERAGES | 1 | 102 | Feuil1 | GRNTSINI | LIBGRNSIN |
| CONS | duplicate_same_label | CONSIGNATION | 1 | 94 | Feuil1 | GRNTSINI | LIBGRNSIN |
| IC | duplicate_same_label | Individual conducteur | 1 | 94 | Feuil1 | GRNTSINI | LIBGRNSIN |
| DC | duplicate_same_label | DECES | 1 | 99 | Feuil1 | GRNTSINI | LIBGRNSIN |
| FM | duplicate_same_label | FRAIS MEDICAUX | 1 | 98 | Feuil1 | GRNTSINI | LIBGRNSIN |
| CAT | duplicate_same_label | CATAS.NATURELLE | 1 | 3 | Feuil1 | GRNTSINI | LIBGRNSIN |
| EME | duplicate_same_label | EMEUTE | 1 | 3 | Feuil1 | GRNTSINI | LIBGRNSIN |
| IPT | duplicate_same_label | INVALIDITE PERMANANTE OU TEMPO | 1 | 99 | Feuil1 | GRNTSINI | LIBGRNSIN |
| IND | matched_unique | INDIVIDUEL ACCIDENT | 1 | 1 | Feuil1 | GRNTSINI | LIBGRNSIN |

## 5. Interpretation

- Do not enrich dim_garantie from the recommended pair yet; at least one target code maps to conflicting labels.
- Duplicate_same_label rows indicate repeated product/formula rows with the same label; this is consistent, but enrichment should use a distinct code-to-label mapping.
- This inspection does not enrich dim_garantie; a dedicated enrichment loader or reference update should implement any correction later.

## 6. Warnings And Failures

- validation_status: `FAIL`
| type | message |
| --- | --- |
| FAILURE | Recommended candidate pair contains conflicting labels for target codes. |
| WARNING | Recommended candidate pair is missing labels for target codes. |
| WARNING | Some target codes appear more than once with the same label; this is consistent but not row-unique. |
