# IRISv2 Mart Views Validation

Generated at: 2026-06-17T23:19:32

This validation is read-only. It queries existing `iris_mart` views and does not modify PostgreSQL objects or run scoring.

## 1. Summary

- final_status: `OK`
- view_count: `6`
- warning_count: `0`
- failure_count: `0`

## 2. View Inventory

| view_name | status | column_count |
| --- | --- | --- |
| vw_client_behavior | OK | 12 |
| vw_dashboard_global | OK | 12 |
| vw_dossier_360 | OK | 54 |
| vw_score_explanation | OK | 14 |
| vw_vehicle_history | OK | 15 |
| vw_worklist_investigation | OK | 42 |

## 3. Row Counts

| view_name | status | row_count | reason |
| --- | --- | --- | --- |
| vw_client_behavior | OK | 461882 | View compiled and returned coherent row counts |
| vw_dashboard_global | OK | 1 | View compiled and returned coherent row counts |
| vw_dossier_360 | OK | 381893 | View compiled and returned coherent row counts |
| vw_score_explanation | OK | 194256 | View compiled and returned coherent row counts |
| vw_vehicle_history | OK | 128130 | View compiled and returned coherent row counts |
| vw_worklist_investigation | OK | 381893 | View compiled and returned coherent row counts |

## 4. Score/VHS Readiness Warnings

- No score/VHS readiness warnings.

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
| 2 | 132 | CL |  | GABES | MARETH | 0 | 0 |  | 0 | 0 |  |
| 3 | 167 | CL |  | MAHDIA | EL JEM | 0 | 0 |  | 0 | 0 |  |
| 4 | 170 | CL |  | SFAX | SFAX | 0 | 0 |  | 0 | 0 |  |

### vw_dashboard_global

Extra checks:
- row_count: `1`
- full_row: `nombre_sinistres=381893; montant_total_sinistres=725309705.589; montant_total_net=616397879.937; nombre_declarations_antidatees=73; nombre_declarations_tardives=128689; nombre_sinistres_avant_contrat=46; nombre_sinistres_precoces=53991; dossiers_normal=381223; dossiers_faible=670; dossiers_moyen=0; dossiers_eleve=0; score_global_moyen=5.2193551966126638`

| nombre_sinistres | montant_total_sinistres | montant_total_net | nombre_declarations_antidatees | nombre_declarations_tardives | nombre_sinistres_avant_contrat | nombre_sinistres_precoces | dossiers_normal | dossiers_faible | dossiers_moyen | dossiers_eleve | score_global_moyen |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 381893 | 725309705.589 | 616397879.937 | 73 | 128689 | 46 | 53991 | 381223 | 670 | 0 | 0 | 5.2193551966126638 |

### vw_dossier_360

Extra checks:
- row_count: `381893`
- sinistre_sk_null_count: `0`
- score_global_not_null_count: `381893`

| sinistre_sk | num_sinistre | sinistre_natural_key | client_sk | num_client | code_nature_client | sexe | date_naissance | gouvernorat_client | localite_client | contrat_sk | num_contrat | num_avenant | num_mise_a_jour | situation_contrat | vehicule_sk | immatriculation | vin | marque | modele | genre_vehicule | usage_vehicule | code_produit | libelle_produit | code_garantie | libelle_garantie | code_cause_sinistre | code_nature_sinistre | code_sous_nature_sinistre | date_survenance | date_declaration | date_ouverture | date_cloture | montant_evaluation_initiale | montant_declare | montant_total | montant_total_net | code_etat_sinistre | etat_garantie | motif_cloture | delai_declaration_jours | delai_ouverture_jours | anciennete_contrat_jours | is_declaration_antidatee | is_declaration_tardive | is_sinistre_avant_contrat | is_sinistre_precoce | score_rule_norm | score_ml | score_cross | score_global | risk_level | confidence_level | triggered_rules |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | S16511000004056 | S16511000004056\|IDA | 359716 | 2559344 | CL |  | 2003-08-01 | TUNIS | BERGE DU LAC | 0 | UNKNOWN | UNKNOWN | UNKNOWN |  | 58356 | 5247TU186 |  |  |  |  |  | 522 | FLOTTE ENTREPRISE | IDA |  | 03 | M | 0 | 2016-03-14 | 2016-03-15 | 2016-03-15 | 2023-09-25 | 0.000 | 0.000 | 0.000 | 0.000 | 2 | C | PR | 1 | 0 | 61 | False | False | False | False | 7.692300 |  |  | 7.692300 | NORMAL | RULE_BASED | CONTRAT_INCONNU |
| 2 | S16511000012866 | S16511000012866\|CAS | 359716 | 2559344 | CL |  | 2003-08-01 | TUNIS | BERGE DU LAC | 0 | UNKNOWN | UNKNOWN | UNKNOWN |  | 58445 | 5255TU186 |  |  |  |  |  | 522 | FLOTTE ENTREPRISE | CAS |  | 05 | M | 0 | 2016-05-17 | 2016-06-02 | 2016-06-02 | 2020-09-08 | 0.000 | 0.000 | 112.972 | 112.972 | 2 | C | CD | 16 | 0 | 125 | False | True | False | False | 19.230800 |  |  | 19.230800 | NORMAL | RULE_BASED | CONTRAT_INCONNU, DECLARATION_TARDIVE |
| 3 | S16511000030807 | S16511000030807\|CAS | 359716 | 2559344 | CL |  | 2003-08-01 | TUNIS | BERGE DU LAC | 0 | UNKNOWN | UNKNOWN | UNKNOWN |  | 77951 | 6686TU147 |  |  |  |  |  | 522 | FLOTTE ENTREPRISE | CAS |  | 02 | M | 2 | 2016-11-29 | 2016-11-29 | 2016-11-29 | 2019-11-21 | 0.000 | 0.000 | 69.956 | 69.956 | 2 | C | CD | 0 | 0 | 333 | False | False | False | False | 7.692300 |  |  | 7.692300 | NORMAL | RULE_BASED | CONTRAT_INCONNU |
| 4 | S16511000030807 | S16511000030807\|TR | 359716 | 2559344 | CL |  | 2003-08-01 | TUNIS | BERGE DU LAC | 0 | UNKNOWN | UNKNOWN | UNKNOWN |  | 77951 | 6686TU147 |  |  |  |  |  | 522 | FLOTTE ENTREPRISE | TR |  | 02 | M | 2 | 2016-11-29 | 2016-11-29 | 2016-11-29 | 2019-11-21 | 1731.060 | 0.000 | 1731.060 | 1731.060 | 2 | C | CD | 0 | 0 | 333 | False | False | False | False | 7.692300 |  |  | 7.692300 | NORMAL | RULE_BASED | CONTRAT_INCONNU |
| 5 | S16511000036412 | S16511000036412\|RCM | 359716 | 2559344 | CL |  | 2003-08-01 | TUNIS | BERGE DU LAC | 0 | UNKNOWN | UNKNOWN | UNKNOWN |  | 58445 | 5255TU186 |  |  |  |  |  | 522 | FLOTTE ENTREPRISE | RCM |  | 05 | M | 0 | 2016-05-17 | 2017-05-12 | 2017-05-12 | 2020-09-08 | 0.000 | 0.000 | 0.000 | -5590.798 | 2 | C | CD | 360 | 0 | 137 | False | True | False | False | 26.923100 |  |  | 26.923100 | FAIBLE | RULE_BASED | CONTRAT_INCONNU, DECLARATION_TARDIVE, MONTANT_TOTAL_NET_NEGATIF |

### vw_score_explanation

Extra checks:
- row_count: `194256`

| num_sinistre | sinistre_sk | code_garantie | libelle_garantie | score_global | risk_level | confidence_level | rule_code | rule_name | rule_category | observed_value | threshold_value | rule_weight | rule_contribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S17511000021299 | 18033 | CAS |  | 11.538500 | NORMAL | RULE_BASED | DECLARATION_TARDIVE | Déclaration tardive | DELAI | 9.0 | >5 jours | 15.0000 | 15.000000 |
| S17511000008168 | 18034 | RCM |  | 11.538500 | NORMAL | RULE_BASED | DECLARATION_TARDIVE | Déclaration tardive | DELAI | 31.0 | >5 jours | 15.0000 | 15.000000 |
| S21511000023079 | 18036 | RCM |  | 11.538500 | NORMAL | RULE_BASED | DECLARATION_TARDIVE | Déclaration tardive | DELAI | 12.0 | >5 jours | 15.0000 | 15.000000 |
| S23511000003827 | 18041 | RCM |  | 11.538500 | NORMAL | RULE_BASED | DECLARATION_TARDIVE | Déclaration tardive | DELAI | 8.0 | >5 jours | 15.0000 | 15.000000 |
| S24511000005679 | 18042 | CAS |  | 11.538500 | NORMAL | RULE_BASED | DECLARATION_TARDIVE | Déclaration tardive | DELAI | 12.0 | >5 jours | 15.0000 | 15.000000 |

### vw_vehicle_history

Extra checks:
- row_count: `128130`
- dernier_vhs_score_not_null_count: `224`

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
- score_global_not_null_count: `381893`

| rank_priority | sinistre_sk | num_sinistre | code_garantie | libelle_garantie | client_sk | num_client | code_nature_client | gouvernorat_client | num_contrat | num_avenant | num_mise_a_jour | vehicule_sk | immatriculation | vin | marque | modele | code_produit | libelle_produit | date_survenance | date_declaration | montant_total | montant_total_net | delai_declaration_jours | anciennete_contrat_jours | is_declaration_antidatee | is_declaration_tardive | is_sinistre_avant_contrat | is_sinistre_precoce | score_rule_norm | score_ml | score_cross | score_global | risk_level | confidence_level | rules_triggered_count | triggered_rules | vhs_score_displayed | safety_grade | vhs_decision | is_drivable | main_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 340433 | S22510000000829 | RCM |  | 432905 | 2557917 | CL | BIZERTE | UNKNOWN | UNKNOWN | UNKNOWN | 81201 | 6920TU105 |  |  |  | 522 | FLOTTE ENTREPRISE | 2022-11-25 | 2022-12-19 | 383000.000 | 383000.000 | 24 | 324 | False | True | False | False | 34.615400 |  |  | 34.615400 | FAIBLE | RULE_BASED | 3 | CONTRAT_INCONNU, DECLARATION_TARDIVE, MONTANT_TOTAL_ELEVE |  |  |  |  | Déclaration tardive |
| 2 | 275793 | S23510000000678 | RCC |  | 177978 | 2697822 | CL | MANNOUBA | 201850000043199 | 2 | 0 | 84371 | 7147TU139 |  |  |  | 551 | USAGE TPM (SUP À 3.5 T) | 2023-07-01 | 2023-12-01 | 362073.197 | 362073.197 | 153 | 22 | False | True | False | True | 34.615400 |  |  | 34.615400 | FAIBLE | RULE_BASED | 3 | DECLARATION_TARDIVE, MONTANT_TOTAL_ELEVE, SINISTRE_PRECOCE |  |  |  |  | Déclaration tardive |
| 3 | 295707 | S19511000003767 | RCM |  | 336854 | 1592731 | CL | ARIANA | 201950000001727 | 0 | 1 | 24798 | 2788TU68 |  |  |  | 542 | UTILITAIRE (SUP.à 3.5T) | 2019-02-06 | 2019-02-15 | 349000.000 | 349000.000 | 9 | 27 | False | True | False | True | 34.615400 |  |  | 34.615400 | FAIBLE | RULE_BASED | 3 | DECLARATION_TARDIVE, MONTANT_TOTAL_ELEVE, SINISTRE_PRECOCE |  |  |  |  | Déclaration tardive |
| 4 | 275791 | S23510000000678 | CONS |  | 177978 | 2697822 | CL | MANNOUBA | 201850000043199 | 2 | 0 | 84371 | 7147TU139 |  |  |  | 551 | USAGE TPM (SUP À 3.5 T) | 2023-07-01 | 2023-12-01 | 327645.817 | 327645.817 | 153 | 22 | False | True | False | True | 34.615400 |  |  | 34.615400 | FAIBLE | RULE_BASED | 3 | DECLARATION_TARDIVE, MONTANT_TOTAL_ELEVE, SINISTRE_PRECOCE |  |  |  |  | Déclaration tardive |
| 5 | 346010 | S23510000000301 | RCC |  | 329617 | 1489735 | CL | JENDOUBA | 202150000011465 | 0 | 2 | 79148 | 6771TU81 |  |  |  | 521 | AFFAIRE ET PROMENADE | 2023-04-30 | 2023-08-15 | 195588.687 | 195588.687 | 107 | 7 | False | True | False | True | 34.615400 |  |  | 34.615400 | FAIBLE | RULE_BASED | 3 | DECLARATION_TARDIVE, MONTANT_TOTAL_ELEVE, SINISTRE_PRECOCE |  |  |  |  | Déclaration tardive |
