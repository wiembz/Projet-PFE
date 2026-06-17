# IRISv2 Reference Conformity Report

Generated at: 2026-06-17T10:23:58

This report is read-only. It reads official reference Excel files and existing `iris_dw` dimension tables; it does not write to PostgreSQL or update DW tables.

- Reference directory: `data\reference`


## 1) Garantie Label Stability

- total rows: `1839`
- distinct GRNTSINI: `27`
- GRNTSINI with multiple labels: `13`

### Sample Conflicts

| GRNTSINI | distinct_label_count | LIBGRNSIN |
| --- | --- | --- |
| ASR | 6 | ASR; AVANCE SUR RECOURS; Avance sur recours; CAS; CONTRE ASSURANCE SPECIAL |
| CAS | 3 | CAS; CONTRE ASSURANCE SPÉCIALE; Contre assurance spéciale |
| DCAT | 2 | CATAS.NATURELLE; DCAT |
| DEM | 2 | CATAS.NATURELLE; DOM SUITE EMEUT/MOUV |
| DOC | 2 | DOMMAGE COLLISION; Dommage Collision |
| GCOM | 2 | GESTE COMMERCIAL; Geste Commercial |
| IC | 2 | INDIVIDUAL CONDUCTEUR; Individual conducteur |
| IDA | 5 | Contre assurance spéciale; IDA; INDEM. DIRECTE DES ASSURÉS; INDEM. DIRECTE DES ASSURéS; Indem. directe des assurés |
| INC | 2 | INC; INCENDIE |
| RCC | 5 | RESP. CIVILE CORPOREL; RESP. CIVILE CORPORELLE; RESP. CIVILE CORPORELLEAGES; RESP. CIVILE corporelle; Responsabilité Civile |
- dim_garantie rows excluding UNKNOWN: `83`
- rows with at least one reference label: `22`
- rows without reference label: `61`

## 2) Cause Sinistre Enrichment Feasibility

- automobile CODFAM scope: `5`

### SI001 CODFAM + CAUSESINI

- total rows: `46`
- complete key rows: `46`
- incomplete key rows: `0`
- duplicate row count: `0`
- duplicate group count: `0`

### SOUSNATSIN CODFAM + CAUSESINI + SOUNATSIN

- total rows: `31`
- complete key rows: `31`
- incomplete key rows: `0`
- duplicate row count: `0`
- duplicate group count: `0`
- dim_cause_sinistre rows excluding UNKNOWN: `74`
- rows enrichable for libelle_cause_sinistre: `74`
- rows enrichable for libelle_sous_nature_sinistre: `14`
- rows not matched: `0`

### Sample Not Matched

- No sample rows.

## 3) Produit Label Stability


### CODPROD + CODFORMU

- total rows: `103`
- complete key rows: `103`
- incomplete key rows: `0`
- duplicate row count: `0`
- duplicate group count: `0`
- CODPROD with multiple LIBFORMU: `12`

### Sample Conflicts

| CODPROD | distinct_label_count | LIBFORMU |
| --- | --- | --- |
| 521 | 15 | AAFCME AU TIERS; AAFCME DOMMAGE COLLISION; AAFCME TIERCE; AFFAIRES ET PROMENADE BASIQUE; AFFAIRES ET PROMENADES |
| 522 | 37 | 521 Promenade et affaires; 523 Ambulance; 524 Corbillards; 526 Auto-école tourisme; 527 Auto-école utilitaire |
| 532 | 2 | AGRICOLE II (SUP.à 3.5T PLATEAU); AGRICOLE II (SUP.à 3.5T TETE) |
| 541 | 2 | UTILITAIRE I; UTILITAIRE I - PROD. INFLAMMABLES |
| 542 | 3 | UTILITAIRE II (SUP.à 3.5T) - PLATEAU; UTILITAIRE II (SUP.à 3.5T) - TETE; UTILITAIRE II - PROD. INFLAMMABLES |
| 543 | 2 | REMORQUE; REMORQUE AVEC PRODUITS INFLAMMABLES |
| 551 | 3 | TPM C.PLATEAU(SUP 3.5T PDT INFLAMMABLES); TPM CAMION PLATEAU (SUP A 3.5 T); TPM TETE (SUP A 3.5 T) |
| 553 | 2 | TPM REMORQUE (SUP A 3.5T); TPM REMORQUE(SUP A 3.5T PDT INFLAMMABLE) |
| 571 | 2 | TAXI; TAXI BASIQUE |
| 582 | 2 | MOISSONNEUSE-BATTEUSE(LOCATION); MOISSONNEUSE-BATTEUSE(PARTICULIER) |
- dim_produit rows excluding UNKNOWN: `86`
- join mode: `code_produit + code_formule`
- rows matched: `0`
- rows unmatched: `86`

## 4) Delegation

- reference rows: `5`
- empty LIBDELEGA rows: `5`
- non-empty LIBDELEGA rows: `0`
- Délégation LIBDELEGA is empty and should not be used for enrichment.

## 5) Intermediaire


### PR01 NATINT + IDINT

- total rows: `300`
- complete key rows: `300`
- incomplete key rows: `0`
- duplicate row count: `0`
- duplicate group count: `0`
- dim_intermediaire rows excluding UNKNOWN: `212`
- matched count: `152`
- unmatched count: `60`
- local_intermediaire column exists: `no`
- Recommendation: do not update current DDL unless local_intermediaire column exists.
