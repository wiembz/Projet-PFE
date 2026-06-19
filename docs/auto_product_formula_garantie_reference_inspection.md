# IRISv2 Automobile Product Formula Garantie Reference Inspection

Generated at: 2026-06-17T21:21:25

This inspection is read-only. It reads local reference Excel files and `iris_dw.dim_produit`; it does not update PostgreSQL, modify `iris_dw`, Silver, loaders, scoring, marts, or orchestration, and it does not create or alter tables.

Automobile perimeter: `CODPROD` / `code_produit` starts with `5`.


## 1. Console Summary

- auto_reference_rows: `1839`
- distinct_auto_codprod: `41`
- distinct_auto_codprod_codformu: `110`
- formula_label_source_status: `available:CAUSESINI, LIBCAUSE, NATSINI, RESPONSA, INFOTIER, RESPXY, OBGSOUNAT, GRNTSINI, GENREEVAL, UPDATE_IDENT,CAUSESINI, SOUNATSIN, LIBSOUNAT,CLASSPERS, LIBELLE, TYPENUM, EXISTE, FNCTAJT, FNCTMDF, FNCTCST, NATCLASS, NATCPTE, UPDATE_IDENT,CNAT, CLASSPERS, LIBELLE, UPDATE_IDENT,GRNTSINI, LIBGRNSIN,GRNTSINI, LIBGRNSIN, COLUMN_6,LIBDELEGA,LIBFAMIL,LIBFORMU,NATINT, IDINT, LOCAL, UPDATE_IDENT,TABLE, LIBELLE, UPDATE_IDENT`
- safest_garantie_mapping_grain: `CODPROD + CODFORMU + GRNTSINI`
- safest_grain_conflicting_count: `0`
- missing_target_codes: `REM, DEPC, EXT, DEPA`
- validation_status: `WARNING`
- distinct_auto_codprod_codformu_grntsini: `1839`

## 2. File Inventory

| file | sheet | row_count | columns | candidate_code_columns | candidate_label_columns |
| --- | --- | --- | --- | --- | --- |
| data\reference\correspondance garantie.xlsx | Feuil1 | 1839 | CODPROD, CODFORMU, GRNTSINI, CODGRNT, LIBGRNSIN, COLUMN_6 | CODPROD, CODFORMU, GRNTSINI, CODGRNT | LIBGRNSIN |
| data\reference\fichierStagiaire.xlsx | GRNTSINI  | 1838 | CODPROD, CODFORMU, GRNTSINI, CODGRNT, LIBGRNSIN | CODPROD, CODFORMU, GRNTSINI, CODGRNT | LIBGRNSIN |
| data\reference\fichierStagiaire.xlsx | CODPROD  | 103 | CODPROD, CODFORMU, LIBFORMU | CODPROD, CODFORMU, LIBFORMU | LIBFORMU |
| data\reference\fichierStagiaire.xlsx | CODFAM | 7 | CODFAM, LIBFAMIL | CODFAM | LIBFAMIL |
| data\reference\fichierStagiaire.xlsx | SOUSNATSIN | 31 | CODFAM, CAUSESINI, SOUNATSIN, LIBSOUNAT | CODFAM | LIBSOUNAT |
| data\reference\fichierStagiaire.xlsx | Délégation  | 5 | CODDELEGA, LIBDELEGA | CODDELEGA | LIBDELEGA |
| data\reference\PE01.xlsx | Sheet1 | 349 | TABLE, CODE, LIBELLE, UPDATE_IDENT | CODE | LIBELLE |
| data\reference\PE02.xlsx | Sheet1 | 24 | CLASSPERS, LIBELLE, TYPENUM, EXISTE, FNCTAJT, FNCTMDF, FNCTCST, NATCLASS, NATCPTE, UPDATE_IDENT |  | LIBELLE |
| data\reference\PE033.xlsx | Sheet1 | 44 | CNAT, CLASSPERS, LIBELLE, UPDATE_IDENT |  | LIBELLE |
| data\reference\PR01.xlsx | Sheet1 | 300 | NATINT, IDINT, LOCAL, UPDATE_IDENT |  |  |
| data\reference\SI001.xlsx | Sheet1 | 46 | CODFAM, CAUSESINI, LIBCAUSE, NATSINI, RESPONSA, INFOTIER, RESPXY, OBGSOUNAT, GRNTSINI, GENREEVAL, UPDATE_IDENT | CODFAM, GRNTSINI | LIBCAUSE |

## 3. Product Formula Coverage

- auto_reference_rows: `1839`
- distinct_CODPROD: `41`
- distinct_CODPROD_CODFORMU: `110`
- distinct_CODPROD_CODFORMU_GRNTSINI: `1839`
- formula_label_source_status: `available:CAUSESINI, LIBCAUSE, NATSINI, RESPONSA, INFOTIER, RESPXY, OBGSOUNAT, GRNTSINI, GENREEVAL, UPDATE_IDENT,CAUSESINI, SOUNATSIN, LIBSOUNAT,CLASSPERS, LIBELLE, TYPENUM, EXISTE, FNCTAJT, FNCTMDF, FNCTCST, NATCLASS, NATCPTE, UPDATE_IDENT,CNAT, CLASSPERS, LIBELLE, UPDATE_IDENT,GRNTSINI, LIBGRNSIN,GRNTSINI, LIBGRNSIN, COLUMN_6,LIBDELEGA,LIBFAMIL,LIBFORMU,NATINT, IDINT, LOCAL, UPDATE_IDENT,TABLE, LIBELLE, UPDATE_IDENT`

## 4. Product Formula Reference Candidates

| file | sheet | row_count | product_code_columns | formula_code_columns | formula_label_columns |
| --- | --- | --- | --- | --- | --- |
| data\reference\correspondance garantie.xlsx | Feuil1 | 1839 | CODPROD, CODFORMU, GRNTSINI, CODGRNT, LIBGRNSIN, COLUMN_6 | CODPROD, CODFORMU, GRNTSINI, CODGRNT, LIBGRNSIN, COLUMN_6 | GRNTSINI, LIBGRNSIN, COLUMN_6 |
| data\reference\fichierStagiaire.xlsx | GRNTSINI  | 1838 | CODPROD, CODFORMU, GRNTSINI, CODGRNT, LIBGRNSIN | CODPROD, CODFORMU, GRNTSINI, CODGRNT, LIBGRNSIN | GRNTSINI, LIBGRNSIN |
| data\reference\fichierStagiaire.xlsx | CODPROD  | 103 | CODPROD, CODFORMU, LIBFORMU | CODPROD, CODFORMU, LIBFORMU | LIBFORMU |
| data\reference\fichierStagiaire.xlsx | CODFAM | 7 | CODFAM, LIBFAMIL | CODFAM, LIBFAMIL | LIBFAMIL |
| data\reference\fichierStagiaire.xlsx | SOUSNATSIN | 31 | CODFAM, CAUSESINI, SOUNATSIN, LIBSOUNAT | CODFAM, CAUSESINI, SOUNATSIN, LIBSOUNAT | CAUSESINI, SOUNATSIN, LIBSOUNAT |
| data\reference\fichierStagiaire.xlsx | Délégation  | 5 | CODDELEGA, LIBDELEGA | CODDELEGA, LIBDELEGA | LIBDELEGA |
| data\reference\PE01.xlsx | Sheet1 | 349 | TABLE, CODE, LIBELLE, UPDATE_IDENT | TABLE, CODE, LIBELLE, UPDATE_IDENT | TABLE, LIBELLE, UPDATE_IDENT |
| data\reference\PE02.xlsx | Sheet1 | 24 | CLASSPERS, LIBELLE, TYPENUM, EXISTE, FNCTAJT, FNCTMDF, FNCTCST, NATCLASS, NATCPTE, UPDATE_IDENT | CLASSPERS, LIBELLE, TYPENUM, EXISTE, FNCTAJT, FNCTMDF, FNCTCST, NATCLASS, NATCPTE, UPDATE_IDENT | CLASSPERS, LIBELLE, TYPENUM, EXISTE, FNCTAJT, FNCTMDF, FNCTCST, NATCLASS, NATCPTE, UPDATE_IDENT |
| data\reference\PE033.xlsx | Sheet1 | 44 | CNAT, CLASSPERS, LIBELLE, UPDATE_IDENT | CNAT, CLASSPERS, LIBELLE, UPDATE_IDENT | CNAT, CLASSPERS, LIBELLE, UPDATE_IDENT |
| data\reference\PR01.xlsx | Sheet1 | 300 | NATINT, IDINT, LOCAL, UPDATE_IDENT | NATINT, IDINT, LOCAL, UPDATE_IDENT | NATINT, IDINT, LOCAL, UPDATE_IDENT |
| data\reference\SI001.xlsx | Sheet1 | 46 | CODFAM, CAUSESINI, LIBCAUSE, NATSINI, RESPONSA, INFOTIER, RESPXY, OBGSOUNAT, GRNTSINI, GENREEVAL, UPDATE_IDENT | CODFAM, CAUSESINI, LIBCAUSE, NATSINI, RESPONSA, INFOTIER, RESPXY, OBGSOUNAT, GRNTSINI, GENREEVAL, UPDATE_IDENT | CAUSESINI, LIBCAUSE, NATSINI, RESPONSA, INFOTIER, RESPXY, OBGSOUNAT, GRNTSINI, GENREEVAL, UPDATE_IDENT |

## 5. iris_dw.dim_produit Comparison

- dim_produit_available: `True`
- auto_product_rows_code_produit_starts_5: `37`
- code_formule_null_rows: `37`
- code_formule_exists_but_no_reference_pair: `0`
- reference_pairs_not_represented_in_dim_produit: `110`
| gap_type | pair |
| --- | --- |
| reference_pair_not_in_dim | 521/1 |
| reference_pair_not_in_dim | 521/10 |
| reference_pair_not_in_dim | 521/11 |
| reference_pair_not_in_dim | 521/12 |
| reference_pair_not_in_dim | 521/13 |
| reference_pair_not_in_dim | 521/14 |
| reference_pair_not_in_dim | 521/15 |
| reference_pair_not_in_dim | 521/2 |
| reference_pair_not_in_dim | 521/3 |
| reference_pair_not_in_dim | 521/4 |
| reference_pair_not_in_dim | 521/5 |
| reference_pair_not_in_dim | 521/55 |
| reference_pair_not_in_dim | 521/6 |
| reference_pair_not_in_dim | 521/7 |
| reference_pair_not_in_dim | 521/8 |
| reference_pair_not_in_dim | 521/9 |
| reference_pair_not_in_dim | 522/1 |
| reference_pair_not_in_dim | 522/21 |
| reference_pair_not_in_dim | 522/23 |
| reference_pair_not_in_dim | 522/24 |
| reference_pair_not_in_dim | 522/26 |
| reference_pair_not_in_dim | 522/27 |
| reference_pair_not_in_dim | 522/31 |
| reference_pair_not_in_dim | 522/32 |
| reference_pair_not_in_dim | 522/33 |

## 6. Guarantee Label Stability By Grain

| grain | target_code_count | matched_count | missing_count | unique_label_count | duplicate_same_label_count | duplicate_conflicting_label_count | safe_mapping_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GRNTSINI | 25 | 21 | 4 | 1 | 12 | 8 | 13 |
| CODPROD + GRNTSINI | 25 | 21 | 4 | 434 | 248 | 21 | 682 |
| CODPROD + CODFORMU + GRNTSINI | 25 | 21 | 4 | 1815 | 0 | 0 | 1815 |
| CODPROD + CODFORMU + CODGRNT + GRNTSINI | 25 | 21 | 4 | 1815 | 0 | 0 | 1815 |

## 7. Missing Target Codes

| target_code | status | grntsini_rows | codgrnt_rows | codprod_codformu_examples |
| --- | --- | --- | --- | --- |
| REM | not_found_in_reference | 0 | 0 |  |
| DEPC | not_found_in_reference | 0 | 0 |  |
| EXT | not_found_in_reference | 0 | 0 |  |
| DEPA | not_found_in_reference | 0 | 0 |  |

## 8. Warnings And Failures

| type | message |
| --- | --- |
| WARNING | At least one requested target code is absent from GRNTSINI and CODGRNT. |
