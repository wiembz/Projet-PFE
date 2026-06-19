# IRISv2 dim_client Quality Validation

Generated at: 2026-06-20T00:21:40

This validation reads `iris_dw.dim_client`, writes audit checks to `iris_admin.data_quality_check`, and does not modify DW tables.

## Decision

- dim_client.status: `VALIDATED_WITH_SOURCE_LIMITS`
- `client_natural_key` is the reliable DW key.
- `identifiant_client` must not be used as a unique client key.
- Duplicated `identifiant_client` values are treated as source/migration artifacts.

## Summary

- total_checks: `14`
- pass_count: `7`
- warning_count: `7`
- fail_count: `0`
- validation_status: `WARNING`

## Structural Checks

| check_name | expected_value | observed_value | status |
| --- | --- | --- | --- |
| dim_client_row_count_positive | >0 | 461882 | PASS |
| dim_client_unknown_row_count | 1 | 1 | PASS |
| dim_client_natural_key_null_count | 0 | 0 | PASS |
| dim_client_natural_key_duplicate_count | 0 | 0 | PASS |

## Identifier Reliability

| check_name | expected_value | observed_value | status |
| --- | --- | --- | --- |
| dim_client_identifiant_client_null_count | 0 | 0 | PASS |
| dim_client_identifiant_client_duplicate_value_count | 0 | 20087 | WARNING |
| dim_client_identifiant_client_max_duplicate_group_size | <=1 | 390 | WARNING |

## Attribute Completeness

| check_name | expected_value | observed_value | status |
| --- | --- | --- | --- |
| dim_client_num_client_null_count | 0 | 0 | PASS |
| dim_client_code_nature_client_null_count | 0 | 0 | PASS |
| dim_client_sexe_null_count | 0 | 61550 | WARNING |
| dim_client_situation_familiale_null_count | 0 | 61551 | WARNING |
| dim_client_date_naissance_null_count | 0 | 4002 | WARNING |
| dim_client_gouvernorat_client_null_count | 0 | 52446 | WARNING |
| dim_client_gouvernorat_client_distinct_count | <=100 | 28703 | WARNING |
