# IRISv2 Automobile Reference Label Diagnostic

Generated at: 2026-06-17T15:53:42

This diagnostic is read-only. It profiles the automobile reference-label perimeter in `iris_dw`; it does not modify PostgreSQL, Silver files, loaders, scoring, marts, or orchestration.

Automobile perimeter: product codes starting with `5`.


## 1. Executive Summary

- auto_product_count: `37`
- auto_product_missing_label_count: `0`
- auto_prime_rows: `517600`
- auto_sinistre_rows: `378167`
- auto_garantie_missing_label_count: `25`
- auto_cause_missing_label_count: `0`
- auto_intermediaire_missing_label_count: `199`
- auto_delegation_missing_label_count: `5`
- validation_status: `WARNING`

## 2. Schema Discovery

| table | exists | detected_code_column | detected_label_column | available_columns |
| --- | --- | --- | --- | --- |
| dim_produit | True | code_produit | libelle_produit | code_famille_produit, code_formule, code_produit, created_at, libelle_produit, produit_natural_key, produit_sk, source_system, updated_at |
| fact_prime | True |  |  | client_sk, contrat_sk, created_at, date_debut_contrat_sk, date_debut_effet_sk, date_fin_contrat_sk, date_fin_effet_sk, delegation_sk, etl_run_id, intermediaire_sk, prime_natural_key, prime_sk, produit_sk, source_system, total_prime, vehicule_sk |
| fact_sinistre | True |  |  | anciennete_contrat_jours, cause_sinistre_sk, client_sk, code_etat_sinistre, contrat_sk, created_at, date_cloture_sk, date_debut_effet_sk, date_declaration_sk, date_fin_effet_sk, date_ouverture_sk, date_survenance_sk, delai_declaration_jours, delai_ouverture_jours, delegation_sk, etat_garantie, etl_run_id, garantie_sk, intermediaire_sk, is_declaration_antidatee, is_declaration_tardive, is_sinistre_avant_contrat, is_sinistre_precoce, montant_declare, montant_evaluation_initiale, montant_paye_garantie, montant_prevision, montant_provision, montant_recours, montant_total, montant_total_net, motif_cloture, num_sinistre, numero_risque, produit_sk, sinistre_natural_key, sinistre_sk, source_system, vehicule_sk |
| dim_garantie | True | code_garantie | libelle_garantie | code_garantie, created_at, famille_garantie, garantie_natural_key, garantie_sk, libelle_garantie, source_system, updated_at |
| dim_cause_sinistre | True | code_cause_sinistre | libelle_cause_sinistre | cause_sinistre_natural_key, cause_sinistre_sk, code_cause_sinistre, code_nature_sinistre, code_sous_nature_sinistre, created_at, is_vol, is_vol_avec_retrouvaille, libelle_cause_sinistre, libelle_nature_sinistre, libelle_sous_nature_sinistre, source_system, updated_at |
| dim_intermediaire | True | code_intermediaire | nom_intermediaire | code_intermediaire, code_nature_intermediaire, created_at, intermediaire_natural_key, intermediaire_sk, nom_intermediaire, source_system, type_intermediaire, updated_at |
| dim_delegation | True | code_delegation | libelle_delegation | code_delegation, created_at, delegation_natural_key, delegation_sk, libelle_delegation, source_system, updated_at |

## 3. dim_produit Automobile Labels

- total_product_rows_excluding_unknown: `86`
- auto_product_rows: `37`
- auto_product_missing_label_rows: `0`
- product_code_column: `code_produit`
- product_label_column: `libelle_produit`
No rows.

## 4. fact_prime Automobile Usage

- total_prime_rows: `585514`
- auto_prime_rows: `517600`
- auto_prime_rows_with_missing_product_label: `0`
| product_code | product_label | row_count | label_status |
| --- | --- | --- | --- |
| 521 | AFFAIRE ET PROMENADE | 344557 | OK |
| 541 | USAGE UTILITAIRE I (INF.A 3.5T) | 119051 | OK |
| 531 | USAGE AGRICOLE I (INF.A 3.5T) | 11515 | OK |
| 542 | UTILITAIRE (SUP.à 3.5T) | 5628 | OK |
| 571 | TAXI | 5547 | OK |
| 551 | USAGE TPM (SUP À 3.5 T) | 4009 | OK |
| 550 | USAGE TPM (INF À 3.5T) | 3749 | OK |
| 572 | LOUAGE | 3513 | OK |
| 581 | USAGE TRACTEUR AGRICOLE (PARTICULIER) | 3254 | OK |
| 591 | USAGE DEUX ROUES (PRIVEE ET AFFAIRE) | 3003 | OK |
| 543 | USAGE UTILITAIRE II (REMORQUE) | 1835 | OK |
| 573 | TRANSPORT RURAL | 1750 | OK |
| 586 | USAGE ENGINS DE CHANTIERS (SUP À 3.5 T) | 1479 | OK |
| 553 | USAGE TPM REMORQUE (SUP À 3.5 T) | 1472 | OK |
| 579 | TAXI COLLECTIF | 1361 | OK |
| 526 | AUTO-ECOLE TOURISME | 1139 | OK |
| 585 | USAGE ENGINS DE CHANTIERS (INF À 3.5 T) | 928 | OK |
| 532 | USAGE AGRICOLE II(SUP.à 3.5T) | 866 | OK |
| 592 | USAGE VEHICULE A TROIS ROUES TRIPORTEUR | 824 | OK |
| 577 | USAGE TRANSPORT PERSONNEL | 618 | OK |
| 522 | FLOTTE ENTREPRISE | 335 | OK |
| 529 | LOCATION DE VOITURE FLOTTE | 314 | OK |
| 576 | USAGE TRANSPORT TOURISTIQUE | 245 | OK |
| 533 | USAGE AGRICOLE II (REMORQUE) | 210 | OK |
| 523 | USAGE AMBULANCE | 115 | OK |
| 574 | TAXI TOURISTIQUE | 114 | OK |
| 583 | USAGE TRACTEUR AGRICOLE(PUBLIQUE) | 58 | OK |
| 527 | USAGE AUTO-ECOLE UTILITAIRE | 40 | OK |
| 575 | USAGE TRANSPORT PUBLIC DE VOYAGEURS | 39 | OK |
| 524 | CORBILLARDS | 9 | OK |
| 587 | BAKO BEE | 9 | OK |
| 593 | USAGE DEUX ROUES (LOCATION) | 4 | OK |
| 596 | QUADS 3OU4ROUES (PR AF SUP 125 CM3) | 4 | OK |
| 594 | QUADS 3OU4ROUES (PR AF INF 125 CM3) | 3 | OK |
| 584 | USAGE MOISSONNEUSE-BATTEUSE(ENTREPRISE) | 1 | OK |
| 588 | BAKO B-VAN | 1 | OK |
| 595 | QUADS 3OU4ROUES (LOC TOURIS INF 125 CM3) | 1 | OK |

## 5. fact_sinistre Automobile Usage

- total_sinistre_rows: `381893`
- auto_sinistre_rows: `378167`
- auto_sinistre_rows_with_missing_product_label: `0`
| product_code | product_label | row_count | label_status |
| --- | --- | --- | --- |
| 521 | AFFAIRE ET PROMENADE | 243278 | OK |
| 541 | USAGE UTILITAIRE I (INF.A 3.5T) | 75896 | OK |
| 571 | TAXI | 16794 | OK |
| 529 | LOCATION DE VOITURE FLOTTE | 9300 | OK |
| 531 | USAGE AGRICOLE I (INF.A 3.5T) | 5453 | OK |
| 522 | FLOTTE ENTREPRISE | 5016 | OK |
| 572 | LOUAGE | 4363 | OK |
| 551 | USAGE TPM (SUP À 3.5 T) | 3755 | OK |
| 579 | TAXI COLLECTIF | 3465 | OK |
| 542 | UTILITAIRE (SUP.à 3.5T) | 3445 | OK |
| 550 | USAGE TPM (INF À 3.5T) | 1742 | OK |
| 526 | AUTO-ECOLE TOURISME | 1418 | OK |
| 573 | TRANSPORT RURAL | 1153 | OK |
| 543 | USAGE UTILITAIRE II (REMORQUE) | 483 | OK |
| 553 | USAGE TPM REMORQUE (SUP À 3.5 T) | 470 | OK |
| 532 | USAGE AGRICOLE II(SUP.à 3.5T) | 405 | OK |
| 577 | USAGE TRANSPORT PERSONNEL | 309 | OK |
| 586 | USAGE ENGINS DE CHANTIERS (SUP À 3.5 T) | 243 | OK |
| 581 | USAGE TRACTEUR AGRICOLE (PARTICULIER) | 241 | OK |
| 592 | USAGE VEHICULE A TROIS ROUES TRIPORTEUR | 235 | OK |
| 576 | USAGE TRANSPORT TOURISTIQUE | 176 | OK |
| 585 | USAGE ENGINS DE CHANTIERS (INF À 3.5 T) | 176 | OK |
| 574 | TAXI TOURISTIQUE | 111 | OK |
| 591 | USAGE DEUX ROUES (PRIVEE ET AFFAIRE) | 100 | OK |
| 523 | USAGE AMBULANCE | 86 | OK |
| 575 | USAGE TRANSPORT PUBLIC DE VOYAGEURS | 20 | OK |
| 527 | USAGE AUTO-ECOLE UTILITAIRE | 14 | OK |
| 533 | USAGE AGRICOLE II (REMORQUE) | 12 | OK |
| 583 | USAGE TRACTEUR AGRICOLE(PUBLIQUE) | 5 | OK |
| 587 | BAKO BEE | 3 | OK |

## 6. dim_garantie Labels Used In Automobile Sinistres

- garantie_code_column: `code_garantie`
- garantie_label_column: `libelle_garantie`
- distinct_garantie_codes_used: `25`
- garantie_missing_label_count: `25`
| garantie_code | garantie_label | row_count | label_status |
| --- | --- | --- | --- |
| CAS |  | 130853 | MISSING_LABEL |
| RCM |  | 90315 | MISSING_LABEL |
| IDA |  | 54958 | MISSING_LABEL |
| BG |  | 28267 | MISSING_LABEL |
| REM |  | 17539 | MISSING_LABEL |
| ASR |  | 15624 | MISSING_LABEL |
| RCC |  | 13500 | MISSING_LABEL |
| TR |  | 10280 | MISSING_LABEL |
| RCDE |  | 8471 | MISSING_LABEL |
| DOC |  | 4924 | MISSING_LABEL |
| INC |  | 1040 | MISSING_LABEL |
| DEPC |  | 645 | MISSING_LABEL |
| VOL |  | 558 | MISSING_LABEL |
| EXT |  | 464 | MISSING_LABEL |
| DEPA |  | 278 | MISSING_LABEL |
| RCR |  | 205 | MISSING_LABEL |
| RCA |  | 100 | MISSING_LABEL |
| CONS |  | 94 | MISSING_LABEL |
| IC |  | 20 | MISSING_LABEL |
| DC |  | 14 | MISSING_LABEL |
| FM |  | 7 | MISSING_LABEL |
| CAT |  | 6 | MISSING_LABEL |
| EME |  | 2 | MISSING_LABEL |
| IPT |  | 2 | MISSING_LABEL |
| IND |  | 1 | MISSING_LABEL |

## 7. dim_cause_sinistre Labels Used In Automobile Sinistres

- cause_code_column: `code_cause_sinistre`
- cause_label_column: `libelle_cause_sinistre`
- sous_nature_label_column: `libelle_sous_nature_sinistre`
- distinct_cause_codes_used: `20`
- cause_missing_label_count: `0`
- sous_nature_missing_label_count: `15`
| cause_code | nature_code | sous_nature_code | cause_label | sous_nature_label | row_count | cause_label_status | sous_nature_label_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 03 | M | 0 | IDA REC |  | 94312 | OK | MISSING_LABEL |
| 11 | M | 0 | BRIS DE GLACE |  | 53137 | OK | MISSING_LABEL |
| 04 | M | 0 | IDA DEF |  | 52594 | OK | MISSING_LABEL |
| 05 | M | 0 | CONV80 REC |  | 42414 | OK | MISSING_LABEL |
| 01 | C | 1 | CORPOREL |  | 35355 | OK | MISSING_LABEL |
| 06 | M | 0 | CONV80 DEF |  | 24647 | OK | MISSING_LABEL |
| 16 | M | 1 | ASSISTANCEREMORQUAGE |  | 18924 | OK | MISSING_LABEL |
| 02 | M | 2 | DOMMAGES |  | 12356 | OK | MISSING_LABEL |
| 07 | M | 2 | CONNEXE |  | 7413 | OK | MISSING_LABEL |
| 07 | M | 1 | CONNEXE |  | 6834 | OK | MISSING_LABEL |
| 07 | M | 0 | CONNEXE |  | 5971 | OK | MISSING_LABEL |
| 10 | M | 0 | DOMMAGE COLLISION |  | 5844 | OK | MISSING_LABEL |
| 09 | C | 1 | CORP.Recup |  | 4641 | OK | MISSING_LABEL |
| 02 | M | 1 | DOMMAGES |  | 3095 | OK | MISSING_LABEL |
| 08 | C | 0 | MAT.CX |  | 2354 | OK | MISSING_LABEL |
| 01 | C | 3 | CORPOREL |  | 1828 | OK | MISSING_LABEL |
| 12 | M | 1 | INCENDIE | Incendie partielle | 1375 | OK | OK |
| 14 | M | 2 | GESTION ETRANGERE | GEST ETRANGERE RECOURS | 783 | OK | OK |
| 13 | M | 1 | VOL | Vol perte totale | 601 | OK | OK |
| 14 | M | 1 | GESTION ETRANGERE | GEST ETRANGERE DEFENSE | 574 | OK | OK |
| 12 | M | 2 | INCENDIE | Incendie Totale | 527 | OK | OK |
| 05 | M | 1 | CONV80 REC |  | 395 | OK | MISSING_LABEL |
| 13 | M | 2 | VOL | Vol avec retrouvaille | 369 | OK | OK |
| 03 | M | 1 | IDA REC |  | 328 | OK | MISSING_LABEL |
| 15 | M | 3 | DIVERS | TUNISIE AUTOROUTE | 314 | OK | OK |
| 06 | M | 1 | CONV80 DEF |  | 254 | OK | MISSING_LABEL |
| 15 | M | 99 | DIVERS | AUTRES | 252 | OK | OK |
| 04 | M | 1 | IDA DEF |  | 195 | OK | MISSING_LABEL |
| 15 | M | 1 | DIVERS | STEG | 90 | OK | OK |
| 11 | M | 2 | BRIS DE GLACE |  | 85 | OK | MISSING_LABEL |
| 20 | M | 0 | NON IDENTIFIE |  | 67 | OK | MISSING_LABEL |
| 15 | M | 4 | DIVERS | DEFENSE NATIONALE | 51 | OK | OK |
| 15 | M | 2 | DIVERS | SONED | 20 | OK | OK |
| 01 | C | 2 | CORPOREL |  | 17 | OK | MISSING_LABEL |
| 11 | M | 1 | BRIS DE GLACE |  | 17 | OK | MISSING_LABEL |
| 05 | M | 2 | CONV80 REC |  | 14 | OK | MISSING_LABEL |
| 09 | C | 2 | CORP.Recup |  | 14 | OK | MISSING_LABEL |
| 17 | M | 1 | CATAS.NATURELLE | CATAS.NATURELLE | 14 | OK | OK |
| 10 | M | 1 | DOMMAGE COLLISION |  | 12 | OK | MISSING_LABEL |
| 21 | C | 0 | NON IDENTIFIE CX |  | 12 | OK | MISSING_LABEL |
| 04 | M | 2 | IDA DEF |  | 8 | OK | MISSING_LABEL |
| 01 | C | 4 | CORPOREL |  | 7 | OK | MISSING_LABEL |
| 08 | C | 2 | MAT.CX |  | 6 | OK | MISSING_LABEL |
| 18 | M | 1 | EMEUTE | ACTE DE VANDALISME | 6 | OK | OK |
| 03 | M | 2 | IDA REC |  | 4 | OK | MISSING_LABEL |
| 15 | M | 5 | DIVERS | TUNISIE TELECOM | 4 | OK | OK |
| 02 | C | 0 | DOMMAGES |  | 3 | OK | MISSING_LABEL |
| 04 | M | 3 | IDA DEF |  | 3 | OK | MISSING_LABEL |
| 06 | C | 0 | CONV80 DEF |  | 3 | OK | MISSING_LABEL |
| 02 | C | 2 | DOMMAGES |  | 2 | OK | MISSING_LABEL |

## 8. Intermediaire And Delegation Automobile Portfolio Labels


### dim_intermediaire

- sources: `fact_prime, fact_sinistre`
- intermediaire_code_column: `code_intermediaire`
- intermediaire_label_column: `nom_intermediaire`
- distinct_intermediaire_used: `199`
- intermediaire_missing_label_count: `199`
| code | label | usage_rows | label_status |
| --- | --- | --- | --- |
| 626 |  | 20358 | MISSING_LABEL |
| 377 |  | 19416 | MISSING_LABEL |
| 733 |  | 18773 | MISSING_LABEL |
| 668 |  | 17426 | MISSING_LABEL |
| 768 |  | 17290 | MISSING_LABEL |
| 765 |  | 17134 | MISSING_LABEL |
| 763 |  | 16648 | MISSING_LABEL |
| 731 |  | 15299 | MISSING_LABEL |
| 120 |  | 14597 | MISSING_LABEL |
| 658 |  | 14401 | MISSING_LABEL |
| 100 |  | 14291 | MISSING_LABEL |
| 783 |  | 12047 | MISSING_LABEL |
| 585 |  | 11866 | MISSING_LABEL |
| 782 |  | 11406 | MISSING_LABEL |
| 599 |  | 11300 | MISSING_LABEL |
| 774 |  | 10864 | MISSING_LABEL |
| 737 |  | 10494 | MISSING_LABEL |
| 725 |  | 10438 | MISSING_LABEL |
| 775 |  | 10337 | MISSING_LABEL |
| 663 |  | 10289 | MISSING_LABEL |
| 784 |  | 10025 | MISSING_LABEL |
| 689 |  | 9994 | MISSING_LABEL |
| 780 |  | 9498 | MISSING_LABEL |
| 431 |  | 9345 | MISSING_LABEL |
| 676 |  | 9327 | MISSING_LABEL |
| 623 |  | 9286 | MISSING_LABEL |
| 643 |  | 9086 | MISSING_LABEL |
| 754 |  | 9048 | MISSING_LABEL |
| 759 |  | 8972 | MISSING_LABEL |
| 684 |  | 8968 | MISSING_LABEL |
| 651 |  | 8840 | MISSING_LABEL |
| 729 |  | 8527 | MISSING_LABEL |
| 739 |  | 8414 | MISSING_LABEL |
| 773 |  | 8305 | MISSING_LABEL |
| 751 |  | 8222 | MISSING_LABEL |
| 644 |  | 8054 | MISSING_LABEL |
| 730 |  | 7900 | MISSING_LABEL |
| 630 |  | 7831 | MISSING_LABEL |
| 769 |  | 7815 | MISSING_LABEL |
| 400 |  | 7738 | MISSING_LABEL |
| 686 |  | 7653 | MISSING_LABEL |
| 736 |  | 7582 | MISSING_LABEL |
| 778 |  | 7557 | MISSING_LABEL |
| 755 |  | 7495 | MISSING_LABEL |
| 752 |  | 7329 | MISSING_LABEL |
| 687 |  | 7321 | MISSING_LABEL |
| 387 |  | 7158 | MISSING_LABEL |
| 758 |  | 7110 | MISSING_LABEL |
| 590 |  | 7073 | MISSING_LABEL |
| 776 |  | 7039 | MISSING_LABEL |

### dim_delegation

- sources: `fact_prime, fact_sinistre`
- delegation_code_column: `code_delegation`
- delegation_label_column: `libelle_delegation`
- distinct_delegation_used: `5`
- delegation_missing_label_count: `5`
| code | label | usage_rows | label_status |
| --- | --- | --- | --- |
| 1 |  | 483114 | MISSING_LABEL |
| 2 |  | 137664 | MISSING_LABEL |
| 3 |  | 130160 | MISSING_LABEL |
| 4 |  | 77617 | MISSING_LABEL |
| 5 |  | 67212 | MISSING_LABEL |

## 9. Recommendations


### Safe To Enrich Now

- No immediate in-place label enrichment candidate was detected.

### Needs Reference File

- dim_garantie has automobile usage with missing labels; enrich from a governed reference file, not from fact free text.
- dim_intermediaire has automobile usage with missing labels; enrich from a governed reference file, not from fact free text.
- dim_delegation has automobile usage with missing labels; enrich from a governed reference file, not from fact free text.

### Cannot Enrich Due To Ambiguous Grain

- No ambiguous-grain blocker was detected for the checks run.

### Not In Automobile Perimeter

- Product codes outside prefix `5` are intentionally excluded.
- No scoring, mart, loader, or warehouse correction is part of this diagnostic.

## 10. Warnings And Failures


### Failures

- No items.

### Warnings

- Automobile sinistres use garantie codes with missing labels.
- Automobile sinistres use cause codes with missing sous-nature labels.
- Automobile portfolio uses intermediaire rows with missing labels.
- Automobile portfolio uses delegation rows with missing labels.
