# IRISv2 Mart Views Validation

Generated at: 2026-06-17T13:11:03

This validation is read-only. It queries existing `iris_mart` views and does not modify PostgreSQL objects or run scoring.

## 1. Summary

- final_status: `WARNING`
- view_count: `6`
- warning_count: `5`
- failure_count: `0`

## 2. View Inventory

| view_name | status | column_count |
| --- | --- | --- |
| vw_client_behavior | OK | 12 |
| vw_dashboard_global | WARNING | 12 |
| vw_dossier_360 | WARNING | 54 |
| vw_score_explanation | WARNING | 14 |
| vw_vehicle_history | WARNING | 15 |
| vw_worklist_investigation | WARNING | 42 |

## 3. Row Counts

| view_name | status | row_count | reason |
| --- | --- | --- | --- |
| vw_client_behavior | OK | 461882 | View compiled and returned coherent row counts |
| vw_dashboard_global | WARNING | 1 | score_global_moyen is null; iris_score may not have run yet |
| vw_dossier_360 | WARNING | 381893 | score_global is null for all sampled population; iris_score may not have run yet |
| vw_score_explanation | WARNING | 0 | Score-dependent view is empty; iris_score may not have run yet |
| vw_vehicle_history | WARNING | 128130 | dernier_vhs_score is null for all vehicle rows; VHS scoring may not have run yet |
| vw_worklist_investigation | WARNING | 381893 | score_global is null for all worklist rows; iris_score may not have run yet |

## 4. Score/VHS Readiness Warnings

- vw_dashboard_global: score_global_moyen is null; iris_score may not have run yet
- vw_dossier_360: score_global is null for all sampled population; iris_score may not have run yet
- vw_score_explanation: Score-dependent view is empty; iris_score may not have run yet
- vw_vehicle_history: dernier_vhs_score is null for all vehicle rows; VHS scoring may not have run yet
- vw_worklist_investigation: score_global is null for all worklist rows; iris_score may not have run yet

## 5. Failures

- No failures.

## 6. Sample Columns Per View

| view_name | sample_columns |
| --- | --- |
| vw_client_behavior | client_sk, num_client, code_nature_client, sexe, gouvernorat_client, localite_client, nb_sinistres, nb_vehicules, montant_total_sinistres, nb_dossiers_moyen, nb_dossiers_eleve, dernier_sinistre |
| vw_dashboard_global | nombre_sinistres, montant_total_sinistres, montant_total_net, nombre_declarations_antidatees, nombre_declarations_tardives, nombre_sinistres_avant_contrat, nombre_sinistres_precoces, dossiers_normal, dossiers_faible, dossiers_moyen, dossiers_eleve, score_global_moyen |
| vw_dossier_360 | sinistre_sk, num_sinistre, sinistre_natural_key, client_sk, num_client, code_nature_client, sexe, date_naissance, gouvernorat_client, localite_client, contrat_sk, num_contrat, num_avenant, num_mise_a_jour, situation_contrat, vehicule_sk, immatriculation, vin, marque, modele, genre_vehicule, usage_vehicule, code_produit, libelle_produit, code_garantie, libelle_garantie, code_cause_sinistre, code_nature_sinistre, code_sous_nature_sinistre, date_survenance, date_declaration, date_ouverture, date_cloture, montant_evaluation_initiale, montant_declare, montant_total, montant_total_net, code_etat_sinistre, etat_garantie, motif_cloture, delai_declaration_jours, delai_ouverture_jours, anciennete_contrat_jours, is_declaration_antidatee, is_declaration_tardive, is_sinistre_avant_contrat, is_sinistre_precoce, score_rule_norm, score_ml, score_cross, score_global, risk_level, confidence_level, triggered_rules |
| vw_score_explanation | num_sinistre, sinistre_sk, code_garantie, libelle_garantie, score_global, risk_level, confidence_level, rule_code, rule_name, rule_category, observed_value, threshold_value, rule_weight, rule_contribution |
| vw_vehicle_history | vehicule_sk, immatriculation, vin, marque, modele, genre_vehicule, usage_vehicule, motorisation, nb_sinistres, nb_inspections, montant_total_sinistres, dernier_vhs_score, dernier_safety_grade, derniere_vhs_decision, dernier_is_drivable |
| vw_worklist_investigation | rank_priority, sinistre_sk, num_sinistre, code_garantie, libelle_garantie, client_sk, num_client, code_nature_client, gouvernorat_client, num_contrat, num_avenant, num_mise_a_jour, vehicule_sk, immatriculation, vin, marque, modele, code_produit, libelle_produit, date_survenance, date_declaration, montant_total, montant_total_net, delai_declaration_jours, anciennete_contrat_jours, is_declaration_antidatee, is_declaration_tardive, is_sinistre_avant_contrat, is_sinistre_precoce, score_rule_norm, score_ml, score_cross, score_global, risk_level, confidence_level, rules_triggered_count, triggered_rules, vhs_score_displayed, safety_grade, vhs_decision, is_drivable, main_reason |

## 7. Optional Sample Rows


### vw_client_behavior

| client_sk | num_client | code_nature_client | sexe | gouvernorat_client | localite_client | nb_sinistres | nb_vehicules | montant_total_sinistres | nb_dossiers_moyen | nb_dossiers_eleve | dernier_sinistre |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | UNKNOWN | UNKNOWN |  |  |  | 28 | 12 | 58916.113 | 0 | 0 | 2026-03-06 |
| 1 | 55 | CL |  |  | SFAX TUNISIE | 0 | 0 |  | 0 | 0 |  |
| 2 | 132 | CL |  |  | MARETH | 0 | 0 |  | 0 | 0 |  |
| 3 | 167 | CL |  |  | EL JEM | 0 | 0 |  | 0 | 0 |  |
| 4 | 170 | CL |  |  | SFAX | 0 | 0 |  | 0 | 0 |  |

### vw_dashboard_global

Extra checks:
- row_count: `1`
- full_row: `nombre_sinistres=381893; montant_total_sinistres=725309705.589; montant_total_net=616397879.937; nombre_declarations_antidatees=73; nombre_declarations_tardives=128689; nombre_sinistres_avant_contrat=46; nombre_sinistres_precoces=53991; dossiers_normal=0; dossiers_faible=0; dossiers_moyen=0; dossiers_eleve=0; score_global_moyen=`

| nombre_sinistres | montant_total_sinistres | montant_total_net | nombre_declarations_antidatees | nombre_declarations_tardives | nombre_sinistres_avant_contrat | nombre_sinistres_precoces | dossiers_normal | dossiers_faible | dossiers_moyen | dossiers_eleve | score_global_moyen |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 381893 | 725309705.589 | 616397879.937 | 73 | 128689 | 46 | 53991 | 0 | 0 | 0 | 0 |  |

### vw_dossier_360

Extra checks:
- row_count: `381893`
- sinistre_sk_null_count: `0`
- score_global_not_null_count: `0`

| sinistre_sk | num_sinistre | sinistre_natural_key | client_sk | num_client | code_nature_client | sexe | date_naissance | gouvernorat_client | localite_client | contrat_sk | num_contrat | num_avenant | num_mise_a_jour | situation_contrat | vehicule_sk | immatriculation | vin | marque | modele | genre_vehicule | usage_vehicule | code_produit | libelle_produit | code_garantie | libelle_garantie | code_cause_sinistre | code_nature_sinistre | code_sous_nature_sinistre | date_survenance | date_declaration | date_ouverture | date_cloture | montant_evaluation_initiale | montant_declare | montant_total | montant_total_net | code_etat_sinistre | etat_garantie | motif_cloture | delai_declaration_jours | delai_ouverture_jours | anciennete_contrat_jours | is_declaration_antidatee | is_declaration_tardive | is_sinistre_avant_contrat | is_sinistre_precoce | score_rule_norm | score_ml | score_cross | score_global | risk_level | confidence_level | triggered_rules |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | S16511000004056 | S16511000004056\|IDA | 359716 | 2559344 | CL |  | 2003-08-01 | TUNIS | BERGE DU LAC | 0 | UNKNOWN | UNKNOWN | UNKNOWN |  | 58356 | 5247TU186 |  |  |  |  |  | 522 | FLOTTE ENTREPRISE | IDA |  | 03 | M | 0 | 2016-03-14 | 2016-03-15 | 2016-03-15 | 2023-09-25 | 0.000 | 0.000 | 0.000 | 0.000 | 2 | C | PR | 1 | 0 | 61 | False | False | False | False |  |  |  |  |  |  |  |
| 2 | S16511000012866 | S16511000012866\|CAS | 359716 | 2559344 | CL |  | 2003-08-01 | TUNIS | BERGE DU LAC | 0 | UNKNOWN | UNKNOWN | UNKNOWN |  | 58445 | 5255TU186 |  |  |  |  |  | 522 | FLOTTE ENTREPRISE | CAS |  | 05 | M | 0 | 2016-05-17 | 2016-06-02 | 2016-06-02 | 2020-09-08 | 0.000 | 0.000 | 112.972 | 112.972 | 2 | C | CD | 16 | 0 | 125 | False | True | False | False |  |  |  |  |  |  |  |
| 3 | S16511000030807 | S16511000030807\|CAS | 359716 | 2559344 | CL |  | 2003-08-01 | TUNIS | BERGE DU LAC | 0 | UNKNOWN | UNKNOWN | UNKNOWN |  | 77951 | 6686TU147 |  |  |  |  |  | 522 | FLOTTE ENTREPRISE | CAS |  | 02 | M | 2 | 2016-11-29 | 2016-11-29 | 2016-11-29 | 2019-11-21 | 0.000 | 0.000 | 69.956 | 69.956 | 2 | C | CD | 0 | 0 | 333 | False | False | False | False |  |  |  |  |  |  |  |
| 4 | S16511000030807 | S16511000030807\|TR | 359716 | 2559344 | CL |  | 2003-08-01 | TUNIS | BERGE DU LAC | 0 | UNKNOWN | UNKNOWN | UNKNOWN |  | 77951 | 6686TU147 |  |  |  |  |  | 522 | FLOTTE ENTREPRISE | TR |  | 02 | M | 2 | 2016-11-29 | 2016-11-29 | 2016-11-29 | 2019-11-21 | 1731.060 | 0.000 | 1731.060 | 1731.060 | 2 | C | CD | 0 | 0 | 333 | False | False | False | False |  |  |  |  |  |  |  |
| 5 | S16511000036412 | S16511000036412\|RCM | 359716 | 2559344 | CL |  | 2003-08-01 | TUNIS | BERGE DU LAC | 0 | UNKNOWN | UNKNOWN | UNKNOWN |  | 58445 | 5255TU186 |  |  |  |  |  | 522 | FLOTTE ENTREPRISE | RCM |  | 05 | M | 0 | 2016-05-17 | 2017-05-12 | 2017-05-12 | 2020-09-08 | 0.000 | 0.000 | 0.000 | -5590.798 | 2 | C | CD | 360 | 0 | 137 | False | True | False | False |  |  |  |  |  |  |  |

### vw_score_explanation

Extra checks:
- row_count: `0`

No sample rows.

### vw_vehicle_history

Extra checks:
- row_count: `128130`
- dernier_vhs_score_not_null_count: `0`

| vehicule_sk | immatriculation | vin | marque | modele | genre_vehicule | usage_vehicule | motorisation | nb_sinistres | nb_inspections | montant_total_sinistres | dernier_vhs_score | dernier_safety_grade | derniere_vhs_decision | dernier_is_drivable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | UNKNOWN | UNKNOWN |  |  |  |  |  | 3923 | 0 | 40546966.074 |  |  |  |  |
| 1 | #101902REM |  |  |  |  |  |  | 1 | 0 | 330.305 |  |  |  |  |
| 2 | #105518TRA |  |  |  |  |  |  | 1 | 0 | 470.366 |  |  |  |  |
| 3 | #10703MK |  |  |  |  |  |  | 1 | 0 | 791.321 |  |  |  |  |
| 4 | #108890RS |  |  |  |  |  |  | 1 | 0 | 3199.155 |  |  |  |  |

### vw_worklist_investigation

Extra checks:
- row_count: `381893`
- score_global_not_null_count: `0`

| rank_priority | sinistre_sk | num_sinistre | code_garantie | libelle_garantie | client_sk | num_client | code_nature_client | gouvernorat_client | num_contrat | num_avenant | num_mise_a_jour | vehicule_sk | immatriculation | vin | marque | modele | code_produit | libelle_produit | date_survenance | date_declaration | montant_total | montant_total_net | delai_declaration_jours | anciennete_contrat_jours | is_declaration_antidatee | is_declaration_tardive | is_sinistre_avant_contrat | is_sinistre_precoce | score_rule_norm | score_ml | score_cross | score_global | risk_level | confidence_level | rules_triggered_count | triggered_rules | vhs_score_displayed | safety_grade | vhs_decision | is_drivable | main_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 369581 | S25110000000119 | BM |  | 3068 | 2563496 | CL | MONASTIR | 202310000000040 | 2 | 1 | 0 | UNKNOWN | UNKNOWN |  |  | 161 | MULTIRISQUES PROFESSIONNELLES | 2025-12-11 | 2025-12-15 | 1300000.000 | 1300000.000 | 4 | 344 | False | False | False | False |  |  |  |  |  |  |  |  |  |  |  |  | Aucun signal majeur |
| 2 | 369580 | S25110000000075 | BM |  | 3068 | 2563496 | CL | MONASTIR | 202310000000040 | 2 | 1 | 0 | UNKNOWN | UNKNOWN |  |  | 161 | MULTIRISQUES PROFESSIONNELLES | 2025-08-18 | 2025-08-23 | 1002141.000 | 1002141.000 | 5 | 229 | False | False | False | False |  |  |  |  |  |  |  |  |  |  |  |  | Aucun signal majeur |
| 3 | 229090 | S19110000000083 | RC |  | 269214 | 1897807 | CL |  | 201710000000939 | 0 | 3 | 0 | UNKNOWN | UNKNOWN |  |  | 161 | MULTIRISQUES PROFESSIONNELLES | 2019-11-04 | 2019-11-08 | 770000.000 | 770000.000 | 4 | 155 | False | False | False | False |  |  |  |  |  |  |  |  |  |  |  |  | Aucun signal majeur |
| 4 | 229089 | S19110000000083 | CONS |  | 269214 | 1897807 | CL |  | 201710000000939 | 0 | 3 | 0 | UNKNOWN | UNKNOWN |  |  | 161 | MULTIRISQUES PROFESSIONNELLES | 2019-11-04 | 2019-11-08 | 736125.948 | 736125.948 | 4 | 155 | False | False | False | False |  |  |  |  |  |  |  |  |  |  |  |  | Aucun signal majeur |
| 5 | 377146 | S24110000000092 | MATP |  | 453365 | 2838296 | CL | MONASTIR | 202410000000053 | 0 | 0 | 0 | UNKNOWN | UNKNOWN |  |  | 161 | MULTIRISQUES PROFESSIONNELLES | 2024-10-20 | 2024-10-21 | 606255.063 | 606255.063 | 1 | 268 | False | False | False | False |  |  |  |  |  |  |  |  |  |  |  |  | Aucun signal majeur |
