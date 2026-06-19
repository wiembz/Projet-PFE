# IRISv2 DW Integrity Validation

Generated at: 2026-06-19T15:58:36

This validation reads `iris_dw`, writes audit checks to `iris_admin.data_quality_check`, and does not modify DW tables.

## Summary

- total_checks: `60`
- pass_count: `21`
- warning_count: `36`
- fail_count: `3`
- validation_status: `FAIL`

## Foreign Key Integrity

| check_name | schema_name | table_name | expected_value | observed_value | status |
| --- | --- | --- | --- | --- | --- |
| dw_fact_prime_client_sk_orphan_count | iris_dw | fact_prime | 0 | 0 | PASS |
| dw_fact_prime_contrat_sk_orphan_count | iris_dw | fact_prime | 0 | 0 | PASS |
| dw_fact_prime_vehicule_sk_orphan_count | iris_dw | fact_prime | 0 | 0 | PASS |
| dw_fact_prime_produit_sk_orphan_count | iris_dw | fact_prime | 0 | 0 | PASS |
| dw_fact_prime_intermediaire_sk_orphan_count | iris_dw | fact_prime | 0 | 0 | PASS |
| dw_fact_prime_delegation_sk_orphan_count | iris_dw | fact_prime | 0 | 0 | PASS |
| dw_fact_sinistre_client_sk_orphan_count | iris_dw | fact_sinistre | 0 | 0 | PASS |
| dw_fact_sinistre_contrat_sk_orphan_count | iris_dw | fact_sinistre | 0 | 0 | PASS |
| dw_fact_sinistre_vehicule_sk_orphan_count | iris_dw | fact_sinistre | 0 | 0 | PASS |
| dw_fact_sinistre_produit_sk_orphan_count | iris_dw | fact_sinistre | 0 | 0 | PASS |
| dw_fact_sinistre_garantie_sk_orphan_count | iris_dw | fact_sinistre | 0 | 0 | PASS |
| dw_fact_sinistre_intermediaire_sk_orphan_count | iris_dw | fact_sinistre | 0 | 0 | PASS |
| dw_fact_sinistre_delegation_sk_orphan_count | iris_dw | fact_sinistre | 0 | 0 | PASS |
| dw_fact_sinistre_cause_sinistre_sk_orphan_count | iris_dw | fact_sinistre | 0 | 0 | PASS |
| dw_fact_inspection_vehicule_sk_orphan_count | iris_dw | fact_inspection | 0 | 0 | PASS |
| dw_fact_inspection_checkpoint_inspection_sk_orphan_count | iris_dw | fact_inspection_checkpoint | 0 | 0 | PASS |
| dw_fact_inspection_checkpoint_checkpoint_sk_orphan_count | iris_dw | fact_inspection_checkpoint | 0 | 0 | PASS |

## Dimension Completeness

| check_name | schema_name | table_name | expected_value | observed_value | status |
| --- | --- | --- | --- | --- | --- |
| dw_dim_vehicule_marque_null_count | iris_dw | dim_vehicule | 0 | 128129 | WARNING |
| dw_dim_vehicule_modele_null_count | iris_dw | dim_vehicule | 0 | 128129 | WARNING |
| dw_dim_vehicule_genre_vehicule_null_count | iris_dw | dim_vehicule | 0 | 128129 | WARNING |
| dw_dim_vehicule_usage_vehicule_null_count | iris_dw | dim_vehicule | 0 | 128129 | WARNING |
| dw_dim_vehicule_energie_null_count | iris_dw | dim_vehicule | 0 | 128129 | WARNING |
| dw_dim_vehicule_puissance_null_count | iris_dw | dim_vehicule | 0 | 128129 | WARNING |
| dw_dim_vehicule_date_mise_circulation_null_count | iris_dw | dim_vehicule | 0 | 128129 | WARNING |
| dw_dim_garantie_libelle_garantie_null_count | iris_dw | dim_garantie | 0 | 79 | WARNING |
| dw_dim_garantie_famille_garantie_null_count | iris_dw | dim_garantie | 0 | 83 | WARNING |
| dw_dim_delegation_libelle_delegation_null_count | iris_dw | dim_delegation | 0 | 5 | WARNING |
| dw_dim_intermediaire_nom_intermediaire_null_count | iris_dw | dim_intermediaire | 0 | 212 | WARNING |
| dw_dim_intermediaire_type_intermediaire_null_count | iris_dw | dim_intermediaire | 0 | 0 | PASS |
| dw_dim_cause_sinistre_libelle_cause_sinistre_null_count | iris_dw | dim_cause_sinistre | 0 | 0 | PASS |
| dw_dim_cause_sinistre_libelle_nature_sinistre_null_count | iris_dw | dim_cause_sinistre | 0 | 74 | FAIL |
| dw_dim_cause_sinistre_libelle_sous_nature_sinistre_null_count | iris_dw | dim_cause_sinistre | 0 | 60 | WARNING |
| dw_dim_vehicule_immatriculation_null_count | iris_dw | dim_vehicule | 0 | 0 | PASS |
| dw_dim_vehicule_vin_null_count | iris_dw | dim_vehicule | 0 | 127905 | WARNING |
| dw_dim_vehicule_motorisation_null_count | iris_dw | dim_vehicule | 0 | 127905 | WARNING |
| dw_dim_vehicule_source_system_null_count | iris_dw | dim_vehicule | 0 | 0 | PASS |

## Fact Anomalies

| check_name | schema_name | table_name | expected_value | observed_value | status |
| --- | --- | --- | --- | --- | --- |
| dw_fact_prime_total_prime_null_count | iris_dw | fact_prime | 0 | 13940 | WARNING |
| dw_fact_prime_total_prime_negative_count | iris_dw | fact_prime | 0 | 40 | WARNING |
| dw_fact_prime_date_fin_contrat_before_debut_count | iris_dw | fact_prime | 0 | 52 | FAIL |
| dw_fact_prime_date_fin_effet_before_debut_count | iris_dw | fact_prime | 0 | 50000 | FAIL |
| dw_fact_sinistre_montant_total_negative_count | iris_dw | fact_sinistre | 0 | 32 | WARNING |
| dw_fact_sinistre_montant_total_net_negative_count | iris_dw | fact_sinistre | 0 | 408 | WARNING |
| dw_fact_sinistre_delai_declaration_negative_count | iris_dw | fact_sinistre | 0 | 73 | WARNING |
| dw_fact_sinistre_delai_ouverture_negative_count | iris_dw | fact_sinistre | 0 | 3 | WARNING |
| dw_fact_sinistre_anciennete_contrat_negative_count | iris_dw | fact_sinistre | 0 | 46 | WARNING |
| dw_fact_sinistre_date_declaration_before_survenance_count | iris_dw | fact_sinistre | 0 | 73 | WARNING |
| dw_fact_sinistre_date_ouverture_before_declaration_count | iris_dw | fact_sinistre | 0 | 3 | WARNING |
| dw_fact_sinistre_sinistre_before_effet_count | iris_dw | fact_sinistre | 0 | 46 | WARNING |

## Kimball Structure

| check_name | schema_name | table_name | expected_value | observed_value | status |
| --- | --- | --- | --- | --- | --- |
| dw_fact_inspection_agent_name_column_presence | iris_dw | fact_inspection | absent | present | WARNING |
| dw_fact_inspection_nom_prenom_client_column_presence | iris_dw | fact_inspection | absent | present | WARNING |
| dw_fact_inspection_telephone_column_presence | iris_dw | fact_inspection | absent | present | WARNING |
| dw_fact_inspection_immatriculation_source_column_presence | iris_dw | fact_inspection | absent | present | WARNING |
| dw_fact_inspection_vin_source_column_presence | iris_dw | fact_inspection | absent | present | WARNING |
| dw_fact_inspection_motorisation_column_presence | iris_dw | fact_inspection | absent | present | WARNING |
| dw_fact_sinistre_code_etat_sinistre_column_presence | iris_dw | fact_sinistre | absent | present | WARNING |
| dw_fact_sinistre_etat_garantie_column_presence | iris_dw | fact_sinistre | absent | present | WARNING |
| dw_fact_sinistre_motif_cloture_column_presence | iris_dw | fact_sinistre | absent | present | WARNING |
| dw_fact_inspection_checkpoint_statut_code_column_presence | iris_dw | fact_inspection_checkpoint | absent | present | WARNING |
| dw_fact_inspection_checkpoint_statut_libelle_column_presence | iris_dw | fact_inspection_checkpoint | absent | present | WARNING |
| dw_fact_inspection_checkpoint_source_column_name_column_presence | iris_dw | fact_inspection_checkpoint | absent | present | WARNING |
