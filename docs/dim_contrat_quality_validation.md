# IRISv2 dim_contrat Quality Validation

Generated at: 2026-06-20T00:51:22

This validation reads `iris_dw.dim_contrat`, writes audit checks to `iris_admin.data_quality_check`, and does not modify DW tables.

## Decision

- dim_contrat.status: `VALIDATED_WITH_SOURCE_LIMITS`
- `contrat_natural_key` is the reliable DW contract key.
- `delegation_sk = 0` is mostly explained by missing source `IDDELEGA`.
- Date anomalies are treated as source/business semantics warnings.
- No automatic date inversion or correction should be applied in ETL.

## Summary

- total_checks: `19`
- pass_count: `9`
- warning_count: `10`
- fail_count: `0`
- validation_status: `WARNING`

## Structural Checks

| check_name | expected_value | observed_value | status |
| --- | --- | --- | --- |
| dim_contrat_row_count_positive | >0 | 585515 | PASS |
| dim_contrat_unknown_row_count | 1 | 1 | PASS |
| dim_contrat_natural_key_null_count | 0 | 0 | PASS |
| dim_contrat_natural_key_duplicate_count | 0 | 0 | PASS |

## Relationship Checks

| check_name | expected_value | observed_value | status |
| --- | --- | --- | --- |
| dim_contrat_produit_unknown_count | <=1 | 1 | PASS |
| dim_contrat_delegation_unknown_count | <=1 | 8112 | WARNING |
| dim_contrat_intermediaire_unknown_count | <=1 | 5 | WARNING |

## Date Semantics

| check_name | expected_value | observed_value | status |
| --- | --- | --- | --- |
| dim_contrat_date_debut_contrat_null_count | 0 | 5 | WARNING |
| dim_contrat_date_fin_contrat_null_count | 0 | 261201 | WARNING |
| dim_contrat_date_debut_effet_null_count | 0 | 5 | WARNING |
| dim_contrat_date_fin_effet_null_count | 0 | 1649 | WARNING |
| dim_contrat_fin_before_debut_contrat_count | 0 | 52 | WARNING |

## Attribute Completeness

| check_name | expected_value | observed_value | status |
| --- | --- | --- | --- |
| dim_contrat_num_contrat_null_count | 0 | 0 | PASS |
| dim_contrat_num_avenant_null_count | 0 | 0 | PASS |
| dim_contrat_num_mise_a_jour_null_count | 0 | 0 | PASS |
| dim_contrat_fin_effet_before_debut_effet_count | 0 | 50000 | WARNING |
| dim_contrat_situation_contrat_null_count | 0 | 0 | PASS |
| dim_contrat_type_resiliation_null_count | 0 | 294700 | WARNING |
| dim_contrat_libelle_resiliation_null_count | 0 | 366066 | WARNING |
