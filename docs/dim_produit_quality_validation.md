# IRISv2 dim_produit Quality Validation

Generated at: 2026-06-19T10:28:57

This validation is read-only. It checks `iris_dw.dim_produit`, fact product links, and mart queryability without modifying data.

## Summary

- total_rows: `237`
- unknown_rows: `1`
- real_row_null_code_formule_count: `0`
- missing_libelle_produit_count: `5`
- missing_libelle_formule_count: `0`
- missing_libelle_famille_count: `5`
- natural_key_mismatch_count: `0`
- duplicate_product_formula_count: `0`
- automobile_product_formula_rows: `141`
- fact_prime_rows: `585514`
- fact_prime_unknown_produit_count: `0`
- fact_sinistre_rows: `381893`
- fact_sinistre_unknown_produit_count: `0`
- mart_view_count: `6`
- invalid_view_count: `0`
- reference_auto_product_formula_pair_count: `103`
- reference_auto_product_formula_missing_count: `0`
- validation_status: `WARNING`

## Duplicate Product Formula Rows

No rows.

## Missing Automobile Reference Pairs

No rows.

## Warnings And Failures

| type | message |
| --- | --- |
| WARNING | Some dim_produit rows are missing libelle_famille_produit. |
