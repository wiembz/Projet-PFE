# IRISv2 dim_client Data Quality Diagnostic

Generated at: 2026-06-17T14:28:33

This diagnostic is read-only. It profiles `iris_dw.dim_client`; it does not modify PostgreSQL, Silver files, loaders, scoring, or marts.


## 1. Executive Summary

- total_clients: `461882`
- duplicate_client_natural_keys: `0`
- sexe_null_count: `61245`
- sexe_x_count: `0`
- situation_familiale_null_count: `14411`
- situation_familiale_x_count: `46835`
- date_naissance_null_count: `4003`
- probable_moral_or_incomplete_profile_count: `25280`
- geo_null_code_postal_count: `29983`
- geo_null_localite_count: `25773`
- geo_null_gouvernorat_count: `148491`
- geo_conflicting_code_postal_count: `965`
- geo_autocorrect_candidate_count: `3727`

## 2. General Volume

- total row count: `461882`
- UNKNOWN row count: `1`
- distinct client_natural_key count: `461882`
- duplicate client_natural_key count: `0`
- duplicate client_natural_key row count: `0`
- available dim_client columns: `adresse, client_natural_key, client_sk, code_nature_client, code_postal, created_at, date_debut_client, date_naissance, gouvernorat_client, identifiant_client, localite_client, nombre_enfants, num_client, profession, sexe, situation_familiale, source_system, type_identifiant, updated_at`

## 3. Client Profile Quality

- Distribution limit: `top 50 rows per table`
| column | status | null_count |
| --- | --- | --- |
| sexe | available | 61245 |
| situation_familiale | available | 14411 |
| nombre_enfants | available | 440840 |
| date_naissance | available | 4003 |
| profession | available | 68989 |
| type_identifiant | available | 5 |
| identifiant_client | available | 1 |

## 3.1 code_nature_client Distribution

| code_nature_client | row_count |
| --- | --- |
| CL | 461881 |
| UNKNOWN | 1 |

## 3.2 type_identifiant Distribution

| type_identifiant | row_count |
| --- | --- |
| CIN | 431564 |
| PAS | 15666 |
| FIS | 10991 |
| REG | 3045 |
| SEJ | 611 |
| <NULL> | 5 |

## 3.3 code_nature_client + type_identifiant

| code_nature_client | type_identifiant | row_count |
| --- | --- | --- |
| CL | CIN | 431564 |
| CL | PAS | 15666 |
| CL | FIS | 10991 |
| CL | REG | 3045 |
| CL | SEJ | 611 |
| CL | <NULL> | 4 |
| UNKNOWN | <NULL> | 1 |

## 3.4 code_nature_client + sexe

| code_nature_client | sexe | row_count |
| --- | --- | --- |
| CL | M | 310417 |
| CL | F | 90220 |
| CL | <NULL> | 61244 |
| UNKNOWN | <NULL> | 1 |

## 3.5 code_nature_client + situation_familiale

| code_nature_client | situation_familiale | row_count |
| --- | --- | --- |
| CL | M | 306632 |
| CL | C | 92931 |
| CL | X | 46835 |
| CL | <NULL> | 14410 |
| CL | D | 925 |
| CL | V | 147 |
| CL | S | 1 |
| UNKNOWN | <NULL> | 1 |

## 3.6 code_nature_client + nombre_enfants

| code_nature_client | nombre_enfants | row_count |
| --- | --- | --- |
| CL | <NULL> | 440839 |
| CL | 2 | 8401 |
| CL | 3 | 5786 |
| CL | 1 | 3460 |
| CL | 4 | 1942 |
| CL | 5 | 792 |
| CL | 6 | 309 |
| CL | 7 | 114 |
| CL | 10 | 47 |
| CL | 8 | 47 |
| CL | 20 | 38 |
| CL | 9 | 25 |
| CL | 31 | 14 |
| CL | 32 | 12 |
| CL | 11 | 8 |
| CL | 30 | 7 |
| CL | 60 | 6 |
| CL | 40 | 6 |
| CL | 50 | 5 |
| CL | 89 | 2 |
| CL | 25 | 2 |
| CL | 90 | 2 |
| CL | 80 | 2 |
| CL | 21 | 2 |
| CL | 70 | 2 |
| CL | 14 | 2 |
| CL | 13 | 1 |
| CL | 19 | 1 |
| CL | 45 | 1 |
| CL | 33 | 1 |
| CL | 57 | 1 |
| CL | 51 | 1 |
| CL | 73 | 1 |
| CL | 71 | 1 |
| CL | 91 | 1 |
| UNKNOWN | <NULL> | 1 |

## 4. Probable Moral/Incomplete Profiles

- sexe = X: `0`
- situation_familiale = X: `46835`
- rows where sexe is null: `61245`
- rows where situation_familiale is null: `14411`
- rows where date_naissance is null: `4003`
- rows where nombre_enfants is null: `440840`
- probable_moral_or_incomplete_profile: `25280`
| indicator | count |
| --- | --- |
| base incomplete personal profile | 3473 |
| type_identifiant moral indicator | 14036 |
| profession moral indicator | 0 |
| adresse moral indicator | 8136 |

## 4.1 Sample probable moral/incomplete profiles

| client_sk | client_natural_key | code_nature_client | type_identifiant | sexe | date_naissance | situation_familiale | nombre_enfants | profession |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | UNKNOWN | UNKNOWN |  |  |  |  |  |  |
| 423 | CL\|2670267 | CL | FIS |  | 2014-10-10 |  |  |  |
| 424 | CL\|2568218 | CL | REG |  | 2013-01-07 |  |  |  |
| 427 | CL\|2585922 | CL | REG |  | 2012-10-31 |  |  |  |
| 445 | CL\|2830210 | CL | FIS |  | 2008-10-09 |  |  |  |
| 448 | CL\|2809902 | CL | FIS |  | 2012-09-07 |  |  |  |
| 449 | CL\|1813269 | CL | FIS |  | 2014-05-12 | X |  |  |
| 451 | CL\|2679364 | CL | REG |  | 2014-01-30 |  |  |  |
| 452 | CL\|2603761 | CL | FIS |  | 2015-01-01 |  |  |  |
| 453 | CL\|2795187 | CL | FIS |  | 2018-03-02 |  |  |  |
| 454 | CL\|2807244 | CL | FIS |  | 2019-02-06 |  |  |  |
| 455 | CL\|2849573 | CL | FIS |  | 2022-04-08 |  |  |  |
| 472 | CL\|2657425 | CL | CIN | M | 1976-10-15 | M |  | 25 |
| 527 | CL\|2690687 | CL | CIN | M | 1959-12-10 | M |  | 19 |
| 543 | CL\|2696282 | CL | REG |  | 2010-10-14 |  |  |  |
| 591 | CL\|2690772 | CL | REG |  | 2014-11-24 |  |  |  |
| 607 | CL\|2699034 | CL | CIN | M | 1953-01-15 | M |  | 32 |
| 669 | CL\|2676286 | CL | CIN | M | 1964-12-30 | M |  | 04 |
| 679 | CL\|2700822 | CL | CIN | F | 1960-01-05 | M |  | 03 |
| 750 | CL\|2686366 | CL | CIN | F | 1972-12-18 | M |  | 12 |

## 5. Physical-Person Anomalies

| anomaly | count |
| --- | --- |
| physical_like_rows | 436602 |
| sexe_not_m_f_or_null | 43771 |
| nombre_enfants_negative | 0 |
| nombre_enfants_gt_20 | 68 |
| date_naissance_in_future | 14 |
| age_gt_120 | 1 |
| situation_familiale_suspicious | 42953 |

## 5.1 Sample physical-person anomaly rows

| client_sk | client_natural_key | code_nature_client | type_identifiant | sexe | date_naissance | situation_familiale | nombre_enfants | sexe_not_m_f_or_null | nombre_enfants_negative | nombre_enfants_gt_20 | date_naissance_in_future | age_gt_120 | situation_familiale_suspicious |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3548 | CL\|9900027437 | CL | CIN |  | 1974-07-07 | X |  | True | False | False | False | False | True |
| 3549 | CL\|9900027719 | CL | CIN |  | 1964-03-31 | X |  | True | False | False | False | False | True |
| 3550 | CL\|9900027784 | CL | CIN |  | 1979-10-16 | X |  | True | False | False | False | False | True |
| 3551 | CL\|9900027956 | CL | CIN |  | 1964-08-25 | X |  | True | False | False | False | False | True |
| 3552 | CL\|9900029210 | CL | CIN |  | 1967-01-22 | X |  | True | False | False | False | False | True |
| 3553 | CL\|9900029478 | CL | CIN |  | 1953-03-15 | X |  | True | False | False | False | False | True |
| 3554 | CL\|9900029506 | CL | CIN |  | 1968-09-28 | X |  | True | False | False | False | False | True |
| 3555 | CL\|9900030032 | CL | CIN |  | 1990-09-22 | X |  | True | False | False | False | False | True |
| 3556 | CL\|9900030911 | CL | CIN |  | 1977-11-17 | X |  | True | False | False | False | False | True |
| 3557 | CL\|9900031126 | CL | CIN |  | 1950-01-03 | X |  | True | False | False | False | False | True |
| 3558 | CL\|9900031246 | CL | CIN |  | 1981-12-06 | X |  | True | False | False | False | False | True |
| 3559 | CL\|9900031706 | CL | CIN |  | 1955-02-11 | X |  | True | False | False | False | False | True |
| 3560 | CL\|9900031909 | CL | CIN |  | 1986-10-03 | X |  | True | False | False | False | False | True |
| 3561 | CL\|9900032621 | CL | CIN |  | 1952-12-18 | X |  | True | False | False | False | False | True |
| 3562 | CL\|9900032707 | CL | CIN |  | 1971-01-26 | X |  | True | False | False | False | False | True |
| 3563 | CL\|9900032818 | CL | CIN |  | 1958-08-19 | X |  | True | False | False | False | False | True |
| 3564 | CL\|9900033278 | CL | CIN |  | 1968-07-10 | X |  | True | False | False | False | False | True |
| 3565 | CL\|9900033379 | CL | CIN |  | 1970-03-23 | X |  | True | False | False | False | False | True |
| 3566 | CL\|9900033924 | CL | CIN |  | 1959-12-26 | X |  | True | False | False | False | False | True |
| 3567 | CL\|9900034210 | CL | CIN |  | 1989-06-13 | X |  | True | False | False | False | False | True |
| 3568 | CL\|9900034959 | CL | CIN |  | 1982-02-25 | X |  | True | False | False | False | False | True |
| 3569 | CL\|9900035714 | CL | CIN |  | 1960-07-16 | X |  | True | False | False | False | False | True |
| 3570 | CL\|9900036442 | CL | CIN |  | 1978-06-12 | X |  | True | False | False | False | False | True |
| 3571 | CL\|9900036492 | CL | CIN |  | 1976-05-21 | X |  | True | False | False | False | False | True |
| 3572 | CL\|9900036501 | CL | CIN |  | 1990-07-31 | X |  | True | False | False | False | False | True |
| 3573 | CL\|9900036826 | CL | CIN |  | 1985-03-24 | X |  | True | False | False | False | False | True |
| 3574 | CL\|9900037006 | CL | CIN |  | 1965-10-25 | X |  | True | False | False | False | False | True |
| 3575 | CL\|9900037011 | CL | CIN |  | 1955-01-12 | X |  | True | False | False | False | False | True |
| 3576 | CL\|9900037200 | CL | CIN |  | 1979-02-02 | X |  | True | False | False | False | False | True |
| 3577 | CL\|9900037997 | CL | CIN |  | 1970-01-28 | X |  | True | False | False | False | False | True |
| 3578 | CL\|9900038464 | CL | CIN |  | 1977-11-04 | X |  | True | False | False | False | False | True |
| 3579 | CL\|9900038776 | CL | CIN |  | 1965-05-26 | X |  | True | False | False | False | False | True |
| 3580 | CL\|9900039068 | CL | CIN |  | 1979-03-27 | X |  | True | False | False | False | False | True |
| 3581 | CL\|9900039105 | CL | CIN |  | 1966-01-24 | X |  | True | False | False | False | False | True |
| 3582 | CL\|9900039260 | CL | CIN |  | 1967-01-01 | X |  | True | False | False | False | False | True |
| 3583 | CL\|9900039365 | CL | CIN |  | 1971-05-12 | X |  | True | False | False | False | False | True |
| 3584 | CL\|9900039594 | CL | CIN |  | 1969-02-02 | X |  | True | False | False | False | False | True |
| 3585 | CL\|9900039946 | CL | CIN |  | 1960-01-27 | X |  | True | False | False | False | False | True |
| 3586 | CL\|9900040344 | CL | CIN |  | 1963-01-30 | X |  | True | False | False | False | False | True |
| 3587 | CL\|9900040571 | CL | CIN |  | 1969-06-17 | X |  | True | False | False | False | False | True |
| 3588 | CL\|9900040702 | CL | CIN |  | 1955-08-21 | X |  | True | False | False | False | False | True |
| 3589 | CL\|9900041177 | CL | CIN |  | 1978-07-09 | X |  | True | False | False | False | False | True |
| 3590 | CL\|9900041707 | CL | CIN |  | 1961-05-08 | X |  | True | False | False | False | False | True |
| 3591 | CL\|9900043049 | CL | CIN |  | 1990-06-26 | X |  | True | False | False | False | False | True |
| 3592 | CL\|9900043207 | CL | CIN |  | 1973-08-16 | X |  | True | False | False | False | False | True |
| 3593 | CL\|9900043747 | CL | CIN |  | 1987-03-09 | X |  | True | False | False | False | False | True |
| 3594 | CL\|9900043783 | CL | CIN |  | 1992-10-08 | X |  | True | False | False | False | False | True |
| 3595 | CL\|9900043920 | CL | CIN |  | 1984-10-02 | X |  | True | False | False | False | False | True |
| 3596 | CL\|9900045687 | CL | CIN |  | 1967-08-05 | X |  | True | False | False | False | False | True |
| 3597 | CL\|9900045910 | CL | CIN |  | 1972-09-04 | X |  | True | False | False | False | False | True |

## 6. Geographic Conflicts

- null/empty code_postal count: `29983`
- null/empty localite_client count: `25773`
- null/empty gouvernorat_client count: `148491`
- conflicting code_postal count: `965`
- conflicting localite_client count: `763`
| metric | group_count | max_distinct_localite_per_group | max_distinct_gouvernorat_per_group |
| --- | --- | --- | --- |
| code_postal values | 1219 | 473 | 36 |
| localite_client values | 11356 |  | 1840 |

## 6.1 Top 50 conflicting code_postal values

| code_postal | distinct_localite_count | distinct_gouvernorat_count | total_rows | dominant_localite | dominant_gouvernorat | dominant_pair_count | dominance_percentage |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 473 | 18 | 7721 | TUNIS | TUNIS | 1983 | 25.68% |
| 4060 | 359 | 8 | 2627 | KALAA EL KEBIRA | SOUSSE | 646 | 24.59% |
| 6100 | 332 | 11 | 2735 | SILIANA | SILIANA | 584 | 21.35% |
| 4000 | 306 | 16 | 7626 | SOUSSE | SOUSSE | 3839 | 50.34% |
| 2080 | 271 | 31 | 11231 | ARIANA | ARIANA | 7138 | 63.56% |
| 6052 | 252 | 2 | 628 | OUEDREF | GABES | 92 | 14.65% |
| 6010 | 247 | 2 | 753 | METOUIA | GABES | 92 | 12.22% |
| 5000 | 220 | 7 | 3713 | MONASTIR | MONASTIR | 2061 | 55.51% |
| 1002 | 218 | 36 | 3383 | TUNIS BELVEDERE | TUNIS | 812 | 24.00% |
| 7000 | 202 | 31 | 9749 | BIZERTE | BIZERTE | 6021 | 61.76% |
| 2074 | 190 | 21 | 4759 | EL MOUROUJ | BEN AROUS | 2097 | 44.06% |
| 1140 | 177 | 6 | 2434 | EL FAHS | ZAGHOUAN | 741 | 30.44% |
| 3000 | 174 | 15 | 27236 | SFAX | SFAX | 16500 | 60.58% |
| 2041 | 166 | 20 | 5648 | CITE ETTADHAMEN | ARIANA | 2066 | 36.58% |
| 2000 | 160 | 28 | 4101 | LE BARDO | TUNIS | 2205 | 53.77% |
| 2045 | 156 | 13 | 5535 | CITE EL MHIRI | TUNIS | 3990 | 72.09% |
| 1009 | 150 | 11 | 2852 | EL OUERDIA | TUNIS | 1160 | 40.67% |
| 2010 | 144 | 21 | 6135 | LA MANNOUBA | MANNOUBA | 4147 | 67.60% |
| 2013 | 143 | 12 | 4499 | BEN AROUS | BEN AROUS | 2735 | 60.79% |
| 2052 | 142 | 21 | 3082 | CITE EZZOUHOUR | TUNIS | 1057 | 34.30% |
| 1110 | 139 | 13 | 2210 | MORNAGUIA | MANNOUBA | 1123 | 50.81% |
| 8000 | 132 | 7 | 3142 | NABEUL | NABEUL | 1538 | 48.95% |
| 2083 | 129 | 10 | 2861 | CITE EL GHAZALA 1 | ARIANA | 854 | 29.85% |
| 2036 | 122 | 17 | 3511 | LA SOUKRA | ARIANA | 1205 | 34.32% |
| 3100 | 122 | 16 | 4824 | KAIROUAN | KAIROUAN | 1868 | 38.72% |
| 1145 | 115 | 7 | 2164 | MOHAMADIA | BEN AROUS | 933 | 43.11% |
| 6000 | 115 | 3 | 2236 | GABES | GABES | 857 | 38.33% |
| 2100 | 112 | 8 | 1720 | GAFSA | GAFSA | 765 | 44.48% |
| 6140 | 112 | 4 | 689 | MAKTHAR | SILIANA | 190 | 27.58% |
| 2051 | 111 | 16 | 3328 | EZZAHROUNI | TUNIS | 2154 | 64.72% |
| 2050 | 109 | 10 | 2110 | HAMMAM LIF | BEN AROUS | 1413 | 66.97% |
| 2021 | 106 | 11 | 2576 | OUED ELLIL | MANNOUBA | 1546 | 60.02% |
| 2082 | 106 | 8 | 2400 | FOUCHANA | BEN AROUS | 1051 | 43.79% |
| 2037 | 102 | 10 | 1411 | CITE ENNASR 2 | ARIANA | 447 | 31.68% |
| 9100 | 102 | 4 | 7234 | SIDI BOUZID | SIDI BOUZID | 4375 | 60.48% |
| 4100 | 100 | 7 | 5435 | MEDENINE | MEDENINE | 2342 | 43.09% |
| 1004 | 99 | 7 | 758 | EL MENZAH 1 | TUNIS | 324 | 42.74% |
| 2040 | 98 | 19 | 4058 | RADES | BEN AROUS | 2285 | 56.31% |
| 2094 | 98 | 13 | 2414 | MNIHLA | ARIANA | 1346 | 55.76% |
| 1095 | 98 | 7 | 4794 | SIDI HASSINE | TUNIS | 3119 | 65.06% |
| 1100 | 92 | 6 | 3438 | ZAGHOUAN | ZAGHOUAN | 1817 | 52.85% |
| 2130 | 91 | 3 | 2556 | METLAOUI | GAFSA | 315 | 12.32% |
| 1006 | 90 | 9 | 945 | TUNIS | TUNIS | 242 | 25.61% |
| 2046 | 89 | 8 | 2253 | CITE BHAR LAZREG | TUNIS | 700 | 31.07% |
| 1003 | 89 | 5 | 1381 | CITE EL KHADRA | TUNIS | 761 | 55.10% |
| 2011 | 87 | 19 | 1834 | DENDEN | MANNOUBA | 1110 | 60.52% |
| 2078 | 87 | 6 | 1035 | LA MARSA | TUNIS | 257 | 24.83% |
| 2070 | 85 | 9 | 1450 | LA MARSA | TUNIS | 371 | 25.59% |
| 1053 | 83 | 9 | 3728 | BERGE DU LAC | TUNIS | 2930 | 78.59% |
| 3200 | 83 | 6 | 7578 | TATAOUINE | TATAOUINE | 4192 | 55.32% |

## 6.2 Top 50 conflicting localite_client values

| localite_client | distinct_gouvernorat_count | total_rows | dominant_gouvernorat | dominance_percentage |
| --- | --- | --- | --- | --- |
| K) | 1840 | 1840 | 1602-032918 | 0.05% |
| BIAT) | 1102 | 1102 | 1605-035089 | 0.09% |
| STRIE (UBC | 384 | 384 | 1605-035118 | 0.26% |
| (ABC) | 93 | 93 | 1703-044298 | 1.08% |
| ENNES ENTR | 80 | 80 | 1609-039784 | 1.25% |
| L AMRI | 28 | 28 | 1811-059328 | 3.57% |
| ELAMRI | 25 | 25 | 1611-042026 | 4.00% |
| TUNIS | 23 | 7490 | TUNIS | 9.37% |
| CITE EZZOUHOUR | 20 | 1663 | TUNIS | 63.68% |
| CITE ERRIADH | 19 | 290 | BEN AROUS | 26.90% |
| CITE ENNASR | 18 | 362 | ARIANA | 40.88% |
| CITE ENNOUR | 18 | 344 | TUNIS | 36.05% |
| CITE ESSAADA | 18 | 99 | TUNIS | 19.19% |
| CITE EL BASSATINE | 16 | 160 | ZAGHOUAN | 26.25% |
| TION CIVIL | 16 | 16 | 1701-042861 | 6.25% |
| ECTION CIV | 15 | 15 | 1805-055505 | 6.67% |
| CITE COMMERCIALE | 13 | 152 | TATAOUINE | 50.00% |
| CITE NOUVELLE | 12 | 427 | MEDENINE | 61.36% |
| CITE ETTAHRIR | 12 | 272 | GABES | 12.13% |
| CITE 7 NOVEMBRE | 12 | 89 | BEN AROUS | 26.97% |
| CITE ENNACIM | 11 | 159 | GAFSA | 52.20% |
| RTS | 11 | 11 | 1611-041636 | 9.09% |
| UNISIENNE | 11 | 11 | 1801-052676 | 9.09% |
| CITE EL AMEL | 10 | 421 | GAFSA | 69.12% |
| CITE AFH | 10 | 263 | KEF | 35.74% |
| CITE SNIT | 10 | 30 | NABEUL | 23.33% |
| LAMRI | 10 | 10 | 1711-051872 | 10.00% |
| CITE IBN KHALDOUN | 9 | 267 | SIDI BOUZID | 8.24% |
| CITE ENNOUZHA | 9 | 190 | TATAOUINE | 25.79% |
| EL MANSOURA | 9 | 85 | MANNOUBA | 44.71% |
| CITE HACHED | 9 | 51 | BEN AROUS | 19.61% |
| RIADH | 9 | 48 | SILIANA | 50.00% |
| SFAX | 8 | 29468 | SFAX | 56.35% |
| MNIHLA | 8 | 1879 | ARIANA | 72.01% |
| CITE EL INTILAKA | 8 | 358 | TUNIS | 75.98% |
| CITE EL IZDIHAR | 8 | 128 | GABES | 39.84% |
| CITE MONGI SLIM | 8 | 112 | TUNIS | 71.43% |
| CITE TAIEB MHIRI | 8 | 77 | BEN AROUS | 29.87% |
| CITE ESSALEM | 8 | 57 | BEN AROUS | 33.33% |
| ENNOUR | 8 | 13 | ZAGHOUAN | 46.15% |
| SOUSSE | 7 | 7857 | SOUSSE | 51.33% |
| BEN AROUS | 7 | 5551 | BEN AROUS | 50.12% |
| CITE JARDINS | 7 | 245 | TUNIS | 91.02% |
| CITE SPROLS | 7 | 133 | TUNIS | 83.46% |
| CITE RIADH | 7 | 122 | SOUSSE | 42.62% |
| ERRIADH | 7 | 105 | MEDENINE | 44.76% |
| SIDI MANSOUR | 7 | 70 | SFAX | 64.29% |
| CITE 20 MARS | 7 | 61 | ZAGHOUAN | 47.54% |
| CITE EL HANA | 7 | 58 | BEN AROUS | 70.69% |
| ESSAADA | 7 | 46 | ZAGHOUAN | 36.96% |

## 7. Auto-Correction Candidates

- candidate group count: `3727`
- candidate row count: `257710`

## 7.1 Candidate Type A: code_postal + localite -> gouvernorat

| candidate_type | code_postal | localite_client | candidate_rows | known_gouvernorat_rows | recommended_gouvernorat | dominance_percentage |
| --- | --- | --- | --- | --- | --- | --- |
| A | 3000 | SFAX | 9309 | 16508 | SFAX | 99.95% |
| A | 7000 | BIZERTE | 3182 | 6022 | BIZERTE | 99.98% |
| A | 2080 | ARIANA | 3139 | 7142 | ARIANA | 99.94% |
| A | 4000 | SOUSSE | 2897 | 3844 | SOUSSE | 99.87% |
| A | 3100 | KAIROUAN | 2628 | 1872 | KAIROUAN | 99.79% |
| A | 3200 | TATAOUINE | 2601 | 4193 | TATAOUINE | 99.98% |
| A | 1000 | TUNIS | 2395 | 395 | TUNIS | 97.22% |
| A | 9100 | SIDI BOUZID | 2277 | 4376 | SIDI BOUZID | 99.98% |
| A | 4100 | MEDENINE | 1649 | 2342 | MEDENINE | 100.00% |
| A | 2041 | CITE ETTADHAMEN | 1456 | 2068 | ARIANA | 99.90% |
| A | 2013 | BEN AROUS | 1421 | 2737 | BEN AROUS | 99.93% |
| A | 8000 | NABEUL | 1239 | 1539 | NABEUL | 99.94% |
| A | 6000 | GABES | 1173 | 857 | GABES | 100.00% |
| A | 5000 | MONASTIR | 1153 | 2062 | MONASTIR | 99.95% |
| A | 8060 | BENI KHIAR | 1091 | 666 | NABEUL | 99.70% |
| A | 8100 | JENDOUBA | 1065 | 2437 | JENDOUBA | 100.00% |
| A | 3040 | SFAX | 1039 | 35 | SFAX | 100.00% |
| A | 9170 | REGUEB | 1037 | 1848 | SIDI BOUZID | 100.00% |
| A | 1000 | TUNIS R P | 975 | 1 | ARIANA | 100.00% |
| A | 8070 | KORBA | 953 | 1578 | NABEUL | 99.94% |
| A | 1100 | ZAGHOUAN | 928 | 1818 | ZAGHOUAN | 99.94% |
| A | 2040 | RADES | 918 | 2288 | BEN AROUS | 99.87% |
| A | 8030 | GROMBALIA | 912 | 1688 | NABEUL | 100.00% |
| A | 7016 | EL ALIA | 895 | 1197 | BIZERTE | 99.92% |
| A | 1002 | TUNIS | 869 | 120 | TUNIS | 96.67% |
| A | 5050 | MOKNINE | 807 | 1038 | MONASTIR | 100.00% |
| A | 1200 | KASSERINE | 795 | 1799 | KASSERINE | 99.78% |
| A | 4070 | MSAKEN | 792 | 2315 | SOUSSE | 99.96% |
| A | 8050 | HAMMAMET | 780 | 2741 | NABEUL | 99.93% |
| A | 7030 | MATEUR | 772 | 1080 | BIZERTE | 99.91% |
| A | 4070 | M SAKEN | 723 | 6 | SOUSSE | 100.00% |
| A | 5100 | MAHDIA | 721 | 913 | MAHDIA | 99.78% |
| A | 2130 | METLAOUI | 713 | 315 | GAFSA | 100.00% |
| A | 6100 | SILIANA | 705 | 585 | SILIANA | 99.83% |
| A | 5140 | SOUASSI | 703 | 775 | MAHDIA | 99.74% |
| A | 2000 | LE BARDO | 701 | 2210 | TUNIS | 99.77% |
| A | 5020 | JEMMEL | 668 | 6 | MONASTIR | 100.00% |
| A | 2100 | GAFSA | 641 | 768 | GAFSA | 99.61% |
| A | 1140 | EL FAHS | 638 | 743 | ZAGHOUAN | 99.73% |
| A | 2021 | OUED ELLIL | 614 | 1558 | MANNOUBA | 99.23% |
| A | 2036 | LA SOUKRA | 599 | 1210 | ARIANA | 99.59% |
| A | 2051 | EZZAHROUNI | 575 | 2158 | TUNIS | 99.81% |
| A | 9010 | NEFZA | 562 | 923 | BEJA | 99.57% |
| A | 4060 | KALAA EL KEBIRA | 542 | 646 | SOUSSE | 100.00% |
| A | 5080 | TEBOULBA | 527 | 1415 | MONASTIR | 100.00% |
| A | 7150 | TAJEROUINE | 526 | 269 | KEF | 99.26% |
| A | 6080 | MARETH | 510 | 436 | GABES | 99.77% |
| A | 2120 | REDEYEF | 493 | 1541 | GAFSA | 100.00% |
| A | 9000 | BEJA | 485 | 2136 | BEJA | 99.91% |
| A | 5040 | ZERAMDINE | 473 | 583 | MONASTIR | 99.83% |
| A | 4170 | ZARZIS | 465 | 436 | MEDENINE | 99.77% |
| A | 3021 | SFAX | 459 | 3 | SFAX | 100.00% |
| A | 2082 | FOUCHANA | 453 | 1053 | BEN AROUS | 99.81% |
| A | 2041 | ARIANA | 451 | 6 | ARIANA | 100.00% |
| A | 4180 | JERBA | 447 | 939 | MEDENINE | 97.98% |
| A | 1095 | TUNIS | 445 | 7 | TUNIS | 100.00% |
| A | 5180 | KSOUR ESSEF | 445 | 6 | MAHDIA | 100.00% |
| A | 2034 | EZZAHRA | 436 | 1558 | BEN AROUS | 99.87% |
| A | 2000 | BARDO | 436 | 28 | TUNIS | 96.43% |
| A | 4060 | KALAA KEBIRA | 435 | 59 | SOUSSE | 98.31% |
| A | 7050 | MENZEL BOURGUIBA | 432 | 1826 | BIZERTE | 99.95% |
| A | 4011 | HAMMAM SOUSSE | 430 | 817 | SOUSSE | 100.00% |
| A | 6020 | EL HAMMA | 424 | 813 | GABES | 100.00% |
| A | 4200 | KEBILI | 418 | 336 | KEBILI | 100.00% |
| A | 2240 | NEFTA | 401 | 529 | TOZEUR | 100.00% |
| A | 3040 | BIR ALI | 400 | 828 | SFAX | 99.88% |
| A | 4160 | BEN GUERDANE | 398 | 2391 | MEDENINE | 100.00% |
| A | 8040 | BOUARGOUB | 395 | 10 | NABEUL | 100.00% |
| A | 2110 | MOULARES | 393 | 898 | GAFSA | 100.00% |
| A | 8011 | DAR CHAABANE | 388 | 165 | NABEUL | 98.18% |
| A | 4022 | AKOUDA | 379 | 670 | SOUSSE | 99.70% |
| A | 3011 | SFAX | 375 | 2 | SFAX | 100.00% |
| A | 2078 | LA MARSA | 364 | 73 | TUNIS | 98.63% |
| A | 1110 | MORNAGUIA | 333 | 1131 | MANNOUBA | 99.29% |
| A | 1053 | LES BERGES DU LAC 2 | 322 | 15 | TUNIS | 100.00% |
| A | 1009 | EL OUERDIA | 319 | 1160 | TUNIS | 100.00% |
| A | 7070 | RAS JEBEL | 310 | 887 | BIZERTE | 100.00% |
| A | 2052 | CITE EZZOUHOUR | 301 | 1058 | TUNIS | 99.91% |
| A | 5020 | JEMMAL | 299 | 1461 | MONASTIR | 100.00% |
| A | 2086 | DOUAR HICHER | 297 | 1802 | MANNOUBA | 99.28% |
| A | 6010 | METOUIA | 295 | 4 | GABES | 100.00% |
| A | 1001 | TUNIS | 293 | 27 | TUNIS | 100.00% |
| A | 2045 | LAOUINA | 292 | 20 | TUNIS | 100.00% |
| A | 7080 | ML JEMIL | 290 | 5 | BIZERTE | 100.00% |
| A | 1002 | TUNIS BELVEDERE | 288 | 812 | TUNIS | 100.00% |
| A | 3180 | KAIROUAN | 278 | 5 | KAIROUAN | 100.00% |
| A | 8110 | TABARKA | 269 | 750 | JENDOUBA | 100.00% |
| A | 5090 | BEKALTA | 267 | 506 | MONASTIR | 98.81% |
| A | 7032 | TINJA | 265 | 588 | BIZERTE | 100.00% |
| A | 2083 | ARIANA NORD | 261 | 1 | ARIANA | 100.00% |
| A | 7100 | LE KEF | 255 | 349 | KEF | 99.14% |
| A | 1124 | JEDAIDA | 253 | 1102 | MANNOUBA | 99.55% |
| A | 5180 | KSOUR ESSAF | 251 | 1092 | MAHDIA | 99.91% |
| A | 2094 | MNIHLA | 247 | 1348 | ARIANA | 99.85% |
| A | 8040 | BOU ARGOUB | 247 | 1327 | NABEUL | 100.00% |
| A | 5070 | KSAR HELLAL | 235 | 34 | MONASTIR | 97.06% |
| A | 1145 | MOHAMEDIA | 233 | 1 | BEN AROUS | 100.00% |
| A | 4012 | HERGLA | 230 | 356 | SOUSSE | 100.00% |
| A | 2074 | EL MOUROUJ | 228 | 2098 | BEN AROUS | 99.95% |
| A | 3180 | BOUHAJLA | 227 | 23 | KAIROUAN | 100.00% |
| A | 2050 | HAMMAM LIF | 226 | 1414 | BEN AROUS | 99.93% |
| A | 5160 | EL JEM | 226 | 368 | MAHDIA | 100.00% |
| A | 7050 | ML BOURG | 225 | 5 | BIZERTE | 100.00% |
| A | 1140 | FAHS | 225 | 2 | ZAGHOUAN | 100.00% |
| A | 2083 | ARIANA | 224 | 9 | ARIANA | 100.00% |
| A | 2033 | MEGRINE | 218 | 626 | BEN AROUS | 99.84% |
| A | 3110 | SBIKHA | 211 | 240 | KAIROUAN | 99.58% |
| A | 4030 | ENFIDHA | 210 | 369 | SOUSSE | 98.64% |
| A | 2200 | TOZEUR | 207 | 784 | TOZEUR | 100.00% |
| A | 7050 | ML BOURGUIBA | 204 | 5 | BIZERTE | 100.00% |
| A | 6120 | LE KRIB | 201 | 496 | SILIANA | 99.80% |
| A | 7021 | JARZOUNA | 197 | 641 | BIZERTE | 100.00% |
| A | 7010 | SEJNANE | 195 | 603 | BIZERTE | 100.00% |
| A | 6052 | OUEDREF | 194 | 1 | GABES | 100.00% |
| A | 8044 | EL MIDA | 193 | 239 | NABEUL | 100.00% |
| A | 4030 | ENFIDA | 189 | 3 | SOUSSE | 100.00% |
| A | 2076 | LA MARSA | 186 | 200 | TUNIS | 99.00% |
| A | 5012 | SAHLINE | 183 | 254 | MONASTIR | 99.21% |
| A | 7015 | RAFRAF | 180 | 226 | BIZERTE | 100.00% |
| A | 3011 | SAKIET EDDAIER | 178 | 1174 | SFAX | 100.00% |
| A | 8080 | MENZEL TEMIME | 177 | 315 | NABEUL | 100.00% |
| A | 3040 | BIR ALI BEN KHALIFA | 176 | 3 | SFAX | 100.00% |
| A | 1005 | TUNIS | 175 | 3 | TUNIS | 100.00% |
| A | 8090 | KELIBIA | 172 | 1093 | NABEUL | 100.00% |
| A | 2062 | CITE IBN KHALDOUN | 172 | 8 | TUNIS | 100.00% |
| A | 1003 | CITE EL KHADHRA | 169 | 2 | TUNIS | 100.00% |
| A | 8024 | TAZARKA | 167 | 346 | NABEUL | 99.71% |
| A | 8013 | MAAMOURA | 167 | 11 | NABEUL | 100.00% |
| A | 8045 | EL HAOUARIA | 166 | 141 | NABEUL | 99.29% |
| A | 7034 | METLINE | 163 | 232 | BIZERTE | 99.57% |
| A | 2052 | EZZOUHOUR | 162 | 18 | TUNIS | 100.00% |
| A | 2052 | TUNIS | 159 | 14 | TUNIS | 100.00% |
| A | 2015 | LE KRAM | 157 | 415 | TUNIS | 100.00% |
| A | 4180 | HOUMT SOUK | 157 | 29 | MEDENINE | 96.55% |
| A | 1004 | EL MENZAH | 157 | 6 | TUNIS | 100.00% |
| A | 1005 | EL OMRANE | 152 | 352 | TUNIS | 100.00% |
| A | 2090 | BEN AROUS | 152 | 7 | BEN AROUS | 100.00% |
| A | 8140 | FERNANA | 150 | 292 | JENDOUBA | 100.00% |
| A | 3021 | SAKIET EZZIT | 149 | 2109 | SFAX | 99.95% |
| A | 2087 | AGBA | 149 | 1 | TUNIS | 100.00% |
| A | 6140 | MAKTHAR | 147 | 190 | SILIANA | 100.00% |
| A | 8130 | AIN DRAHAM | 146 | 369 | JENDOUBA | 99.73% |
| A | 5022 | MENZEL ENNOUR | 146 | 235 | MONASTIR | 100.00% |
| A | 7114 | JERISSA | 145 | 50 | KEF | 100.00% |
| A | 2090 | MORNAG | 144 | 1063 | BEN AROUS | 99.91% |
| A | 2045 | EL AOUINA | 143 | 43 | TUNIS | 95.35% |
| A | 2045 | L AOUINA | 142 | 2 | TUNIS | 100.00% |
| A | 5130 | CHORBANE | 138 | 170 | MAHDIA | 99.41% |
| A | 2045 | TUNIS | 136 | 4 | TUNIS | 100.00% |
| A | 2073 | BORJ LOUZIR | 133 | 1089 | ARIANA | 99.82% |
| A | 1270 | SBIBA | 133 | 304 | KASSERINE | 99.67% |
| A | 6021 | GHANNOUCHE | 133 | 181 | GABES | 100.00% |
| A | 2052 | ZAHROUNI | 132 | 1 | TUNIS | 100.00% |
| A | 2097 | BOUMHAL | 131 | 20 | BEN AROUS | 95.00% |
| A | 3050 | SFAX | 130 | 3 | SFAX | 100.00% |
| A | 1135 | NAASSEN | 128 | 481 | BEN AROUS | 100.00% |
| A | 7060 | UTIQUE | 126 | 177 | BIZERTE | 100.00% |
| A | 1210 | THALA | 124 | 123 | KASSERINE | 100.00% |
| A | 2010 | DEN DEN | 123 | 1 | TUNIS | 100.00% |
| A | 1160 | ENNADHOUR | 122 | 300 | ZAGHOUAN | 100.00% |
| A | 8023 | SOMAA | 122 | 138 | NABEUL | 99.28% |
| A | 1130 | TEBOURBA | 121 | 540 | MANNOUBA | 98.89% |
| A | 1250 | SBEITLA | 121 | 238 | KASSERINE | 100.00% |
| A | 1002 | SBIBA | 118 | 265 | KASSERINE | 99.62% |
| A | 2000 | TUNIS | 118 | 3 | TUNIS | 100.00% |
| A | 2073 | BORDJ LOUZIR | 118 | 3 | ARIANA | 100.00% |
| A | 2017 | KHAZNADAR | 116 | 731 | TUNIS | 100.00% |
| A | 5010 | OUERDANINE | 116 | 214 | MONASTIR | 100.00% |
| A | 1145 | MOHAMADIA | 113 | 933 | BEN AROUS | 100.00% |
| A | 8160 | GHARDIMAOU | 112 | 414 | JENDOUBA | 100.00% |
| A | 1003 | TUNIS | 108 | 6 | TUNIS | 100.00% |
| A | 1053 | LAC 2 | 106 | 11 | TUNIS | 100.00% |
| A | 4023 | SOUSSE | 103 | 9 | SOUSSE | 100.00% |
| A | 1009 | EL OUARDIA | 103 | 4 | TUNIS | 100.00% |
| A | 3030 | SFAX | 102 | 2 | SFAX | 100.00% |
| A | 2063 | NOUVELLE MEDINA | 101 | 1269 | BEN AROUS | 99.92% |
| A | 3130 | HAFFOUZ | 100 | 155 | KAIROUAN | 99.35% |
| A | 4060 | K KEBIRA | 99 | 5 | SOUSSE | 100.00% |
| A | 2016 | CARTHAGE | 97 | 433 | TUNIS | 99.77% |
| A | 2009 | KSAR SAID | 96 | 460 | TUNIS | 99.78% |
| A | 8020 | SOLIMAN | 93 | 759 | NABEUL | 99.60% |
| A | 2045 | L'AOUINA | 93 | 50 | TUNIS | 98.00% |
| A | 8011 | DAR CHAABANE EL FEHRI | 93 | 9 | NABEUL | 100.00% |
| A | 3050 | SKHIRA | 93 | 4 | SFAX | 100.00% |
| A | 4020 | KONDAR | 92 | 120 | SOUSSE | 100.00% |
| A | 9170 | SIDI BOUZID | 91 | 2 | SIDI BOUZID | 100.00% |
| A | 2056 | RAOUED | 90 | 707 | ARIANA | 100.00% |
| A | 9060 | TESTOUR | 90 | 93 | BEJA | 100.00% |
| A | 4081 | ZAOUIET SOUSSE | 89 | 318 | SOUSSE | 100.00% |
| A | 5021 | BEMBLA | 89 | 246 | MONASTIR | 99.59% |
| A | 4040 | SIDI BOU ALI | 89 | 178 | SOUSSE | 99.44% |
| A | 2036 | ARIANA | 89 | 8 | ARIANA | 100.00% |
| A | 5160 | ELJEM | 89 | 1 | MONASTIR | 100.00% |
| A | 2050 | H LIF | 88 | 2 | BEN AROUS | 100.00% |
| A | 9080 | GOUBELLAT | 87 | 114 | BEJA | 100.00% |
| A | 8056 | BARRAKET ESSAHEL | 86 | 445 | NABEUL | 100.00% |
| A | 3013 | SFAX | 86 | 4 | SFAX | 100.00% |
| A | 2051 | TUNIS | 86 | 2 | TUNIS | 100.00% |
| A | 3000 | AIN CHARFI | 85 | 847 | SFAX | 100.00% |
| A | 5013 | MENZEL KAMEL | 85 | 374 | MONASTIR | 99.73% |
| A | 2096 | BEN AROUS | 85 | 2 | BEN AROUS | 100.00% |
| A | 3020 | SFAX | 84 | 1 | SFAX | 100.00% |
| A | 2074 | MOUROUJ 1 | 83 | 4 | BEN AROUS | 100.00% |
| A | 7033 | GHAR EL MELH | 81 | 189 | BIZERTE | 100.00% |
| A | 5035 | SAYADA | 81 | 141 | MONASTIR | 99.29% |
| A | 8021 | BENI KHALLED | 80 | 340 | NABEUL | 100.00% |
| A | 5115 | EL BRADAA | 80 | 178 | MAHDIA | 100.00% |
| A | 7014 | AOUSJA | 80 | 3 | BIZERTE | 100.00% |
| A | 2011 | DENDEN | 78 | 1126 | MANNOUBA | 98.58% |
| A | 2074 | MOUROUJ 5 | 78 | 2 | BEN AROUS | 100.00% |
| A | 3060 | SFAX | 78 | 2 | SFAX | 100.00% |
| A | 1141 | ZAGHOUAN | 77 | 1 | ZAGHOUAN | 100.00% |
| A | 3034 | GHRAIBA | 76 | 171 | SFAX | 100.00% |
| A | 3120 | OUESLATIA | 76 | 139 | KAIROUAN | 100.00% |
| A | 1095 | SEJOUMI | 76 | 4 | TUNIS | 100.00% |
| A | 6011 | GABES | 75 | 2 | GABES | 100.00% |
| A | 8042 | BIR BOURAGBA | 75 | 1 | NABEUL | 100.00% |
| A | 2060 | LA GOULETTE | 73 | 321 | TUNIS | 100.00% |
| A | 7040 | GHEZALA | 72 | 308 | BIZERTE | 100.00% |
| A | 4011 | H.SOUSSE | 72 | 1 | SOUSSE | 100.00% |
| A | 2054 | KHELIDIA | 71 | 169 | BEN AROUS | 99.41% |
| A | 6032 | TEBELBOU | 71 | 6 | GABES | 100.00% |
| A | 4061 | SOUSSE | 71 | 3 | SOUSSE | 100.00% |
| A | 2037 | ARIANA | 70 | 6 | ARIANA | 100.00% |
| A | 2094 | ARIANA | 70 | 4 | ARIANA | 100.00% |
| A | 3150 | KAIROUAN | 69 | 4 | KAIROUAN | 100.00% |
| A | 6012 | GABES | 69 | 4 | GABES | 100.00% |
| A | 2033 | BEN AROUS | 69 | 1 | BEN AROUS | 100.00% |
| A | 7024 | ZOUAOUINE | 68 | 109 | BIZERTE | 100.00% |
| A | 1008 | TUNIS | 68 | 21 | TUNIS | 100.00% |
| A | 6044 | NVELLE MATMATA | 68 | 1 | GABES | 100.00% |
| A | 1053 | TUNIS | 67 | 3 | TUNIS | 100.00% |
| A | 7080 | MLE JEMILE | 67 | 3 | BIZERTE | 100.00% |
| A | 2020 | SIDI THABET | 66 | 244 | ARIANA | 99.59% |
| A | 3220 | GHOMRASSEN | 66 | 227 | TATAOUINE | 96.04% |
| A | 8010 | MENZEL BOUZELFA | 65 | 233 | NABEUL | 100.00% |
| A | 3160 | HAJEB LAYOUN | 65 | 5 | KAIROUAN | 100.00% |
| A | 8042 | BIR BOUREGBA | 64 | 671 | NABEUL | 100.00% |
| A | 7026 | EL AZIB | 62 | 168 | BIZERTE | 100.00% |
| A | 4021 | SOUSSE | 62 | 8 | SOUSSE | 100.00% |
| A | 2074 | MOUROUJ 4 | 62 | 3 | BEN AROUS | 100.00% |
| A | 1095 | SIDI HESSINE | 62 | 2 | TUNIS | 100.00% |
| A | 6012 | SIDI BOULBABA | 61 | 143 | GABES | 100.00% |
| A | 1145 | BEN AROUS | 61 | 4 | BEN AROUS | 100.00% |
| A | 4011 | SOUSSE | 61 | 2 | SOUSSE | 100.00% |
| A | 7033 | GHAR EL MELEH | 61 | 1 | BIZERTE | 100.00% |
| A | 5014 | BENI HASSEN | 60 | 220 | MONASTIR | 100.00% |
| A | 9014 | ESSLOUGUIA | 60 | 106 | BEJA | 100.00% |
| A | 7021 | ZARZOUNA | 60 | 11 | BIZERTE | 100.00% |
| A | 2062 | TUNIS | 60 | 4 | TUNIS | 100.00% |
| A | 3121 | CHEBIKA | 59 | 122 | KAIROUAN | 100.00% |
| A | 6041 | CHENINI | 59 | 7 | GABES | 100.00% |
| A | 2053 | TUNIS | 59 | 1 | TUNIS | 100.00% |
| A | 6031 | BOUCHEMMA | 58 | 8 | GABES | 100.00% |
| A | 2042 | TUNIS | 58 | 3 | TUNIS | 100.00% |
| A | 2051 | ZAHROUNI | 58 | 3 | TUNIS | 100.00% |
| A | 2081 | ARIANA | 57 | 14 | ARIANA | 100.00% |
| A | 5031 | KSIBET MEDIOUNI | 57 | 11 | MONASTIR | 100.00% |
| A | 2090 | MORNEG | 57 | 7 | BEN AROUS | 100.00% |
| A | 2021 | MANOUBA | 57 | 1 | MANOUBA | 100.00% |
| A | 6114 | KESRA | 56 | 67 | SILIANA | 100.00% |
| A | 4031 | SOUSSE | 56 | 3 | SOUSSE | 100.00% |
| A | 2243 | TOZEUR | 55 | 1 | TOZEUR | 100.00% |
| A | 5034 | CHERAHIL | 52 | 105 | MONASTIR | 99.05% |
| A | 4070 | SOUSSE | 52 | 3 | SOUSSE | 100.00% |
| A | 9150 | SIDI BOUZID | 52 | 1 | SIDI BOUZID | 100.00% |
| A | 9113 | BIR LAHFAY | 52 | 1 | SIDI BOUZID | 100.00% |
| A | 3030 | AGAREB | 51 | 360 | SFAX | 100.00% |
| A | 3041 | SFAX | 51 | 1 | SFAX | 100.00% |
| A | 2092 | EL MANAR 2 | 50 | 524 | TUNIS | 100.00% |
| A | 5023 | TOUZA | 50 | 159 | MONASTIR | 100.00% |
| A | 7020 | JOUMINE | 50 | 102 | BIZERTE | 100.00% |
| A | 9040 | TEBOURSOUK | 49 | 186 | BEJA | 100.00% |
| A | 4025 | SIDI EL HANI | 49 | 3 | SOUSSE | 100.00% |
| A | 4144 | ZARZIS | 49 | 2 | MEDENINE | 100.00% |
| A | 1142 | BORJ EL AMRI | 48 | 369 | MANNOUBA | 100.00% |
| A | 2022 | KALAAT LANDLOUS | 48 | 280 | ARIANA | 100.00% |
| A | 2052 | EZZAHROUNI | 48 | 3 | TUNIS | 100.00% |
| A | 1009 | BELLEVUE | 47 | 379 | TUNIS | 100.00% |
| A | 4023 | CITE RIADH | 47 | 37 | SOUSSE | 100.00% |
| A | 3220 | TATAOUINE | 47 | 3 | TATAOUINE | 100.00% |
| A | 3160 | HAJEB EL AYOUN | 46 | 342 | KAIROUAN | 100.00% |
| A | 6180 | BOU ARADA | 46 | 114 | SILIANA | 100.00% |
| A | 6110 | GAAFOUR | 46 | 83 | SILIANA | 97.59% |
| A | 6070 | MATMATA | 46 | 43 | GABES | 100.00% |
| A | 6113 | BOUROUIS | 46 | 4 | SILIANA | 100.00% |
| A | 8140 | JENDOUBA | 46 | 2 | JENDOUBA | 100.00% |
| A | 3010 | SFAX | 45 | 1 | SFAX | 100.00% |
| A | 6072 | GABES | 45 | 1 | GABES | 100.00% |
| A | 3150 | EL ALA | 44 | 143 | KAIROUAN | 99.30% |
| A | 3042 | SFAX | 44 | 3 | SFAX | 100.00% |
| A | 9070 | MJEZ EL BAB | 43 | 4 | BEJA | 100.00% |
| A | 2046 | TUNIS | 43 | 2 | TUNIS | 100.00% |
| A | 3064 | SFAX | 43 | 2 | SFAX | 100.00% |
| A | 1064 | TUNIS | 43 | 1 | TUNIS | 100.00% |
| A | 1135 | BEN AROUS | 43 | 1 | BEN AROUS | 100.00% |
| A | 2034 | BEN AROUS | 43 | 1 | TUNISIE | 100.00% |
| A | 2051 | SEJOUMI | 43 | 1 | TUNIS | 100.00% |
| A | 2080 | MANOUBA | 42 | 1 | TUNIS | 100.00% |
| A | 6031 | GABES | 42 | 1 | GABES | 100.00% |
| A | 1003 | CITE EL KHADRA | 41 | 761 | TUNIS | 100.00% |
| A | 7025 | SOUNINE | 41 | 57 | BIZERTE | 100.00% |
| A | 5151 | ZORDA | 41 | 48 | MAHDIA | 100.00% |
| A | 2037 | ENNASR 2 | 41 | 6 | ARIANA | 100.00% |
| A | 3130 | KAIROUAN | 41 | 3 | KAIROUAN | 100.00% |
| A | 6044 | NV MATMATA | 41 | 2 | GABES | 100.00% |
| A | 5011 | KHENIS | 40 | 153 | MONASTIR | 100.00% |
| A | 1221 | HAIDRA | 40 | 20 | KASSERINE | 100.00% |
| A | 2045 | AOUINA | 40 | 12 | TUNIS | 100.00% |
| A | 4051 | SOUSSE | 40 | 11 | SOUSSE | 100.00% |
| A | 2010 | AGBA | 40 | 3 | MANNOUBA | 100.00% |
| A | 2245 | NEFTA | 40 | 2 | TOZEUR | 100.00% |
| A | 2041 | DOUAR HICHER | 40 | 1 | LA MANOUBA | 100.00% |
| A | 2066 | IBN SINA | 39 | 596 | TUNIS | 100.00% |
| A | 3120 | KAIROUAN | 39 | 3 | KAIROUAN | 100.00% |
| A | 1000 | ARIANA | 39 | 2 | TUNIS | 100.00% |
| A | 9180 | SIDI BOUZID | 39 | 2 | SIDI BOUZID | 100.00% |
| A | 1095 | SIDI HASSINE | 38 | 3119 | TUNIS | 100.00% |
| A | 7180 | LE SERS | 38 | 115 | KEF | 100.00% |
| A | 2072 | TUNIS | 38 | 4 | TUNIS | 100.00% |
| A | 2054 | BEN AROUS | 38 | 2 | BEN AROUS | 100.00% |
| A | 3052 | SFAX | 38 | 2 | SFAX | 100.00% |
| A | 2051 | SIDI HASSINE | 38 | 1 | TUNIS | 100.00% |
| A | 2010 | MANNOUBA | 38 | 1 | MANNOUBA | 100.00% |
| A | 7170 | DAHMANI | 37 | 119 | KEF | 98.32% |
| A | 3240 | REMADA | 37 | 104 | TATAOUINE | 100.00% |
| A | 4022 | SOUSSE | 37 | 5 | SOUSSE | 100.00% |
| A | 2036 | TUNIS | 37 | 1 | ARIANA | 100.00% |
| A | 2096 | ELYASMINET | 37 | 1 | BEN AROUS | 100.00% |
| A | 6030 | MENZEL LAHBIB | 37 | 1 | GABES | 100.00% |
| A | 1000 | BEN AROUS | 36 | 3 | TUNIS | 100.00% |
| A | 2056 | ARIANA | 36 | 3 | ARIANA | 100.00% |
| A | 2046 | LA SOUKRA | 36 | 2 | TUNIS | 100.00% |
| A | 3012 | SFAX | 36 | 2 | SFAX | 100.00% |
| A | 1002 | ARIANA | 36 | 1 | TUNIS | 100.00% |
| A | 2009 | TUNIS | 36 | 1 | TUNIS | 100.00% |
| A | 1074 | MOUROUJ 2 | 36 | 1 | TUNIS | 100.00% |
| A | 4042 | CHATT MERIEM | 35 | 150 | SOUSSE | 100.00% |
| A | 6072 | ZRIG | 35 | 81 | GABES | 100.00% |
| A | 2083 | CITE EL GHAZELA | 35 | 1 | ARIANA | 100.00% |
| A | 8032 | SIDI JEDIDI | 34 | 188 | NABEUL | 100.00% |
| A | 8115 | OUED MLIZ | 34 | 132 | JENDOUBA | 100.00% |
| A | 4135 | AJIM | 34 | 120 | MEDENINE | 99.17% |
| A | 2042 | ETTAHRIR | 34 | 17 | TUNIS | 100.00% |
| A | 2083 | CITE EL GHAZALA | 34 | 17 | ARIANA | 100.00% |
| A | 8042 | BOUARGOUB | 34 | 9 | NABEUL | 100.00% |
| A | 3110 | KAIROUAN | 34 | 6 | KAIROUAN | 100.00% |
| A | 2082 | BEN AROUS | 34 | 3 | BEN AROUS | 100.00% |
| A | 7100 | KEF | 34 | 3 | KEF | 100.00% |
| A | 2073 | B LOUZIR | 34 | 1 | ARIANA | 100.00% |
| A | 8021 | BNI KHALED | 34 | 1 | NABEUL | 100.00% |
| A | 2036 | DAR FADHAL | 33 | 494 | ARIANA | 99.19% |
| A | 3027 | SFAX | 33 | 2 | SFAX | 100.00% |
| A | 7081 | EL KHETMINE | 33 | 1 | BIZERTE | 100.00% |
| A | 6014 | GABES | 33 | 1 | GABES | 100.00% |
| A | 7130 | KALAAT SINANE | 32 | 75 | KEF | 100.00% |
| A | 2050 | BEN AROUS | 32 | 2 | TUNIS | 100.00% |
| A | 4054 | SOUSSE | 32 | 1 | SOUSSE | 100.00% |
| A | 2046 | GAMMARTH | 32 | 1 | TUNIS | 100.00% |
| A | 3040 | BIR ALI BEN KHELIFA | 31 | 471 | SFAX | 100.00% |
| A | 3083 | SFAX | 31 | 5 | SFAX | 100.00% |
| A | 2045 | LAAOUINA | 31 | 1 | TUNIS | 100.00% |
| A | 2035 | TUNIS CARTHAGE | 31 | 1 | TUNIS | 100.00% |
| A | 4020 | SOUSSE | 31 | 1 | SOUSSE | 100.00% |
| A | 3080 | JEBENIANA | 30 | 302 | SFAX | 100.00% |
| A | 4260 | DOUZ | 30 | 84 | KEBILI | 100.00% |
| A | 2053 | EL KABBARIA | 30 | 17 | TUNIS | 100.00% |
| A | 2092 | TUNIS | 30 | 1 | TUNIS | 100.00% |
| A | 5024 | MOKNINE | 30 | 1 | MONASTIR | 100.00% |
| A | 2010 | LA MANNOUBA | 29 | 4152 | MANNOUBA | 99.88% |
| A | 8170 | BOU SALEM | 29 | 377 | JENDOUBA | 99.73% |
| A | 9180 | OULED HAFFOUZ | 29 | 238 | SIDI BOUZID | 99.58% |
| A | 4114 | ZARZIS | 29 | 2 | MEDENINE | 100.00% |
| A | 1004 | TUNIS | 29 | 1 | TUNIS | 100.00% |
| A | 1095 | SEDJOUMI | 29 | 1 | TUNIS | 100.00% |
| A | 7012 | BAZINA | 28 | 160 | BIZERTE | 100.00% |
| A | 4000 | BOUHSINA | 28 | 52 | SOUSSE | 100.00% |
| A | 4031 | CITE EZZOUHOUR | 28 | 7 | SOUSSE | 100.00% |
| A | 1160 | ZAGHOUAN | 28 | 4 | ZAGHOUAN | 100.00% |
| A | 1110 | ZAGHOUAN | 28 | 1 | ZAGHOUAN | 100.00% |
| A | 2074 | EL MOUROUJ 1 | 27 | 233 | BEN AROUS | 98.71% |
| A | 8013 | EL MAAMOURA | 27 | 132 | NABEUL | 100.00% |
| A | 3170 | NASRALLAH | 27 | 125 | KAIROUAN | 99.20% |
| A | 5010 | OUARDANINE | 27 | 12 | MONASTIR | 100.00% |
| A | 2051 | HRAIRIA | 27 | 2 | TUNIS | 100.00% |
| A | 2041 | CITE 18 JANVIER | 26 | 464 | ARIANA | 100.00% |
| A | 9100 | CITE AGRICOLE | 26 | 45 | SIDI BOUZID | 100.00% |
| A | 7151 | MENZEL SALEM | 26 | 23 | KEF | 100.00% |
| A | 1007 | TUNIS | 26 | 7 | TUNIS | 100.00% |
| A | 5010 | MONASTIR | 26 | 3 | MONASTIR | 100.00% |
| A | 7013 | UTIQUE | 26 | 2 | BIZERTE | 100.00% |
| A | 2070 | TUNIS | 26 | 1 | TUNIS | 100.00% |
| A | 2066 | TUNIS | 26 | 1 | TUNIS | 100.00% |
| A | 3070 | SFAX | 26 | 1 | SFAX | 100.00% |
| A | 3150 | ALAA | 26 | 1 | KAIROUAN | 100.00% |
| A | 5130 | MAHDIA | 26 | 1 | MAHDIA | 100.00% |
| A | 5061 | SIDI AMEUR | 25 | 87 | MONASTIR | 100.00% |
| A | 2046 | AIN ZAGHOUAN | 25 | 35 | TUNIS | 100.00% |
| A | 4070 | MSAKEN EST | 25 | 5 | SOUSSE | 100.00% |
| A | 2110 | GAFSA | 25 | 3 | GAFSA | 100.00% |
| A | 4015 | MSAKEN | 25 | 2 | SOUSSE | 100.00% |
| A | 1095 | SIDI HSINE | 25 | 2 | TUNIS | 100.00% |
| A | 3062 | SFAX | 25 | 2 | SFAX | 100.00% |
| A | 1110 | TUNIS | 25 | 1 | ARIANA | 100.00% |
| A | 2086 | KHALED IBN WALID | 25 | 1 | MANOUBA | 100.00% |
| A | 7040 | GHAZELA | 25 | 1 | BIZERTE | 100.00% |
| A | 4116 | MIDOUN | 24 | 257 | MEDENINE | 99.61% |
| A | 6014 | MTORRECH | 24 | 88 | GABES | 100.00% |
| A | 1220 | FOUSSANA | 24 | 68 | KASSERINE | 100.00% |
| A | 4011 | H SOUSSE | 24 | 2 | SOUSSE | 100.00% |
| A | 2016 | CARTHAGE BYRSA | 24 | 2 | TUNIS | 100.00% |
| A | 2010 | ARIANA | 24 | 1 | ARIANA | 100.00% |
| A | 5199 | EZZAHRA | 24 | 1 | MAHDIA | 100.00% |
| A | 1121 | ZAGHOUAN | 24 | 1 | ZAGHOUAN | 100.00% |
| A | 5120 | MAHDIA | 24 | 1 | MAHDIA | 100.00% |
| A | 2074 | EL MOUROUJ 4 | 23 | 139 | BEN AROUS | 100.00% |
| A | 4041 | KSIBET SOUSSE | 23 | 116 | SOUSSE | 100.00% |
| A | 8031 | TAKELSA | 23 | 84 | NABEUL | 100.00% |
| A | 6001 | GABES HACHED | 23 | 47 | GABES | 100.00% |
| A | 2011 | TUNIS | 23 | 3 | MANNOUBA | 100.00% |
| A | 2022 | ARIANA | 23 | 2 | ARIANA | 100.00% |
| A | 1009 | OUARDIA 1 | 23 | 2 | TUNIS | 100.00% |
| A | 3121 | KAIROUAN | 23 | 2 | KAIROUAN | 100.00% |
| A | 2111 | GAFSA | 23 | 2 | GAFSA | 100.00% |
| A | 1068 | ROMANA | 23 | 1 | TUNIS | 100.00% |
| A | 5140 | MAHDIA | 23 | 1 | MAHDIA | 100.00% |
| A | 9121 | SOUK JEDID | 22 | 417 | SIDI BOUZID | 100.00% |
| A | 1004 | EL MENZAH 1 | 22 | 325 | TUNIS | 99.69% |
| A | 7014 | EL AOUSJA | 22 | 222 | BIZERTE | 100.00% |
| A | 2074 | EL MOUROUJ 3 | 22 | 193 | BEN AROUS | 99.48% |
| A | 5033 | MENZEL HAYET | 22 | 112 | MONASTIR | 100.00% |
| A | 8053 | GARAAT SASSI | 22 | 50 | NABEUL | 100.00% |
| A | 2089 | LE KRAM | 22 | 12 | TUNIS | 100.00% |
| A | 4031 | EZZOUHOUR | 22 | 11 | SOUSSE | 100.00% |
| A | 9110 | SIDI BOUZID | 22 | 8 | SIDI BOUZID | 100.00% |
| A | 1095 | SIJOUMI | 22 | 6 | TUNIS | 100.00% |
| A | 1141 | BIR MCHERGUA | 22 | 6 | ZAGHOUAN | 100.00% |
| A | 8050 | NABEUL | 22 | 4 | NABEUL | 100.00% |
| A | 9113 | SIDI BOUZID | 22 | 4 | SIDI BOUZID | 100.00% |
| A | 8020 | NABEUL | 22 | 3 | NABEUL | 100.00% |
| A | 9120 | SIDI BOUZID | 22 | 2 | SIDI BOUZID | 100.00% |
| A | 1013 | TUNIS | 22 | 1 | TUNIS | 100.00% |
| A | 1046 | J JELOUD | 22 | 1 | TUNIS | 100.00% |
| A | 6010 | GABES | 22 | 1 | GABES | 100.00% |
| A | 2083 | LA PETITE ARIANA | 22 | 1 | LA PETITE AR | 100.00% |
| A | 1100 | ZAGHOUANE | 22 | 1 | ZAGHOUAN | 100.00% |
| A | 4013 | MESSAADINE | 22 | 1 | SOUSSE | 100.00% |
| A | 1000 | EL MEDINA | 21 | 861 | TUNIS | 100.00% |
| A | 2084 | BORJ CEDRIA | 21 | 395 | BEN AROUS | 100.00% |
| A | 4110 | BENI KHEDACHE | 21 | 248 | MEDENINE | 100.00% |
| A | 9122 | CEBBALA | 21 | 204 | SIDI BOUZID | 100.00% |
| A | 2074 | EL MOUROUJ 5 | 21 | 136 | BEN AROUS | 100.00% |
| A | 5024 | MENZEL FERSI | 21 | 106 | MONASTIR | 100.00% |
| A | 4130 | MEDENINE EL JEDIDA | 21 | 87 | MEDENINE | 100.00% |
| A | 2083 | RAOUED | 21 | 10 | ARIANA | 100.00% |
| A | 5020 | JAMMEL | 21 | 9 | MONASTIR | 100.00% |
| A | 2097 | BOUMHEL | 21 | 4 | BEN AROUS | 100.00% |
| A | 2046 | LAOUINA | 21 | 3 | TUNIS | 100.00% |
| A | 2016 | TUNIS | 21 | 1 | TUNIS | 100.00% |
| A | 3000 | KAIROUAN | 21 | 1 | SFAX | 100.00% |
| A | 8100 | JANDOUBA | 21 | 1 | JENDOUBA | 100.00% |
| A | 1013 | EL MENZAH 9 | 20 | 296 | TUNIS | 100.00% |
| A | 2026 | SIDI BOUSAID | 20 | 231 | TUNIS | 99.57% |
| A | 2040 | RADES PLAGE | 20 | 221 | BEN AROUS | 100.00% |
| A | 3116 | CHERARDA | 20 | 98 | KAIROUAN | 98.98% |
| A | 5112 | KERKER | 20 | 91 | MAHDIA | 100.00% |
| A | 4100 | CITE EL KHRACHFA | 20 | 32 | MEDENINE | 100.00% |
| A | 7050 | HENCHIR EL BERNA | 20 | 7 | BIZERTE | 100.00% |
| A | 4030 | SOUSSE | 20 | 5 | SOUSSE | 100.00% |
| A | 3022 | SFAX | 20 | 3 | SFAX | 100.00% |
| A | 8170 | JENDOUBA | 20 | 3 | JENDOUBA | 100.00% |
| A | 1053 | LES JARDINS DE CARTHAGE | 20 | 2 | TUNIS | 100.00% |
| A | 8060 | NABEUL | 20 | 1 | NABEUL | 100.00% |
| A | 5020 | MONASTIR | 20 | 1 | MONASTIR | 100.00% |
| A | 7040 | MATEUR | 20 | 1 | BIZERTE | 100.00% |
| A | 2010 | TUNIS | 20 | 1 | TUNIS | 100.00% |
| A | 4116 | DJERBA | 20 | 1 | DJERBA | 100.00% |
| A | 5190 | SIDI ALOUENE | 19 | 690 | MAHDIA | 100.00% |
| A | 9110 | JILMA | 19 | 312 | SIDI BOUZID | 100.00% |
| A | 4013 | MESSADINE | 19 | 181 | SOUSSE | 100.00% |
| A | 1240 | FERIANA | 19 | 81 | KASSERINE | 100.00% |
| A | 5121 | REJICHE | 19 | 68 | MAHDIA | 100.00% |
| A | 3011 | MERKEZ KAANICHE | 19 | 54 | SFAX | 100.00% |
| A | 5070 | CITE BIR ALI HELLAL | 19 | 34 | MONASTIR | 100.00% |
| A | 4081 | SOUSSE | 19 | 7 | SOUSSE | 100.00% |
| A | 3160 | KAIROUAN | 19 | 6 | KAIROUAN | 100.00% |
| A | 4000 | ZAOUIET SOUSSE | 19 | 5 | SOUSSE | 100.00% |
| A | 1053 | LA MARSA | 19 | 3 | TUNIS | 100.00% |
| A | 2037 | ENNASER 2 | 19 | 3 | ARIANA | 100.00% |
| A | 2062 | IBN KHALDOUN | 19 | 2 | TUNIS | 100.00% |
| A | 1001 | TUNIS REPUBLIQUE | 19 | 1 | TUNIS | 100.00% |
| A | 7040 | GHEZALLA | 19 | 1 | BIZERTE | 100.00% |
| A | 2239 | TOZEUR | 19 | 1 | TOZEUR | 100.00% |
| A | 4100 | BENI KHEDACHE | 19 | 1 | MEDENINE | 100.00% |
| A | 1164 | HAMMAM CHATT | 18 | 365 | BEN AROUS | 100.00% |
| A | 2000 | RAS TABIA | 18 | 115 | TUNIS | 100.00% |
| A | 4071 | KHEZAMA OUEST | 18 | 84 | SOUSSE | 100.00% |
| A | 8033 | DIAR EL HOJJEJ | 18 | 58 | NABEUL | 100.00% |
| A | 2092 | EL MANAR 1 | 18 | 34 | TUNIS | 100.00% |
| A | 6036 | KETTANA | 18 | 34 | GABES | 100.00% |
| A | 6120 | KRIB | 18 | 9 | SILIANA | 100.00% |
| A | 3140 | KAIROUAN | 18 | 7 | KAIROUAN | 100.00% |
| A | 4061 | CITE AEROPORT | 18 | 6 | SOUSSE | 100.00% |
| A | 2017 | TUNIS | 18 | 4 | TUNIS | 100.00% |
| A | 4040 | SIDI BOUALI | 18 | 3 | SOUSSE | 100.00% |
| A | 2074 | MOUROUJ 6 | 18 | 3 | BEN AROUS | 100.00% |
| A | 4042 | CHATT MARIEM | 18 | 3 | SOUSSE | 100.00% |
| A | 2052 | CITE ZOUHOUR | 18 | 1 | TUNIS | 100.00% |
| A | 1002 | MANOUBA | 18 | 1 | TUNIS | 100.00% |
| A | 6013 | EL HAMMA | 18 | 1 | GABES | 100.00% |
| A | 3212 | BIR LAHMAR | 17 | 170 | TATAOUINE | 100.00% |
| A | 5031 | KSIBET EL MEDIOUNI | 17 | 146 | MONASTIR | 100.00% |
| A | 4025 | SIDI EL HENI | 17 | 71 | SOUSSE | 100.00% |
| A | 2046 | AIN ZAGHOUANE | 17 | 9 | TUNIS | 100.00% |
| A | 5111 | HIBOUN | 17 | 6 | MAHDIA | 100.00% |
| A | 7021 | BIZERTE | 17 | 6 | BIZERTE | 100.00% |
| A | 5031 | KSIBET EL MADIOUNI | 17 | 4 | MONASTIR | 100.00% |
| A | 6001 | GABES | 17 | 4 | GABES | 100.00% |
| A | 2076 | TUNIS | 17 | 3 | TUNIS | 100.00% |
| A | 6031 | BOUCHAMMA | 17 | 3 | GABES | 100.00% |
| A | 7000 | MATEUR | 17 | 2 | BIZERTE | 100.00% |
| A | 4021 | KALAA SEGHIRA | 17 | 2 | SOUSSE | 100.00% |
| A | 5070 | KSAR HLEL | 17 | 2 | MONASTIR | 100.00% |
| A | 2014 | BEN AROUS | 17 | 1 | BEN AROUS | 100.00% |
| A | 3100 | KAIRAOUAN | 17 | 1 | KAIRAOUAN | 100.00% |
| A | 1140 | ELFAHS | 17 | 1 | ZAGHOUAN | 100.00% |
| A | 3212 | TATAOUINE | 17 | 1 | TATAOUINE | 100.00% |
| A | 2076 | MARSA | 16 | 1570 | TUNIS | 100.00% |
| A | 1006 | BAB SOUIKA | 16 | 243 | TUNIS | 99.59% |
| A | 2070 | MARSA | 16 | 226 | TUNIS | 100.00% |
| A | 7081 | KHETMINE | 16 | 121 | BIZERTE | 100.00% |
| A | 2033 | SIDI REZIG | 16 | 111 | BEN AROUS | 99.10% |
| A | 7011 | LA PECHERIE | 16 | 100 | BIZERTE | 100.00% |
| A | 4191 | SIDI MAKHLOUF | 16 | 93 | MEDENINE | 100.00% |
| A | 5032 | MAZDOUR | 16 | 46 | MONASTIR | 100.00% |
| A | 2087 | TUNIS | 16 | 7 | TUNIS | 100.00% |
| A | 5015 | BOUHJAR | 16 | 4 | MONASTIR | 100.00% |
| A | 5115 | BRADAA | 16 | 3 | MAHDIA | 100.00% |
| A | 3081 | SFAX | 16 | 3 | SFAX | 100.00% |
| A | 1003 | CITE OLYMPIQUE | 16 | 3 | TUNIS | 100.00% |
| A | 6052 | OUEDHREF | 16 | 3 | GABES | 100.00% |
| A | 4023 | ERRIADH | 16 | 2 | SOUSSE | 100.00% |
| A | 3142 | KAIROUAN | 16 | 2 | KAIROUAN | 100.00% |
| A | 2100 | MOULARES | 16 | 2 | GAFSA | 100.00% |
| A | 2023 | TUNIS | 16 | 1 | TUNIS | 100.00% |
| A | 6080 | ANCIEN BLED | 15 | 313 | GABES | 100.00% |
| A | 2043 | BEN AROUS SUD | 15 | 261 | BEN AROUS | 100.00% |
| A | 2089 | LE KRAM OUEST | 15 | 228 | TUNIS | 100.00% |
| A | 9150 | MEZZOUNA | 15 | 215 | SIDI BOUZID | 100.00% |
| A | 2078 | MARSA | 15 | 104 | TUNIS | 100.00% |
| A | 7113 | KALAA EL KHASBA | 15 | 44 | KEF | 100.00% |
| A | 8015 | MENZEL HORR | 15 | 36 | NABEUL | 100.00% |
| A | 6100 | SELIANA | 15 | 16 | SELIANA | 100.00% |
| A | 1009 | EL OUERDIA 1 | 15 | 15 | TUNIS | 100.00% |
| A | 4000 | BOUHSSINA | 15 | 12 | SOUSSE | 100.00% |
| A | 8000 | BENI KHIAR | 15 | 10 | NABEUL | 100.00% |
| A | 4051 | KHEZAMA EST | 15 | 5 | SOUSSE | 100.00% |
| A | 2170 | MDHILLA | 15 | 4 | GAFSA | 100.00% |
| A | 4173 | ZARZIS | 15 | 3 | MEDENINE | 100.00% |
| A | 2037 | TUNIS | 15 | 2 | TUNIS | 100.00% |
| A | 1091 | OMRANE SUPERIEUR | 15 | 2 | TUNIS | 100.00% |
| A | 2180 | GAFSA | 15 | 2 | GAFSA | 100.00% |
| A | 1009 | MONTFLEURY | 15 | 1 | TUNIS | 100.00% |
| A | 2074 | MOUROUJ4 | 15 | 1 | BEN AROUS | 100.00% |
| A | 3131 | KAIROUAN | 15 | 1 | KAIROUAN | 100.00% |
| A | 1111 | ZAGHOUAN | 15 | 1 | ZAGHOUAN | 100.00% |
| A | 1095 | SIDI HCINE | 15 | 1 | TUNIS | 100.00% |
| A | 8160 | JENDOUBA | 15 | 1 | JENDOUBA | 100.00% |
| A | 2120 | MOULARES | 15 | 1 | GAFSA | 100.00% |
| A | 7080 | MENZEL JEMIL | 14 | 1202 | BIZERTE | 100.00% |
| A | 4121 | KOUTINE | 14 | 93 | MEDENINE | 100.00% |
| A | 4015 | EL BORJINE | 14 | 82 | SOUSSE | 100.00% |
| A | 4070 | MSAKEN OUEST | 14 | 7 | SOUSSE | 100.00% |
| A | 1250 | KASSERINE | 14 | 7 | KASSERINE | 100.00% |
| A | 2080 | ARIANA NORD | 14 | 3 | ARIANA | 100.00% |
| A | 8012 | GROMBALIA | 14 | 3 | NABEUL | 100.00% |
| A | 1145 | EL MOHAMADIA | 14 | 2 | BEN AROUS | 100.00% |
| A | 4274 | KEBILI | 14 | 1 | KEBILI | 100.00% |
| A | 5000 | MAHDIA | 14 | 1 | MAHDIA | 100.00% |
| A | 2082 | FOUCHENA | 14 | 1 | MANNOUBA | 100.00% |
| A | 4175 | JERBA | 14 | 1 | MEDNINE | 100.00% |
| A | 2051 | MELLASSINE | 14 | 1 | EZZAHROUNI | 100.00% |
| A | 1100 | ZRIBA | 14 | 1 | ZAGHOUAN | 100.00% |
| A | 3200 | TATAOUIN | 14 | 1 | TATAOUIN | 100.00% |
| A | 7035 | MENZEL ABDERRAHMEN | 14 | 1 | BIZERTE | 100.00% |
| A | 8000 | JENDOUBA | 14 | 1 | JENDOUBA | 100.00% |
| A | 5034 | MOKNINE | 14 | 1 | MONASTIR | 100.00% |
| A | 9140 | MAKNASSY | 13 | 365 | SIDI BOUZID | 100.00% |
| A | 2036 | CHOTRANA 1 | 13 | 328 | ARIANA | 99.70% |
| A | 3036 | EL AMRA | 13 | 114 | SFAX | 99.12% |
| A | 7041 | LOUATA | 13 | 84 | BIZERTE | 100.00% |
| A | 5044 | SIDI BANNOUR | 13 | 82 | MONASTIR | 100.00% |
| A | 2083 | CITE DE LA RTT 2 | 13 | 76 | ARIANA | 100.00% |
| A | 2078 | CITE AFH | 13 | 26 | TUNIS | 100.00% |
| A | 4071 | KHEZEMA OUEST | 13 | 5 | SOUSSE | 100.00% |
| A | 3060 | BELHOUCHETTE | 13 | 5 | SFAX | 100.00% |
| A | 7050 | BIZERTE | 13 | 4 | BIZERTE | 100.00% |
| A | 7030 | BIZERTE | 13 | 4 | BIZERTE | 100.00% |
| A | 8000 | HAMMAMET | 13 | 2 | NABEUL | 100.00% |
| A | 1008 | MONFLEURY | 13 | 2 | TUNIS | 100.00% |
| A | 2123 | GAFSA | 13 | 2 | GAFSA | 100.00% |
| A | 2083 | JAAFAR | 13 | 1 | ARIANA | 100.00% |
| A | 2083 | CITE EL GAZELLA | 13 | 1 | ARIANA | 100.00% |
| A | 3034 | SFAX | 13 | 1 | SFAX | 100.00% |
| A | 7080 | MEL JEMIL | 13 | 1 | BIZERTE | 100.00% |
| A | 7045 | MENZEL BOURGUIBA | 13 | 1 | BIZERTE | 100.00% |
| A | 7026 | LAAZIB | 13 | 1 | BIZERTE | 100.00% |
| A | 4071 | SOUSSE | 13 | 1 | SOUSSE | 100.00% |
| A | 4124 | ZARZIS | 13 | 1 | MEDENINE | 100.00% |
| A | 2097 | BOU MHEL | 12 | 1304 | BEN AROUS | 100.00% |
| A | 2096 | EL YASMINETTE | 12 | 699 | BEN AROUS | 100.00% |
| A | 2024 | MEGRINE CHAKER | 12 | 274 | BEN AROUS | 100.00% |
| A | 6044 | NOUVELLE MATMATA | 12 | 175 | GABES | 100.00% |
| A | 3010 | EL HENCHA | 12 | 91 | SFAX | 100.00% |
| A | 7112 | TOUIREF | 12 | 41 | KEF | 100.00% |
| A | 2052 | CITE DES OFFICIERS | 12 | 13 | TUNIS | 100.00% |
| A | 2010 | DENDEN | 12 | 4 | MANNOUBA | 100.00% |
| A | 1006 | BAB SAADOUN | 12 | 4 | TUNIS | 100.00% |
| A | 6140 | SILIANA | 12 | 3 | SILIANA | 100.00% |
| A | 4025 | SOUSSE | 12 | 3 | SOUSSE | 100.00% |
| A | 7080 | BIZERTE | 12 | 2 | BIZERTE | 100.00% |
| A | 1270 | KASSERINE | 12 | 2 | KASSERINE | 100.00% |
| A | 5100 | MONASTIR | 12 | 1 | MAHDIA | 100.00% |
| A | 2080 | BEN AROUS | 12 | 1 | ARIANA | 100.00% |
| A | 4115 | JERBA | 12 | 1 | MEDENINE | 100.00% |
| A | 8021 | BENI KHALED | 12 | 1 | NABEUL | 100.00% |
| A | 2070 | GAMMARTH | 12 | 1 | TUNIS | 100.00% |
| A | 4010 | SOUSSE | 12 | 1 | SOUSSE | 100.00% |
| A | 2041 | MANOUBA | 12 | 1 | ARIANA | 100.00% |
| A | 2080 | RAOUED | 12 | 1 | ARIANA | 100.00% |
| A | 1152 | ZRIBA | 12 | 1 | ZAGHOUAN | 100.00% |
| A | 3012 | GREMDA | 12 | 1 | SFAX | 100.00% |
| A | 7010 | BIZERTE | 12 | 1 | BIZERTE | 100.00% |
| A | 8010 | MENZEL BOUZALFA | 12 | 1 | NABEUL | 100.00% |
| A | 4021 | K SGHIRA | 12 | 1 | SOUSSE | 100.00% |
| A | 2074 | MOUROUJ3 | 12 | 1 | BEN AROUS | 100.00% |
| A | 7000 | BEJA | 12 | 1 | BEJA | 100.00% |
| A | 8110 | JENDOUBA | 12 | 1 | JENDOUBA | 100.00% |
| A | 3272 | TATAOUINE | 12 | 1 | TATAOUINE | 100.00% |
| A | 5076 | MNARA | 12 | 1 | MONASTIR | 100.00% |
| A | 1000 | BAB BHAR | 11 | 1983 | TUNIS | 100.00% |
| A | 2223 | HEZOUA | 11 | 181 | TOZEUR | 100.00% |
| A | 4054 | SAHLOUL | 11 | 163 | SOUSSE | 100.00% |
| A | 3070 | KERKENAH | 11 | 140 | SFAX | 100.00% |
| A | 4000 | CITE BOUKHZAR | 11 | 121 | SOUSSE | 100.00% |
| A | 1122 | ZRIBA | 11 | 105 | ZAGHOUAN | 100.00% |
| A | 6026 | ZARAT | 11 | 74 | GABES | 100.00% |
| A | 2180 | EL GUETTAR | 11 | 45 | GAFSA | 100.00% |
| A | 6030 | MENZEL HABIB | 11 | 42 | GABES | 100.00% |
| A | 2045 | AIN ZAGHOUANE | 11 | 8 | TUNIS | 100.00% |
| A | 3240 | TATAOUINE | 11 | 4 | TATAOUINE | 100.00% |
| A | 2042 | CITE ETTADHAMEN | 11 | 3 | ARIANA | 100.00% |
| A | 2083 | NKHILETTE | 11 | 2 | ARIANA | 100.00% |
| A | 9170 | RGUEB | 11 | 2 | SIDI BOUZID | 100.00% |
| A | 2089 | TUNIS | 11 | 1 | TUNIS | 100.00% |
| A | 1004 | ARIANA | 11 | 1 | ARIANA | 100.00% |
| A | 2046 | MARSA | 11 | 1 | TUNIS | 100.00% |
| A | 8010 | NABEUL | 11 | 1 | NABEUL | 100.00% |
| A | 2041 | CITE ETTAHRIR | 11 | 1 | ARIANA | 100.00% |
| A | 1134 | TEBOURBA | 11 | 1 | TEBOURBA | 100.00% |
| A | 7035 | ML ABDERAHMEN | 11 | 1 | BIZERTE | 100.00% |
| A | 8010 | BENI KHALED | 11 | 1 | NABEUL | 100.00% |
| A | 2040 | ARIANA | 11 | 1 | TYNIS | 100.00% |
| A | 2115 | GAFSA | 11 | 1 | GAFSA | 100.00% |
| A | 3140 | SOUASSI | 11 | 1 | MAHDIA | 100.00% |
| A | 9121 | SIDI BOUZID | 11 | 1 | SIDI BOUZID | 100.00% |
| A | 1152 | HAMMAM ZRIBA | 10 | 435 | ZAGHOUAN | 100.00% |
| A | 3042 | EL AIN | 10 | 251 | SFAX | 100.00% |
| A | 6031 | BOU CHEMMA | 10 | 137 | GABES | 100.00% |
| A | 2074 | CITE ALYSSA 1 | 10 | 116 | BEN AROUS | 100.00% |
| A | 5046 | MLICHETTE | 10 | 68 | MONASTIR | 100.00% |
| A | 5146 | RECHERCHA | 10 | 61 | MAHDIA | 100.00% |
| A | 6092 | BECHIMA | 10 | 58 | GABES | 100.00% |
| A | 5099 | LAMTA | 10 | 45 | MONASTIR | 100.00% |
| A | 4021 | KALAA ESGHIRA | 10 | 31 | SOUSSE | 100.00% |
| A | 5040 | CITE EL KODS | 10 | 12 | MONASTIR | 100.00% |
| A | 2113 | METLAOUI GARE | 10 | 11 | GAFSA | 100.00% |
| A | 2066 | CITE IBN SINA | 10 | 3 | TUNIS | 100.00% |
| A | 3263 | TATAOUINE | 10 | 3 | TATAOUINE | 100.00% |
| A | 3051 | SFAX | 10 | 2 | SFAX | 100.00% |
| A | 2036 | SOKRA | 10 | 2 | ARIANA | 100.00% |
| A | 7011 | BIZERTE | 10 | 2 | BIZERTE | 100.00% |
| A | 8000 | CITE SIDI MOUSSA | 10 | 2 | NABEUL | 100.00% |
| A | 5080 | MONASTIR | 10 | 2 | MONASTIR | 100.00% |
| A | 2092 | EL MENZAH 9 | 10 | 1 | TUNIS | 100.00% |
| A | 4042 | CHAT MARIEM | 10 | 1 | SOUSSE | 100.00% |
| A | 2083 | EL GHAZELA | 10 | 1 | ARIANA | 100.00% |
| A | 1064 | CITE INTILAKA | 10 | 1 | TUNIS | 100.00% |
| A | 3023 | SFAX | 10 | 1 | SFAX | 100.00% |
| A | 2041 | ETADHAMEN | 10 | 1 | TUNIS | 100.00% |
| A | 8160 | JANDOUBA | 10 | 1 | JENDOUBA | 100.00% |
| A | 4234 | KEBILI | 10 | 1 | KEBILI | 100.00% |
| A | 5050 | MONASTIR | 10 | 1 | MONASTIR | 100.00% |
| A | 9112 | SIDI BOUZID | 10 | 1 | SIDI BOUZID | 100.00% |
| A | 1074 | EL MOUROUJ 2 | 9 | 317 | TUNIS | 100.00% |
| A | 2055 | BIR EL BEY | 9 | 148 | BEN AROUS | 100.00% |
| A | 8070 | BENI AICHOUN | 9 | 99 | NABEUL | 100.00% |
| A | 9022 | THIBAR | 9 | 65 | BEJA | 100.00% |
| A | 2040 | CHOUCHET RADES | 9 | 53 | BEN AROUS | 100.00% |
| A | 4230 | SOUK EL AHAD | 9 | 41 | KEBILI | 100.00% |
| A | 7016 | CITE INDEPENDANCE | 9 | 33 | BIZERTE | 100.00% |
| A | 5020 | CITE COMMERCIALE 1 | 9 | 25 | MONASTIR | 100.00% |
| A | 2151 | GAFSA AEROPORT | 9 | 20 | GAFSA | 100.00% |
| A | 4170 | BENI FETAIEL | 9 | 20 | MEDENINE | 100.00% |
| A | 4000 | CITE RIADH | 9 | 12 | SOUSSE | 100.00% |
| A | 6010 | CITE EL FANKAR | 9 | 7 | GABES | 100.00% |
| A | 2046 | LES JARDINS DE CARTHAGE | 9 | 3 | TUNIS | 100.00% |
| A | 2045 | LA MARSA | 9 | 3 | TUNIS | 100.00% |
| A | 8025 | TAZARKA | 9 | 3 | NABEUL | 100.00% |
| A | 7029 | BIZERTE | 9 | 3 | BIZERTE | 100.00% |
| A | 1000 | OUERDIA | 9 | 2 | TUNIS | 100.00% |
| A | 1005 | JBAL LAHMER | 9 | 2 | EL OMRANE | 100.00% |
| A | 1006 | BAB MNARA | 9 | 2 | TUNIS | 100.00% |
| A | 3074 | SFAX | 9 | 2 | SFAX | 100.00% |
| A | 2092 | MANAR | 9 | 1 | TUNIS | 100.00% |
| A | 2040 | RADES MONGIL | 9 | 1 | BEN AROUS | 100.00% |
| A | 2032 | ARIANA | 9 | 1 | ARIANA | 100.00% |
| A | 2083 | ENKHILET | 9 | 1 | ARIANA | 100.00% |
| A | 3000 | TUNIS | 9 | 1 | SFAX | 100.00% |
| A | 2042 | CITE TAHRIR | 9 | 1 | TUNIS | 100.00% |
| A | 2037 | MENZAH 8 | 9 | 1 | ARIANA | 100.00% |
| A | 2031 | MANOUBA | 9 | 1 | MANNOUBA | 100.00% |
| A | 3072 | SFAX | 9 | 1 | SFAX | 100.00% |
| A | 7026 | BIZERTE | 9 | 1 | BIZERTE | 100.00% |
| A | 4013 | SOUSSE | 9 | 1 | SOUSSE | 100.00% |
| A | 5113 | MAHDIA | 9 | 1 | MAHDIA | 100.00% |
| A | 5113 | HABIRA | 9 | 1 | MAHDIA | 100.00% |
| A | 5044 | MOKNINE | 9 | 1 | MONASTIR | 100.00% |
| A | 6120 | SILIANA | 9 | 1 | SILIANA | 100.00% |
| A | 2037 | EL MENZAH 7 | 8 | 196 | ARIANA | 100.00% |
| A | 1073 | MONTPLAISIR | 8 | 185 | TUNIS | 100.00% |
| A | 6041 | CHENINI GABES | 8 | 128 | GABES | 100.00% |
| A | 6013 | SOMBAT | 8 | 119 | GABES | 100.00% |
| A | 2080 | NOUVELLE ARIANA | 8 | 105 | ARIANA | 100.00% |
| A | 2014 | MEGRINE RIADH | 8 | 90 | BEN AROUS | 100.00% |
| A | 2051 | CITE BOUGATFA 1 | 8 | 80 | TUNIS | 100.00% |
| A | 8055 | DAR ALLOUCHE | 8 | 51 | NABEUL | 100.00% |
| A | 3263 | TATAOUINE 7 NOVEMBRE | 8 | 48 | TATAOUINE | 100.00% |
| A | 2100 | CITE BAYECH | 8 | 42 | GAFSA | 100.00% |
| A | 5080 | CITE BOU DRISSE | 8 | 33 | MONASTIR | 100.00% |
| A | 4180 | BAZIM | 8 | 29 | MEDENINE | 96.55% |
| A | 1230 | KASSERINE NOUR | 8 | 28 | KASSERINE | 100.00% |
| A | 6095 | CHENCHOU | 8 | 25 | GABES | 100.00% |
| A | 2240 | CITE ERRIADH | 8 | 9 | TOZEUR | 100.00% |
| A | 4023 | CITE ERRIADH | 8 | 7 | SOUSSE | 100.00% |
| A | 5060 | MONASTIR | 8 | 4 | MONASTIR | 100.00% |
| A | 2011 | OUED ELLIL | 8 | 4 | LA MANOUBA | 100.00% |
| A | 5111 | MAHDIA | 8 | 4 | MAHDIA | 100.00% |
| A | 1073 | TUNIS | 8 | 3 | TUNIS | 100.00% |
| A | 1053 | LES BERGES DU LAC 1 | 8 | 3 | TUNIS | 100.00% |
| A | 2011 | MANNOUBA | 8 | 3 | MANNOUBA | 100.00% |
| A | 2034 | CITE 18 JANVIER | 8 | 3 | BEN AROUS | 100.00% |
| A | 2080 | ARIANA SUPERIEUR | 8 | 3 | ARIANA | 100.00% |
| A | 4031 | CITE ZOUHOUR | 8 | 3 | SOUSSE | 100.00% |
| A | 2011 | AMAL | 8 | 2 | MANNOUBA | 100.00% |
| A | 2058 | ARIANA | 8 | 2 | ARIANA | 100.00% |
| A | 2042 | ETTADHAMEN | 8 | 2 | TUNIS | 100.00% |
| A | 2072 | MNIHLA | 8 | 2 | TUNIS | 100.00% |
| A | 2060 | TUNIS | 8 | 2 | TUNIS | 100.00% |
| A | 5061 | MONASTIR | 8 | 1 | MONASTIR | 100.00% |
| A | 1006 | HALFAOUINE | 8 | 1 | TUNIS | 100.00% |
| A | 3067 | SFAX | 8 | 1 | SFAX | 100.00% |
| A | 8030 | BENI KHALLED | 8 | 1 | NABEUL | 100.00% |
| A | 8080 | NABEUL | 8 | 1 | NABEUL | 100.00% |
| A | 3113 | KAIROUAN | 8 | 1 | KAIROUAN | 100.00% |
| A | 9000 | CITE DES MIMOSAS | 8 | 1 | BEJA | 100.00% |
| A | 4061 | KSIBET CHATT | 8 | 1 | SOUSSE | 100.00% |
| A | 4000 | MSAKEN | 8 | 1 | SOUSSE | 100.00% |
| A | 1135 | NAASEN | 8 | 1 | BEN AROUS | 100.00% |
| A | 5031 | KT MEDIOUNI | 8 | 1 | MONASTIR | 100.00% |
| A | 5027 | TYAYRA | 8 | 1 | MONASTIR | 100.00% |
| A | 1091 | EL OMRANE SUPERIEUR | 7 | 458 | TUNIS | 100.00% |
| A | 2046 | CITE AZIZA | 7 | 195 | TUNIS | 100.00% |
| A | 2037 | EL MENZAH 8 | 7 | 158 | ARIANA | 99.37% |
| A | 8025 | HAMMAM EL GHEZAZ | 7 | 123 | NABEUL | 100.00% |
| A | 5025 | BENNANE | 7 | 119 | MONASTIR | 100.00% |
| A | 4155 | GUELLALA | 7 | 109 | MEDENINE | 100.00% |
| A | 8040 | BORJ HAFAIEDH | 7 | 86 | NABEUL | 100.00% |
| A | 5045 | MZAOUGHA | 7 | 77 | MONASTIR | 100.00% |
| A | 1110 | BOU REGBA | 7 | 75 | MANNOUBA | 100.00% |
| A | 4060 | KALAA KEBIRAA | 7 | 73 | SOUSSE | 98.63% |
| A | 5113 | HBIRA | 7 | 60 | MAHDIA | 100.00% |
| A | 8035 | AZMOUR | 7 | 50 | NABEUL | 100.00% |
| A | 5131 | JOUAOUDA | 7 | 47 | MAHDIA | 100.00% |
| A | 5199 | MAHDIA EZZAHRA | 7 | 44 | MAHDIA | 100.00% |
| A | 7120 | ESSAKIA | 7 | 40 | KEF | 100.00% |
| A | 2017 | CITE DES ENSEIGNANTS | 7 | 25 | TUNIS | 100.00% |
| A | 2036 | SIDI SALAH | 7 | 23 | ARIANA | 100.00% |
| A | 4060 | KALAA KBIRA | 7 | 6 | SOUSSE | 100.00% |
| A | 4051 | KHEZEMA | 7 | 5 | SOUSSE | 100.00% |
| A | 2040 | MANOUBA | 7 | 3 | MANOUBA | 100.00% |
| A | 2074 | EL MOUROUJ1 | 7 | 3 | BEN AROUS | 100.00% |
| A | 2036 | LA SOKRA | 7 | 2 | ARIANA | 100.00% |
| A | 4054 | SAHLOUL 2 | 7 | 2 | SOUSSE | 100.00% |
| A | 5190 | MAHDIA | 7 | 2 | MAHDIA | 100.00% |
| A | 2078 | TUNIS | 7 | 2 | TUNIS | 100.00% |
| A | 2036 | BORJ LOUZIR | 7 | 2 | ARIANA | 100.00% |
| A | 3016 | SFAX | 7 | 2 | SFAX | 100.00% |
| A | 4110 | MEDENINE | 7 | 2 | MEDENINE | 100.00% |
| A | 8112 | TABARKA | 7 | 2 | JENDOUBA | 100.00% |
| A | 4040 | SOUSSE | 7 | 2 | SOUSSE | 100.00% |
| A | 2081 | NKHILETTE | 7 | 2 | ARIANA | 100.00% |
| A | 5011 | KHNISS | 7 | 2 | MONASTIR | 100.00% |
| A | 5033 | ZERAMDINE | 7 | 2 | MONASTIR | 100.00% |
| A | 8000 | GROMBALIA | 7 | 1 | NABEUL | 100.00% |
| A | 2054 | KHLIDIA | 7 | 1 | BEN AROUS | 100.00% |
| A | 2042 | CTE ETTAHRIR | 7 | 1 | BARDO | 100.00% |
| A | 1004 | MENZAH 1 | 7 | 1 | TUNIS | 100.00% |
| A | 2086 | LA MANOUBA | 7 | 1 | MANNOUBA | 100.00% |
| A | 2087 | BEN YOUNES | 7 | 1 | TUNIS | 100.00% |
| A | 7000 | SILIANA | 7 | 1 | SILIANA | 100.00% |
| A | 1057 | LA MARSA | 7 | 1 | TUNIS | 100.00% |
| A | 1115 | SAWAF | 7 | 1 | ZAGHOUAN | 100.00% |
| A | 8031 | NABEUL | 7 | 1 | NABEUL | 100.00% |
| A | 1000 | MNIHLA | 7 | 1 | TUNIS | 100.00% |
| A | 8045 | ECHRAF | 7 | 1 | NABEUL | 100.00% |
| A | 3110 | SEBIKHA | 7 | 1 | KAIROUAN | 100.00% |
| A | 1200 | KASSRINE | 7 | 1 | KASSRINE | 100.00% |
| A | 2056 | ARIANA NORD | 7 | 1 | ARIANA | 100.00% |
| A | 2120 | REDAYEF | 7 | 1 | GAFSA | 100.00% |
| A | 2116 | GAFSA | 7 | 1 | GAFSA | 100.00% |
| A | 2121 | GAFSA | 7 | 1 | GAFSA | 100.00% |
| A | 3293 | TATAOUINE | 7 | 1 | TATAOUINE | 100.00% |
| A | 7150 | CITE 2 MARS | 7 | 1 | KEF | 100.00% |
| A | 3078 | SFAX | 7 | 1 | SFAX | 100.00% |
| A | 2045 | CITE EL MHIRI | 6 | 3990 | TUNIS | 100.00% |
| A | 1057 | GAMMART | 6 | 792 | TUNIS | 100.00% |
| A | 4023 | SOUSSE RIADH | 6 | 540 | SOUSSE | 100.00% |
| A | 1095 | BIRINE | 6 | 324 | TUNIS | 100.00% |
| A | 9115 | SAIDA | 6 | 289 | SIDI BOUZID | 100.00% |
| A | 6150 | ROHIA | 6 | 281 | SILIANA | 100.00% |
| A | 1064 | CITE EL INTILAKA | 6 | 270 | TUNIS | 100.00% |
| A | 1141 | BIR MCHERGA | 6 | 262 | ZAGHOUAN | 100.00% |
| A | 2081 | BORJ TOUIL | 6 | 141 | ARIANA | 100.00% |
| A | 1082 | MUTUELLE VILLE | 6 | 136 | TUNIS | 100.00% |
| A | 3253 | DHEHIBA | 6 | 108 | TATAOUINE | 100.00% |
| A | 3223 | SMAR | 6 | 93 | TATAOUINE | 100.00% |
| A | 4014 | EL KNAIES | 6 | 72 | SOUSSE | 100.00% |
| A | 1131 | SMINJA | 6 | 69 | ZAGHOUAN | 100.00% |
| A | 5126 | SALAKTA | 6 | 58 | MAHDIA | 100.00% |
| A | 2025 | SALAMBO | 6 | 55 | TUNIS | 100.00% |
| A | 7033 | BAJOU | 6 | 55 | BIZERTE | 100.00% |
| A | 7160 | EL KSOUR | 6 | 31 | KEF | 100.00% |
| A | 6180 | BOUARAADA | 6 | 28 | SELIANA | 100.00% |
| A | 2120 | CITE DE LA GARE | 6 | 25 | GAFSA | 100.00% |
| A | 5136 | EL GHEDHABNA | 6 | 21 | MAHDIA | 95.24% |
| A | 4000 | HAMMAM SOUSSE | 6 | 14 | SOUSSE | 100.00% |
| A | 8034 | LEBNA | 6 | 12 | NABEUL | 100.00% |
| A | 2089 | KRAM OUEST | 6 | 12 | TUNIS | 100.00% |
| A | 4051 | KHEZAMA | 6 | 11 | SOUSSE | 100.00% |
| A | 5180 | CITE COMMERCIALE | 6 | 11 | MAHDIA | 100.00% |
| A | 5190 | BAAJLA | 6 | 9 | MAHDIA | 100.00% |
| A | 2037 | CITE ENNASR | 6 | 6 | ARIANA | 100.00% |
| A | 1004 | EL MENZAH 4 | 6 | 5 | TUNIS | 100.00% |
| A | 2083 | CITE GHAZELLA | 6 | 5 | ARIANA | 100.00% |
| A | 8045 | ABENE | 6 | 5 | NABEUL | 100.00% |
| A | 6052 | EL MIDA | 6 | 5 | GABES | 100.00% |
| A | 1008 | MONTFLEURY | 6 | 4 | TUNIS | 100.00% |
| A | 2074 | EL MOUROUJ4 | 6 | 4 | BEN AROUS | 100.00% |
| A | 1004 | EL MENZAH 5 | 6 | 3 | TUNIS | 100.00% |
| A | 2017 | BARDO | 6 | 3 | TUNIS | 100.00% |
| A | 4042 | SOUSSE | 6 | 3 | SOUSSE | 100.00% |
| A | 1008 | BAB MNARA | 6 | 3 | TUNIS | 100.00% |
| A | 4033 | MSAKEN | 6 | 3 | SOUSSE | 100.00% |
| A | 4089 | KANTAOUI | 6 | 2 | SOUSSE | 100.00% |
| A | 1004 | EL MENZAH 7 | 6 | 2 | TUNIS | 100.00% |
| A | 8050 | MREZGUA | 6 | 2 | NABEUL | 100.00% |
| A | 2022 | KALAAT LANDALOUS | 6 | 2 | L'ARIANA | 100.00% |
| A | 2022 | KALAAT ANDALOUS | 6 | 2 | ARIANA | 100.00% |
| A | 2010 | EL AGBA | 6 | 2 | MANNOUBA | 100.00% |
| A | 5040 | ZAREMDINE | 6 | 2 | MONASTIR | 100.00% |
| A | 5045 | ZERAMDINE | 6 | 2 | MONASTIR | 100.00% |
| A | 2046 | CARTHAGE | 6 | 1 | TUNIS | 100.00% |
| A | 1075 | TUNIS | 6 | 1 | TUNIS | 100.00% |
| A | 4000 | SOUUSE | 6 | 1 | SOUSSE | 100.00% |
| A | 2082 | TUNIS | 6 | 1 | TUNIS | 100.00% |
| A | 2073 | LA MARSA | 6 | 1 | LA MARSA | 100.00% |
| A | 2045 | AIN ZAGHOUAN NORD | 6 | 1 | TUNIS | 100.00% |
| A | 2045 | SOUKRA | 6 | 1 | TUNIS | 100.00% |
| A | 1000 | SIDI HASSINE | 6 | 1 | TUNIS | 100.00% |
| A | 1057 | TUNIS | 6 | 1 | TUNIS | 100.00% |
| A | 1000 | BAB SAADOUN | 6 | 1 | TUNIS | 100.00% |
| A | 4030 | ENNFIDHA | 6 | 1 | SOUSSE | 100.00% |
| A | 2051 | CITE EZZOUHOUR | 6 | 1 | TUNIS | 100.00% |
| A | 2083 | PETITE ARIANA | 6 | 1 | ARIANA | 100.00% |
| A | 1068 | TUNIS | 6 | 1 | KEF | 100.00% |
| A | 2091 | TUNIS | 6 | 1 | TUNIS | 100.00% |
| A | 8056 | MANARET HAMMAMET | 6 | 1 | NABEUL | 100.00% |
| A | 2032 | SIDI THABET | 6 | 1 | ARIANA | 100.00% |
| A | 3253 | TATAOUINE | 6 | 1 | TATAOUINE | 100.00% |
| A | 7043 | BIZERTE | 6 | 1 | BIZERTE | 100.00% |
| A | 8045 | EL KEDOUA | 6 | 1 | NABEUL | 100.00% |
| A | 3115 | KAIROUAN | 6 | 1 | KAIROUAN | 100.00% |
| A | 8100 | FERNANA | 6 | 1 | JANDOUBA | 100.00% |
| A | 2091 | ARIANA | 6 | 1 | ARIANA | 100.00% |
| A | 4185 | JERBA | 6 | 1 | MEDENINE | 100.00% |
| A | 3252 | TATAOUINE | 6 | 1 | TATAOUINE | 100.00% |
| A | 2021 | CHEBBAOU | 6 | 1 | MANNOUBA | 100.00% |
| A | 5125 | BOUMERDES | 6 | 1 | MAHDIA | 100.00% |
| A | 5014 | BENI HASSAN | 6 | 1 | MONASTIR | 100.00% |
| A | 5042 | MASJED AISSA | 6 | 1 | MONASTIR | 100.00% |
| A | 4131 | MEDENINE | 6 | 1 | MEDENINE | 100.00% |
| A | 3040 | SIDI BOUZID | 6 | 1 | SIDI BOUZID | 100.00% |
| A | 4000 | KAIROUAN | 6 | 1 | SOUSSE | 100.00% |
| A | 9113 | BIR EL HAFFEY | 5 | 598 | SIDI BOUZID | 100.00% |
| A | 2062 | CITE IBN KHALDOUN I | 5 | 514 | TUNIS | 100.00% |
| A | 2052 | EZZOUHOUR 4 | 5 | 377 | TUNIS | 100.00% |
| A | 2087 | CITE EL MECHTEL | 5 | 278 | TUNIS | 100.00% |
| A | 2078 | MARSA SAFSAF | 5 | 257 | TUNIS | 100.00% |
| A | 2023 | SIDI FATHALLAH | 5 | 231 | TUNIS | 100.00% |
| A | 2031 | ESSAIDA | 5 | 138 | MANNOUBA | 100.00% |
| A | 5028 | ZAOUIET KONTECH | 5 | 89 | MONASTIR | 100.00% |
| A | 1200 | DOUGHRA | 5 | 39 | KASSERINE | 100.00% |
| A | 1140 | BIR MOUKRA | 5 | 32 | ZAGHOUAN | 100.00% |
| A | 2050 | CITE 7 NOVEMBRE | 5 | 24 | BEN AROUS | 100.00% |
| A | 6000 | CITE BEN KILANI | 5 | 24 | GABES | 100.00% |
| A | 1002 | EL AYOUN | 5 | 22 | KASSERINE | 100.00% |
| A | 3220 | CITE BAKHTIT | 5 | 18 | TATAOUINE | 100.00% |
| A | 2021 | TUNIS | 5 | 15 | MANNOUBA | 100.00% |
| A | 7032 | AIN FAROUA | 5 | 14 | BIZERTE | 100.00% |
| A | 4054 | SAHLOUL 3 | 5 | 8 | SOUSSE | 100.00% |
| A | 2013 | MHAMDIA | 5 | 8 | BEN AROUS | 100.00% |
| A | 6052 | CITE ENNACIM | 5 | 8 | GABES | 100.00% |
| A | 4054 | SAHLOUL 1 | 5 | 7 | SOUSSE | 100.00% |
| A | 4000 | KHEZAMA | 5 | 6 | SOUSSE | 100.00% |
| A | 4000 | KALAA SOGHRA | 5 | 6 | SOUSSE | 100.00% |
| A | 8062 | NABEUL | 5 | 5 | NABEUL | 100.00% |
| A | 2098 | RADES | 5 | 5 | BEN AROUS | 100.00% |
| A | 4089 | HAMMAM SOUSSE | 5 | 4 | SOUSSE | 100.00% |
| A | 1002 | LAFAYETTE | 5 | 4 | TUNIS | 100.00% |
| A | 8056 | HAMMAMET | 5 | 4 | NABEUL | 100.00% |
| A | 4000 | SIDI ABDELHAMID | 5 | 4 | SOUSSE | 100.00% |
| A | 3160 | HAJEB LAAYOUN | 5 | 4 | KAIROUAN | 100.00% |
| A | 7150 | KEF | 5 | 4 | KEF | 100.00% |
| A | 1006 | BAB EL KHADHRA | 5 | 4 | TUNIS | 100.00% |
| A | 3054 | SAKIET EDDAIER | 5 | 3 | SFAX | 100.00% |
| A | 2016 | LE KRAM | 5 | 3 | TUNIS | 100.00% |
| A | 8045 | SIDI MADHKOUR | 5 | 3 | NABEUL | 100.00% |
| A | 4061 | SIDI ABDELHAMID | 5 | 3 | SOUSSE | 100.00% |
| A | 1220 | KASSERINE | 5 | 3 | KASSERINE | 100.00% |
| A | 5014 | BNI HASSEN | 5 | 3 | MONASTIR | 100.00% |
| A | 8011 | DAR CHAABNE | 5 | 3 | NABEUL | 100.00% |
| A | 1000 | SIJOUMI | 5 | 2 | TUNIS | 100.00% |
| A | 5070 | MONASTIR | 5 | 2 | MONASTIR | 100.00% |
| A | 2087 | HRAIRIA | 5 | 2 | TUNIS | 100.00% |
| A | 3021 | SAKIET EDDAIER | 5 | 2 | SFAX | 100.00% |
| A | 3000 | AGAREB | 5 | 2 | SFAX | 100.00% |
| A | 5170 | MAHDIA | 5 | 2 | MAHDIA | 100.00% |
| A | 9131 | SIDI BOUZID | 5 | 2 | SIDI BOUZID | 100.00% |
| A | 6100 | BOU ARADA | 5 | 2 | SILIANA | 100.00% |
| A | 4081 | ZAOUIT SOUSSE | 5 | 2 | SOUSSE | 100.00% |
| A | 3000 | SOUSSE | 5 | 1 | SOUSSE | 100.00% |
| A | 3200 | TATOUINE | 5 | 1 | TUNISIE | 100.00% |
| A | 2037 | ENNASR2 | 5 | 1 | ARIANA | 100.00% |
| A | 2013 | MOUROUJ 5 | 5 | 1 | BEN AROUS | 100.00% |
| A | 2037 | MENZEH 7 | 5 | 1 | ARIANA | 100.00% |
| A | 1000 | OMRANE | 5 | 1 | TUNIS | 100.00% |
| A | 2050 | HAMMAM CHATT | 5 | 1 | BEN AROUS | 100.00% |
| A | 2021 | MANNOUBA | 5 | 1 | MANNOUBA | 100.00% |
| A | 1013 | EL MENZAH 9A | 5 | 1 | TUNIS | 100.00% |
| A | 2089 | EL KRAM | 5 | 1 | TUNIS | 100.00% |
| A | 1124 | JDAIDA | 5 | 1 | MANNOUBA | 100.00% |
| A | 2010 | LE BARDO | 5 | 1 | TUNIS | 100.00% |
| A | 2031 | SAIDA | 5 | 1 | MANNOUBA | 100.00% |
| A | 2025 | CARTHAGE | 5 | 1 | TUNIS | 100.00% |
| A | 8044 | MIDA | 5 | 1 | NABEUL | 100.00% |
| A | 1100 | SAOUAF | 5 | 1 | ZAGHOUANE | 100.00% |
| A | 2097 | BOUMHAL BASSATINE | 5 | 1 | BEN AROUS | 100.00% |
| A | 3000 | MENZEL CHAKER | 5 | 1 | SFAX | 100.00% |
| A | 3000 | CHIHIA | 5 | 1 | SFAX | 100.00% |
| A | 7000 | TINJA | 5 | 1 | BIZERTE | 100.00% |
| A | 7080 | M EL JEMIL | 5 | 1 | BIZERTE | 100.00% |
| A | 8045 | MENZEL SALEM | 5 | 1 | NABEUL | 100.00% |
| A | 8080 | GROMBALIA | 5 | 1 | NABEUL | 100.00% |
| A | 8052 | GROMBALIA | 5 | 1 | NABEUL | 100.00% |
| A | 8030 | GRAMBALIA | 5 | 1 | TUNIS | 100.00% |
| A | 3100 | SBIKHA | 5 | 1 | KAIROUAN | 100.00% |
| A | 3124 | OUESLATIA | 5 | 1 | KAIROUAN | 100.00% |
| A | 2080 | ETTADHAMEN | 5 | 1 | TUNIS | 100.00% |
| A | 2080 | BORDJ LOZIR | 5 | 1 | ARIANA | 100.00% |
| A | 4000 | KSIBET SOUSSE | 5 | 1 | SOUSSE | 100.00% |
| A | 2212 | TOZEUR | 5 | 1 | TOZEUR | 100.00% |
| A | 2139 | GAFSA | 5 | 1 | GAFSA | 100.00% |
| A | 1000 | JEBAL LAHMAR | 5 | 1 | TUNIS | 100.00% |
| A | 5025 | BANEN | 5 | 1 | MONASTIR | 100.00% |
| A | 5028 | JAMMEL | 5 | 1 | MOUNASTIR | 100.00% |
| A | 2015 | LE KRAM OUEST | 5 | 1 | TUNIS | 100.00% |
| A | 1000 | SILIANA | 5 | 1 | TUNIS | 100.00% |
| A | 2051 | AGBA | 5 | 1 | TUNIS | 100.00% |
| A | 9000 | SIDI BOUZID | 5 | 1 | SIDI BOUZID | 100.00% |
| A | 8042 | NABEUL | 5 | 1 | NABEUL | 100.00% |
| A | 8090 | KLIBIA | 5 | 1 | NABEUL | 100.00% |
| A | 5046 | ZERAMDINE | 5 | 1 | MONASTIR | 100.00% |
| A | 9114 | MENZEL BOUZAIENE | 4 | 205 | SIDI BOUZID | 100.00% |
| A | 9120 | BEN OUN | 4 | 186 | SIDI BOUZID | 100.00% |
| A | 6113 | BOU ROUIS | 4 | 120 | SILIANA | 100.00% |
| A | 1155 | BIR HALIMA | 4 | 116 | ZAGHOUAN | 100.00% |
| A | 1009 | DIBOUZVILLE | 4 | 91 | TUNIS | 100.00% |
| A | 4131 | HASSI AMOR | 4 | 79 | MEDENINE | 100.00% |
| A | 2081 | ARIANA ESSOUGHRA | 4 | 77 | ARIANA | 100.00% |
| A | 2035 | CHARGUIA 2 | 4 | 75 | ARIANA | 100.00% |
| A | 9070 | ARGOUB EZZAATAR | 4 | 71 | BEJA | 100.00% |
| A | 4033 | MOUREDDINE | 4 | 68 | SOUSSE | 100.00% |
| A | 5111 | MAHDIA HIBOUN | 4 | 61 | MAHDIA | 100.00% |
| A | 2074 | EL MOUROUJ 6 | 4 | 48 | BEN AROUS | 100.00% |
| A | 4026 | KROUSSIA | 4 | 43 | SOUSSE | 100.00% |
| A | 2115 | BELKHIR | 4 | 40 | GAFSA | 100.00% |
| A | 5012 | MOOTMAR | 4 | 39 | MONASTIR | 100.00% |
| A | 7031 | TAMRA | 4 | 38 | BIZERTE | 100.00% |
| A | 2020 | BEJAOUA 2 | 4 | 37 | ARIANA | 100.00% |
| A | 2092 | CITE DES MEDECINS | 4 | 32 | TUNIS | 100.00% |
| A | 3026 | HAZEG | 4 | 28 | SFAX | 100.00% |
| A | 8041 | KORBOUS | 4 | 26 | NABEUL | 100.00% |
| A | 2121 | LALA | 4 | 16 | GAFSA | 100.00% |
| A | 6112 | KRIB GARE | 4 | 15 | SILIANA | 100.00% |
| A | 7113 | CITE EL MELLESSINE | 4 | 13 | KEF | 100.00% |
| A | 1131 | SMENJA | 4 | 12 | ZAGHOUAN | 100.00% |
| A | 5100 | CITE AFH | 4 | 12 | MAHDIA | 100.00% |
| A | 3132 | SISSEB | 4 | 8 | KAIROUAN | 100.00% |
| A | 8080 | DAMOUS | 4 | 8 | NABEUL | 100.00% |
| A | 3080 | JIBINIANA | 4 | 7 | SFAX | 100.00% |
| A | 5050 | CITE 7 NOVEMBRE | 4 | 7 | MONASTIR | 100.00% |
| A | 1009 | EL OUERDIA 6 | 4 | 6 | TUNIS | 100.00% |
| A | 8080 | SIDI JAMELEDDINE | 4 | 6 | NABEUL | 100.00% |
| A | 2046 | AOUINA | 4 | 5 | TUNIS | 100.00% |
| A | 8024 | CITE SIDI AMOR | 4 | 5 | NABEUL | 100.00% |
| A | 2074 | EL MOUROUJ5 | 4 | 5 | BEN AROUS | 100.00% |
| A | 1009 | EL OUERDIA 4 | 4 | 5 | TUNIS | 100.00% |
| A | 4031 | EZOUHOUR | 4 | 4 | SOUSSE | 100.00% |
| A | 6113 | SIDI BOUROUIS | 4 | 4 | SILIANA | 100.00% |
| A | 2062 | EL OMRANE SUPERIEUR | 4 | 3 | TUNIS | 100.00% |
| A | 1155 | BIR HLIMA | 4 | 3 | ZAGHOUAN | 100.00% |
| A | 5022 | MONASTIR | 4 | 3 | MONASTIR | 100.00% |
| A | 8042 | HAMMAMET | 4 | 2 | NABEUL | 100.00% |
| A | 8020 | SLIMANE | 4 | 2 | NABEUL | 100.00% |
| A | 2011 | ELAGBA | 4 | 2 | MANNOUBA | 100.00% |
| A | 7024 | BIZERTE | 4 | 2 | BIZERTE | 100.00% |
| A | 2021 | CITE DHAMENE 2 | 4 | 2 | MANNOUBA | 100.00% |
| A | 2054 | MORNAG | 4 | 2 | BEN AROUS | 100.00% |
| A | 1155 | ZAGHOUAN | 4 | 2 | ZAGHOUAN | 100.00% |
| A | 3100 | BOUHAJLA | 4 | 2 | KAIROUAN | 100.00% |
| A | 3100 | OUESLATIA | 4 | 2 | KAIROUAN | 100.00% |
| A | 1007 | TUNIS JEBBARI | 4 | 1 | TUNIS | 100.00% |
| A | 1004 | EL MENZAH 9 | 4 | 1 | TUNIS | 100.00% |
| A | 2094 | EL MNIHLA | 4 | 1 | MANNOUBA | 100.00% |
| A | 2037 | CITE ENNASER 2 | 4 | 1 | ARIANA | 100.00% |
| A | 3111 | KAIROUAN | 4 | 1 | KAIROUAN | 100.00% |
| A | 2037 | CITE ENNASER | 4 | 1 | ARIANA | 100.00% |
| A | 2080 | AIN ZAGHOUAN | 4 | 1 | TUNIS | 100.00% |
| A | 2080 | ARIANA ECOLE | 4 | 1 | ARIANA | 100.00% |
| A | 1091 | EL OMRANE SUP | 4 | 1 | TUNIS | 100.00% |
| A | 2085 | CARTHAGE | 4 | 1 | TUNIS | 100.00% |
| A | 2051 | EZZOUHOUR | 4 | 1 | TUNIS | 100.00% |
| A | 2058 | RIADH EL ANDALOUS | 4 | 1 | ARIANA | 100.00% |
| A | 2016 | CARTHAGE BIRSA | 4 | 1 | TUNIS | 100.00% |
| A | 1074 | BEN AROUS | 4 | 1 | TUNIS | 100.00% |
| A | 1000 | MANAR | 4 | 1 | TUNIS | 100.00% |
| A | 2072 | CITE INTILAKA | 4 | 1 | TUNIS | 100.00% |
| A | 1111 | BIR MCHERGUA | 4 | 1 | ZAGHOUAN | 100.00% |
| A | 1142 | BORJ ELAMRI | 4 | 1 | MANNOUBA | 100.00% |
| A | 2011 | LA MANOUBA | 4 | 1 | MANNOUBA | 100.00% |
| A | 3010 | HENCHA | 4 | 1 | SFAX | 100.00% |
| A | 7000 | TUNIS | 4 | 1 | TUNIS | 100.00% |
| A | 8000 | DAR CHAABANE | 4 | 1 | NABEUL | 100.00% |
| A | 2037 | BORJ LOUZIR | 4 | 1 | ARIANA | 100.00% |
| A | 4021 | KALAA SEGHAIRA | 4 | 1 | SOUSSE | 100.00% |
| A | 9021 | BEJA | 4 | 1 | BEJA | 100.00% |
| A | 1000 | BEJA | 4 | 1 | TUNIS | 100.00% |
| A | 2056 | RAOUED PLAGE | 4 | 1 | ARIANA | 100.00% |
| A | 2050 | BOUMHAL | 4 | 1 | BEN AROUS | 100.00% |
| A | 4034 | ENFIDHA | 4 | 1 | SOUSSE | 100.00% |
| A | 2260 | TOZEUR | 4 | 1 | TOZEUR | 100.00% |
| A | 7035 | BIZERTE | 4 | 1 | BIZERTE | 100.00% |
| A | 4280 | KEBILI | 4 | 1 | KEBILI | 100.00% |
| A | 6030 | WALI | 4 | 1 | GABES | 100.00% |
| A | 6044 | MATMATA | 4 | 1 | GABES | 100.00% |
| A | 7130 | LE KEF | 4 | 1 | KEF | 100.00% |
| A | 7180 | SERES | 4 | 1 | KEF | 100.00% |
| A | 5011 | MONASTIR | 4 | 1 | MONASTIR | 100.00% |
| A | 5040 | ZERMADINE | 4 | 1 | MONASTIR | 100.00% |
| A | 2015 | LA GOULETTE | 4 | 1 | TUNIS | 100.00% |
| A | 6100 | BARGOU | 4 | 1 | SILIANA | 100.00% |
| A | 1009 | OUARDIA 4 | 4 | 1 | TUNIS | 100.00% |
| A | 6131 | KESRA | 4 | 1 | SILIANA | 100.00% |
| A | 1005 | EL OMRAN | 4 | 1 | TUNIS | 100.00% |
| A | 2026 | CARTHAGE BYRSA | 4 | 1 | TUNIS | 100.00% |
| A | 7035 | M EL ABDERRAHMEN | 4 | 1 | BIZERTE | 100.00% |
| A | 4133 | JERBA | 4 | 1 | MEDENINE | 100.00% |
| A | 2081 | TUNIS | 4 | 1 | TUNIS | 100.00% |
| A | 2087 | EL HRAIRIA | 3 | 1051 | TUNIS | 99.90% |
| A | 2046 | SIDI DAOUD | 3 | 684 | TUNIS | 100.00% |
| A | 4021 | KALAA ESSGHIRA | 3 | 498 | SOUSSE | 100.00% |
| A | 4010 | BOU FICHA | 3 | 410 | SOUSSE | 100.00% |
| A | 2072 | CITE HELAL | 3 | 246 | TUNIS | 100.00% |
| A | 6032 | TEBOULBOU | 3 | 138 | GABES | 100.00% |
| A | 1089 | MONFLEURY | 3 | 100 | TUNIS | 100.00% |
| A | 2130 | CITE MZERAA | 3 | 87 | GAFSA | 100.00% |
| A | 4015 | BENI RABIA | 3 | 82 | SOUSSE | 100.00% |
| A | 4175 | EL MAY | 3 | 81 | MEDENINE | 100.00% |
| A | 3012 | MERKEZ SAHNOUN | 3 | 78 | SFAX | 100.00% |
| A | 2009 | BORTAL HAYDER | 3 | 76 | TUNIS | 100.00% |
| A | 2042 | CITE DU JARDIN | 3 | 71 | TUNIS | 100.00% |
| A | 7100 | BARNOUSSA | 3 | 69 | KEF | 98.55% |
| A | 7013 | AIN GHELAL | 3 | 60 | BIZERTE | 100.00% |
| A | 8050 | CHAABET EL MREZGA | 3 | 58 | NABEUL | 100.00% |
| A | 5000 | SKANES | 3 | 58 | MONASTIR | 100.00% |
| A | 3100 | CITE EL MOEZ | 3 | 49 | KAIROUAN | 97.96% |
| A | 4146 | ERRIADH | 3 | 47 | MEDENINE | 100.00% |
| A | 1134 | CHAOUAT | 3 | 44 | MANNOUBA | 100.00% |
| A | 2023 | CITE THAMEUR | 3 | 43 | TUNIS | 100.00% |
| A | 2130 | CITE MAGROUN | 3 | 41 | GAFSA | 100.00% |
| A | 2036 | CHOTRANA 3 | 3 | 37 | ARIANA | 97.30% |
| A | 8020 | CITE GHARNATA | 3 | 37 | NABEUL | 100.00% |
| A | 1145 | CITE BOU AKROUCHA | 3 | 35 | BEN AROUS | 100.00% |
| A | 5116 | SIDI ASSAKER | 3 | 33 | MAHDIA | 100.00% |
| A | 7010 | CITE AIR NOUVELLE | 3 | 32 | BIZERTE | 100.00% |
| A | 2046 | AIN ZAGHOUEN | 3 | 31 | TUNIS | 100.00% |
| A | 4231 | BECHRI | 3 | 29 | KEBILI | 100.00% |
| A | 7036 | TESKRAYA | 3 | 26 | BIZERTE | 100.00% |
| A | 4264 | EL FAOUAR | 3 | 25 | KEBILI | 100.00% |
| A | 6051 | NAHAL | 3 | 25 | GABES | 100.00% |
| A | 3083 | CITE BADRANI | 3 | 24 | SFAX | 100.00% |
| A | 1210 | CHAFAI | 3 | 22 | KASSERINE | 100.00% |
| A | 5141 | CHIBA | 3 | 22 | MAHDIA | 100.00% |
| A | 4061 | SOUSSE IBN KHALDOUN | 3 | 19 | SOUSSE | 100.00% |
| A | 4060 | AHEL JEMIAA | 3 | 19 | SOUSSE | 100.00% |
| A | 8031 | BIR MROUA | 3 | 18 | NABEUL | 100.00% |
| A | 9010 | BENI SAID | 3 | 17 | BEJA | 100.00% |
| A | 2032 | EL NAHLI | 3 | 14 | ARIANA | 100.00% |
| A | 7035 | CITE BIR HMEM | 3 | 13 | BIZERTE | 100.00% |
| A | 5113 | AGBA | 3 | 10 | MAHDIA | 100.00% |
| A | 1250 | CITE DES ENSEIGNANTS | 3 | 9 | KASSERINE | 100.00% |
| A | 4051 | KHEZAMA OUEST | 3 | 8 | SOUSSE | 100.00% |
| A | 4042 | AKOUDA | 3 | 7 | SOUSSE | 100.00% |
| A | 9110 | AIN JAFFEL | 3 | 7 | SIDI BOUZID | 100.00% |
| A | 1082 | CENTRE URBAIN NORD | 3 | 6 | TUNIS | 100.00% |
| A | 3140 | CITE DAR EL AMEN | 3 | 6 | KAIROUAN | 100.00% |
| A | 5000 | ZAOUIET KONTECH | 3 | 6 | MONASTIR | 100.00% |
| A | 4030 | CITE 7 NOVEMBRE | 3 | 5 | SOUSSE | 100.00% |
| A | 4000 | SAHLOUL | 3 | 5 | SOUSSE | 100.00% |
| A | 2090 | BORJ ESSOUFI | 3 | 5 | BEN AROUS | 100.00% |
| A | 1053 | LAC | 3 | 4 | TUNIS | 100.00% |
| A | 8030 | GROMBELIA | 3 | 4 | NABEUL | 100.00% |
| A | 4030 | NFIDHA | 3 | 4 | SOUSSE | 100.00% |
| A | 1029 | BAB SAADOUN GARE | 3 | 4 | TUNIS | 100.00% |
| A | 4021 | KALAA SOGHRA | 3 | 4 | SOUSSE | 100.00% |
| A | 1089 | MONTFLEURY | 3 | 3 | TUNIS | 100.00% |
| A | 2080 | EL MENZAH 5 | 3 | 3 | ARIANA | 100.00% |
| A | 2086 | TUNIS | 3 | 3 | TUNIS | 100.00% |
| A | 2260 | CITE DE LA GARE | 3 | 3 | TOZEUR | 100.00% |
| A | 5122 | MAHDIA | 3 | 3 | MAHDIA | 100.00% |
| A | 2016 | CARTHAGE HANNIBAL | 3 | 2 | TUNIS | 100.00% |
| A | 4054 | SAHLOUL2 | 3 | 2 | SOUSSE | 100.00% |
| A | 4025 | CITE RIADH | 3 | 2 | SOUSSE | 100.00% |
| A | 1000 | GAFSA | 3 | 2 | TUNIS | 100.00% |
| A | 4030 | KONDAR | 3 | 2 | SOUSSE | 100.00% |
| A | 4000 | KALAA KEBIRA | 3 | 2 | SOUSSE | 100.00% |
| A | 5010 | CITE 22 JANVIER | 3 | 2 | MONASTIR | 100.00% |
| A | 1009 | MONFLEURY | 3 | 2 | TUNIS | 100.00% |
| A | 3200 | TUNIS | 3 | 2 | TATAOUINE | 100.00% |
| A | 2035 | ARIANA | 3 | 2 | ARIANA | 100.00% |
| A | 7000 | MENZEL BOURGUIBA | 3 | 2 | BIZERTE | 100.00% |
| A | 5000 | BEMBLA | 3 | 2 | MONASTIR | 100.00% |
| A | 2028 | MORNAGUIA | 3 | 2 | MANNOUBA | 100.00% |
| A | 2026 | CARTHAGE | 3 | 1 | TUNIS | 100.00% |
| A | 9123 | SIDI BOUZID | 3 | 1 | SIDI BOUZID | 100.00% |
| A | 2080 | L'AOUINA | 3 | 1 | ARIANA | 100.00% |
| A | 7000 | BHIRA | 3 | 1 | BIZERTE | 100.00% |
| A | 2000 | BIZERTE | 3 | 1 | TUNIS | 100.00% |
| A | 5021 | MNARA | 3 | 1 | MONASTIR | 100.00% |
| A | 2013 | BOUMHAL | 3 | 1 | BEN AROUS | 100.00% |
| A | 2064 | MORNAG | 3 | 1 | BEN AROUS | 100.00% |
| A | 1000 | SAIDA | 3 | 1 | TUNIS | 100.00% |
| A | 2078 | SIDI DAOUED | 3 | 1 | LA MARSA | 100.00% |
| A | 6100 | KRIB | 3 | 1 | SILIANA | 100.00% |
| A | 2066 | AVICENNE | 3 | 1 | TUNIS | 100.00% |
| A | 1009 | FATHALLAH | 3 | 1 | TUNIS | 100.00% |
| A | 2012 | TUNIS | 3 | 1 | TUNIS | 100.00% |
| A | 8044 | NABEUL | 3 | 1 | NABEUL | 100.00% |
| A | 1000 | ZAHROUNI | 3 | 1 | TUNIS | 100.00% |
| A | 2070 | MARSA OUEST | 3 | 1 | TUNIS | 100.00% |
| A | 2034 | TUNIS | 3 | 1 | BEN AROUS | 100.00% |
| A | 4179 | HOUMT SOUK | 3 | 1 | MEDENINE | 100.00% |
| A | 2056 | TUNIS | 3 | 1 | TUNIS | 100.00% |
| A | 1140 | FAHES | 3 | 1 | KAIROUAN | 100.00% |
| A | 2022 | KALLAT ANDALOUS | 3 | 1 | ARIANA | 100.00% |
| A | 1100 | BIR MCHERGA | 3 | 1 | ZAGHOUAN | 100.00% |
| A | 3000 | MAHRES | 3 | 1 | SFAX | 100.00% |
| A | 3000 | SFAX VILLE | 3 | 1 | SFAX | 100.00% |
| A | 7093 | BIZERTE | 3 | 1 | BIZERTE | 100.00% |
| A | 3021 | AIN CHARFI | 3 | 1 | SFAX | 100.00% |
| A | 5036 | MENZEL HAREB | 3 | 1 | MONASTIR | 100.00% |
| A | 7000 | SEJNANE | 3 | 1 | BIZERTE | 100.00% |
| A | 7034 | BIZERTE | 3 | 1 | BIZERTE | 100.00% |
| A | 8045 | BENI KHERA | 3 | 1 | NABEUL | 100.00% |
| A | 3113 | AIN JLOULA | 3 | 1 | KAIROUAN | 100.00% |
| A | 3143 | KAIROUAN | 3 | 1 | KAIROUAN | 100.00% |
| A | 3132 | SBIKHA | 3 | 1 | KAIROUAN | 100.00% |
| A | 2054 | NAASSEN | 3 | 1 | BEN AROUS | 100.00% |
| A | 7063 | BIZERTE | 3 | 1 | BIZERTE | 100.00% |
| A | 2055 | BIR BEY | 3 | 1 | BEN AROUS | 100.00% |
| A | 9080 | GOUBELAT | 3 | 1 | BEJA | 100.00% |
| A | 9022 | BEJA | 3 | 1 | BEJA | 100.00% |
| A | 1210 | KASSERINE | 3 | 1 | KASSERINE | 100.00% |
| A | 4021 | KALAA KEBIRA | 3 | 1 | SOUSSE | 100.00% |
| A | 4013 | MSAKEN | 3 | 1 | SOUSSE | 100.00% |
| A | 4060 | K KOBRA | 3 | 1 | SOUSSE | 100.00% |
| A | 2140 | REDEYEF | 3 | 1 | GAFSA | 100.00% |
| A | 6044 | NV MATMATTA | 3 | 1 | GABES | 100.00% |
| A | 6044 | MATMATA NOUVELLE | 3 | 1 | GABES | 100.00% |
| A | 3211 | TATAOUINE | 3 | 1 | TATAOUINE | 100.00% |
| A | 7113 | KEF | 3 | 1 | KEF | 100.00% |
| A | 2036 | SIDI FRAJ | 3 | 1 | ARIANA | 100.00% |
| A | 7180 | KEF | 3 | 1 | KEF | 100.00% |
| A | 5180 | MAHDIA | 3 | 1 | MAHDIA | 100.00% |
| A | 5180 | SALAKTA | 3 | 1 | MAHDIA | 100.00% |
| A | 5026 | MONASTIR | 3 | 1 | MONASTIR | 100.00% |
| A | 5010 | OURDANINE | 3 | 1 | MONASTIR | 100.00% |
| A | 5020 | ZAOUIET KONTECH | 3 | 1 | MONASTIR | 100.00% |
| A | 9170 | SFAX | 3 | 1 | SFAX | 100.00% |
| A | 2051 | EL HRAIRIA | 3 | 1 | TUNIS | 100.00% |
| A | 1064 | CITÉ INTILAKA | 3 | 1 | TUNIS | 100.00% |
| A | 1004 | EL MENZAH 8 | 3 | 1 | TUNIS | 100.00% |
| A | 8050 | HAMMAMAET | 3 | 1 | NABEUL | 100.00% |
| A | 2013 | MORNEG | 3 | 1 | BEN AROUS | 100.00% |
| A | 4000 | SOUSSE MEDINA | 3 | 1 | SOUSSE | 100.00% |
| A | 7040 | UTIQUE | 3 | 1 | BIZERTE | 100.00% |
| A | 7000 | JOUMINE | 3 | 1 | BIZERTE | 100.00% |
| A | 8000 | BENI KHALLED | 3 | 1 | NABEUL | 100.00% |
| A | 5040 | ZARMDINE | 3 | 1 | MONASTIR | 100.00% |
| A | 5000 | MOKNINE | 3 | 1 | MONASTIR | 100.00% |
| A | 5021 | MONASTIR | 3 | 1 | MONASTIR | 100.00% |
| A | 2094 | D HICHER | 3 | 1 | ARIANA | 100.00% |
| A | 8010 | JENDOUBA | 3 | 1 | JENDOUBA | 100.00% |
| A | 1005 | CITE ZAYATINE | 3 | 1 | TUNIS | 100.00% |
| A | 2240 | NAFTA | 3 | 1 | TOZUER | 100.00% |
| A | 1053 | BERGE DU LAC | 2 | 2930 | TUNIS | 100.00% |
| A | 1001 | REPUBLIQUE | 2 | 1628 | TUNIS | 99.94% |
| A | 3060 | MAHRAS | 2 | 1124 | SFAX | 100.00% |
| A | 2083 | JAAFAR 1 | 2 | 353 | ARIANA | 100.00% |
| A | 8011 | DAR CHAABANE ELFEHRI | 2 | 326 | NABEUL | 100.00% |
| A | 4031 | SOUSSE EZZOUHOUR | 2 | 282 | SOUSSE | 100.00% |
| A | 2091 | EL MENZAH 5 | 2 | 255 | ARIANA | 99.61% |
| A | 1002 | CITE JARDINS | 2 | 219 | TUNIS | 100.00% |
| A | 1095 | JAYARA | 2 | 210 | TUNIS | 100.00% |
| A | 1068 | ROMMANA | 2 | 164 | TUNIS | 100.00% |
| A | 1008 | BAB DJEDID | 2 | 129 | TUNIS | 100.00% |
| A | 2053 | CITE ENNOUR | 2 | 122 | TUNIS | 100.00% |
| A | 6100 | TAIEB MHIRI | 2 | 110 | SILIANA | 99.09% |
| A | 3052 | CITE EL HABIB | 2 | 103 | SFAX | 100.00% |
| A | 2015 | LE KRAM EST | 2 | 98 | TUNIS | 100.00% |
| A | 6052 | OUDHREF | 2 | 92 | GABES | 100.00% |
| A | 9171 | LESSOUDA | 2 | 90 | SIDI BOUZID | 100.00% |
| A | 2035 | CHARGUIA 1 | 2 | 85 | ARIANA | 98.82% |
| A | 6100 | HACHED | 2 | 84 | SILIANA | 98.81% |
| A | 6100 | NOZHA | 2 | 74 | SILIANA | 100.00% |
| A | 6116 | EL AROUSSA | 2 | 68 | SILIANA | 100.00% |
| A | 6016 | ARRAM | 2 | 60 | GABES | 100.00% |
| A | 2224 | EL MAHASSEN | 2 | 56 | TOZEUR | 100.00% |
| A | 5131 | EL HEKAIMA | 2 | 56 | MAHDIA | 100.00% |
| A | 2130 | CITE MODERNE | 2 | 52 | GAFSA | 100.00% |
| A | 2036 | CHOTRANA 2 | 2 | 50 | ARIANA | 100.00% |
| A | 4016 | BENI KALTHOUM | 2 | 49 | SOUSSE | 100.00% |
| A | 7110 | NEBEUR | 2 | 49 | KEF | 100.00% |
| A | 4120 | JERBA AEROPORT | 2 | 47 | MEDENINE | 100.00% |
| A | 6061 | CHATT ESSALEM | 2 | 46 | GABES | 100.00% |
| A | 5116 | OULED SALAH | 2 | 45 | MAHDIA | 100.00% |
| A | 1054 | AMILCAR | 2 | 42 | TUNIS | 100.00% |
| A | 2212 | AIN EL KARMA | 2 | 39 | TOZEUR | 100.00% |
| A | 3071 | OUED CHAABOUNI | 2 | 37 | SFAX | 100.00% |
| A | 2094 | CITE ALI BOURGUIBA | 2 | 37 | ARIANA | 100.00% |
| A | 2044 | ERRISSALA | 2 | 36 | BEN AROUS | 100.00% |
| A | 5036 | MENZEL HARB | 2 | 34 | MONASTIR | 100.00% |
| A | 1130 | ARGOUB ERROUMI | 2 | 34 | MANNOUBA | 100.00% |
| A | 4173 | SOUIHEL | 2 | 30 | MEDENINE | 100.00% |
| A | 4059 | SOUSSE CORNICHE | 2 | 29 | SOUSSE | 100.00% |
| A | 8014 | BIR DRASSEN | 2 | 28 | NABEUL | 100.00% |
| A | 8022 | BELLI | 2 | 28 | NABEUL | 100.00% |
| A | 4156 | GHIZEN | 2 | 27 | MEDENINE | 100.00% |
| A | 4032 | MENZEL BEL OUAER | 2 | 27 | SOUSSE | 100.00% |
| A | 6045 | TOUJANE | 2 | 25 | GABES | 100.00% |
| A | 5043 | BIR TAIEB | 2 | 25 | MONASTIR | 100.00% |
| A | 4020 | OULED AMEUR | 2 | 23 | SOUSSE | 100.00% |
| A | 5026 | GHENADA | 2 | 21 | MONASTIR | 100.00% |
| A | 5016 | KSAR HELAL RIADH | 2 | 18 | MONASTIR | 100.00% |
| A | 5090 | BAGHDADI | 2 | 16 | MONASTIR | 100.00% |
| A | 8044 | EL MAISRA | 2 | 16 | NABEUL | 100.00% |
| A | 2059 | BIR EL KASSAA | 2 | 15 | BEN AROUS | 100.00% |
| A | 2082 | CITE 20 MARS | 2 | 15 | BEN AROUS | 100.00% |
| A | 7034 | CAP ZBIB | 2 | 14 | BIZERTE | 100.00% |
| A | 2130 | CITE PRESIDENT | 2 | 14 | GAFSA | 100.00% |
| A | 3024 | CHAAL | 2 | 13 | SFAX | 100.00% |
| A | 2233 | BLED EL HADHAR | 2 | 12 | TOZEUR | 100.00% |
| A | 5130 | CHARAF | 2 | 12 | MAHDIA | 100.00% |
| A | 3111 | EL MOUTBASTA | 2 | 11 | KAIROUAN | 100.00% |
| A | 7081 | EZZITOUNE | 2 | 11 | BIZERTE | 100.00% |
| A | 8080 | BENI ABDELAZIZ | 2 | 10 | NABEUL | 100.00% |
| A | 2111 | CITE BAB ETTOUB | 2 | 10 | GAFSA | 100.00% |
| A | 4155 | EL GUEBLINE | 2 | 9 | MEDENINE | 100.00% |
| A | 3222 | CHENINI | 2 | 9 | TATAOUINE | 100.00% |
| A | 7180 | BIR HEDDI | 2 | 7 | KEF | 100.00% |
| A | 6041 | BARGUIA | 2 | 7 | GABES | 100.00% |
| A | 8023 | CITE BOU JAAFAR | 2 | 6 | NABEUL | 100.00% |
| A | 4000 | CITE EZZOUHOUR | 2 | 6 | SOUSSE | 100.00% |
| A | 2053 | EL OUERDIA 6 | 2 | 6 | TUNIS | 100.00% |
| A | 5022 | CITE EL JAZIA | 2 | 6 | MONASTIR | 100.00% |
| A | 2041 | CITE 2 MARS | 2 | 6 | ARIANA | 100.00% |
| A | 2111 | GAFSA GARE | 2 | 6 | GAFSA | 100.00% |
| A | 2046 | JARDINS DE CARTHAGE | 2 | 5 | TUNIS | 100.00% |
| A | 6014 | CITE AZAIEZ | 2 | 5 | GABES | 100.00% |
| A | 2017 | LE BARDO | 2 | 5 | TUNIS | 100.00% |
| A | 2045 | ELAOUINA | 2 | 5 | TUNIS | 100.00% |
| A | 1000 | BAB EL KHADHRA | 2 | 5 | TUNIS | 100.00% |
| A | 4081 | ZAOUET SOUSSE | 2 | 5 | SOUSSE | 100.00% |
| A | 4000 | KHEZEMA | 2 | 5 | SOUSSE | 100.00% |
| A | 3069 | SFAX | 2 | 5 | SFAX | 100.00% |
| A | 4025 | EL MOUISSETTE | 2 | 5 | SOUSSE | 100.00% |
| A | 2041 | 2 MARS | 2 | 4 | ARIANA | 100.00% |
| A | 5199 | MAHDIA | 2 | 4 | MAHDIA | 100.00% |
| A | 1130 | TUNIS | 2 | 4 | MANNOUBA | 100.00% |
| A | 3081 | ESSAADI | 2 | 4 | SFAX | 100.00% |
| A | 3011 | SAKIET EZZIT | 2 | 4 | SFAX | 100.00% |
| A | 1003 | CITE STAR | 2 | 4 | TUNIS | 100.00% |
| A | 3100 | HAFFOUZ | 2 | 4 | KAIROUAN | 100.00% |
| A | 1009 | EL OUERDIA 5 | 2 | 4 | TUNIS | 100.00% |
| A | 4011 | SAHLOUL | 2 | 4 | SOUSSE | 100.00% |
| A | 2036 | AOUINA | 2 | 3 | ARIANA | 100.00% |
| A | 2035 | LA SOUKRA | 2 | 3 | ARIANA | 100.00% |
| A | 2092 | EL MANAR 3 | 2 | 3 | TUNIS | 100.00% |
| A | 5170 | CHEBBA | 2 | 3 | MAHDIA | 100.00% |
| A | 5028 | JEMMAL | 2 | 3 | MONASTIR | 100.00% |
| A | 4051 | SAHLOUL | 2 | 3 | SOUSSE | 100.00% |
| A | 5000 | JEMMEL | 2 | 3 | MONASTIR | 100.00% |
| A | 8011 | DAR CHAAABNE | 2 | 3 | NABEUL | 100.00% |
| A | 4000 | KHEZEMA EST | 2 | 3 | SOUSSE | 100.00% |
| A | 6032 | CITE 7 NOVEMBRE | 2 | 3 | GABES | 100.00% |
| A | 5000 | JAMMEL | 2 | 3 | MONASTIR | 100.00% |
| A | 5025 | MONASTIR | 2 | 3 | MONASTIR | 100.00% |
| A | 5035 | CITE GOURRAIA | 2 | 3 | MONASTIR | 100.00% |
| A | 6140 | TUNIS | 2 | 3 | SILIANA | 100.00% |
| A | 4000 | BOUKHZAR | 2 | 3 | SOUSSE | 100.00% |
| A | 3253 | CITE OLYMPIQUE | 2 | 3 | TATAOUINE | 100.00% |
| A | 4180 | HOUMET ESSOUK | 2 | 2 | MEDENINE | 100.00% |
| A | 2045 | TAIEB MHIRI | 2 | 2 | TUNIS | 100.00% |
| A | 2036 | LA MARSA | 2 | 2 | ARIANA | 100.00% |
| A | 1053 | LAC2 | 2 | 2 | TUNIS | 100.00% |
| A | 2055 | BIR EL BAY | 2 | 2 | BEN AROUS | 100.00% |
| A | 1004 | EL MANAR 1 | 2 | 2 | TUNIS | 100.00% |
| A | 1124 | TUNIS | 2 | 2 | MANNOUBA | 100.00% |
| A | 2094 | CITE ETTADHAMEN | 2 | 2 | ARIANA | 100.00% |
| A | 1133 | TEBOURBA | 2 | 2 | MANNOUBA | 100.00% |
| A | 3000 | EL AIN | 2 | 2 | SFAX | 100.00% |
| A | 3000 | SAKIET EZZIT | 2 | 2 | SFAX | 100.00% |
| A | 7070 | RAS JEBAL | 2 | 2 | BIZERTE | 100.00% |
| A | 8000 | BIR CHELLOUF | 2 | 2 | NABEUL | 100.00% |
| A | 8045 | EL GHORFA | 2 | 2 | NABEUL | 100.00% |
| A | 3130 | BOUHAJLA | 2 | 2 | KAIROUAN | 100.00% |
| A | 3100 | HAJEB LAAYOUN | 2 | 2 | KAIROUAN | 100.00% |
| A | 4011 | HAMAM SOUSSE | 2 | 2 | SOUSSE | 100.00% |
| A | 4000 | AKOUDA | 2 | 2 | SOUSSE | 100.00% |
| A | 6052 | RUE DE LA REPUBLIQUE | 2 | 2 | GABES | 100.00% |
| A | 2074 | EL MOUROUJ6 | 2 | 2 | BEN AROUS | 100.00% |
| A | 6141 | KESRA | 2 | 2 | SILIANA | 100.00% |
| A | 2052 | SIDI HSSINE | 2 | 2 | TUNIS | 100.00% |
| A | 2011 | BEN YOUNES | 2 | 2 | MANNOUBA | 100.00% |
| A | 2062 | OMRANE SUPERIEUR | 2 | 2 | TUNIS | 100.00% |
| A | 2073 | BOREJ LOUZIR | 2 | 2 | ARIANA | 100.00% |
| A | 5000 | SIDI AMEUR | 2 | 2 | MONASTIR | 100.00% |
| A | 4000 | HERGLA | 2 | 2 | SOUSSE | 100.00% |
| A | 8075 | DAR CHAABANE | 2 | 2 | NABEUL | 100.00% |
| A | 1053 | JARDIN DE CARTHAGE | 2 | 1 | TUNIS | 100.00% |
| A | 1053 | CITE LES PINS | 2 | 1 | TUNIS | 100.00% |
| A | 3225 | TATAOUINE | 2 | 1 | TATAOUINE | 100.00% |
| A | 4186 | HOUMT SOUK | 2 | 1 | MEDENINE | 100.00% |
| A | 1000 | TRIPOLI | 2 | 1 | TRIPOLI | 100.00% |
| A | 4115 | HOUMT SOUK | 2 | 1 | MEDENINE | 100.00% |
| A | 1006 | BAB SADOUN | 2 | 1 | TUNIS | 100.00% |
| A | 2015 | KHEIREDDINE | 2 | 1 | TUNIS | 100.00% |
| A | 1004 | MANZEH 7 | 2 | 1 | ARIANA | 100.00% |
| A | 1000 | H LIF | 2 | 1 | TUNIS | 100.00% |
| A | 1013 | EL MENZAH | 2 | 1 | TUNIS | 100.00% |
| A | 2013 | NOUVELLE MEDINA | 2 | 1 | BEN AROUS | 100.00% |
| A | 1003 | EL KHADRA | 2 | 1 | TUNIS | 100.00% |
| A | 1004 | MENZAH 4 | 2 | 1 | TUNIS | 100.00% |
| A | 1000 | EL MOUROUJ | 2 | 1 | TUNIS | 100.00% |
| A | 1009 | EL OUARDIA1 | 2 | 1 | TUNIS | 100.00% |
| A | 1091 | ARIANA | 2 | 1 | TUNIS | 100.00% |
| A | 1089 | TUNIS | 2 | 1 | TUNIS | 100.00% |
| A | 1000 | MHAMDIA | 2 | 1 | TUNIS | 100.00% |
| A | 2045 | CITE TAIEB MHIRI | 2 | 1 | MONASTIR | 100.00% |
| A | 1145 | MHEMDIA | 2 | 1 | BEN AROUS | 100.00% |
| A | 2017 | WIFAK | 2 | 1 | TUNIS | 100.00% |
| A | 2016 | LES JARDINS DE CARTHAGE | 2 | 1 | TUNIS | 100.00% |
| A | 8016 | SIDI DAOUED | 2 | 1 | NABEUL | 100.00% |
| A | 2084 | BORDJ CEDRIA | 2 | 1 | HAMMAM LIF | 100.00% |
| A | 1000 | EL WARDIA | 2 | 1 | TUNIS | 100.00% |
| A | 2094 | ETTADHAMEN | 2 | 1 | ARIANA | 100.00% |
| A | 2016 | SIDI BOU SAID | 2 | 1 | TUNIS | 100.00% |
| A | 1000 | TUNIS BELVEDERE | 2 | 1 | TUNIS | 100.00% |
| A | 1110 | MORNAGUI | 2 | 1 | A | 100.00% |
| A | 2074 | EL MOUROUJ II | 2 | 1 | BEN AROUS | 100.00% |
| A | 4165 | MIDOUN | 2 | 1 | MEDENINE | 100.00% |
| A | 2074 | EL MOUROUJ2 | 2 | 1 | BEN AROUS | 100.00% |
| A | 1064 | INTILAKA | 2 | 1 | TUNIS | 100.00% |
| A | 2073 | SOUKRA | 2 | 1 | ARIANA | 100.00% |
| A | 2083 | GHAZELLA | 2 | 1 | ARIANA | 100.00% |
| A | 7080 | ML JMIL | 2 | 1 | BIZERTE | 100.00% |
| A | 1131 | BIR MCHERGUA | 2 | 1 | ZAGHOUAN | 100.00% |
| A | 2080 | RIADH EL ANDALOUS | 2 | 1 | ARIANA | 100.00% |
| A | 3020 | MENZEL CHAKER | 2 | 1 | SFAX | 100.00% |
| A | 2080 | PETITE ARIANA | 2 | 1 | ARIANA | 100.00% |
| A | 2000 | MONASTIR | 2 | 1 | MONASTIR | 100.00% |
| A | 5013 | MONASTIR | 2 | 1 | MONASTIR | 100.00% |
| A | 7024 | AOUSJA | 2 | 1 | BIZERTE | 100.00% |
| A | 7003 | BIZERTE | 2 | 1 | BIZERTE | 100.00% |
| A | 7060 | UITIQUE | 2 | 1 | BIZERTE | 100.00% |
| A | 8045 | BIR JEDEY | 2 | 1 | NABEUL | 100.00% |
| A | 8080 | EL MIDA | 2 | 1 | NABEUL | 100.00% |
| A | 2057 | SIDI THABET | 2 | 1 | ARIANA | 100.00% |
| A | 4000 | THERAYET | 2 | 1 | SOUSSE | 100.00% |
| A | 3125 | SBIKHA | 2 | 1 | KAIROUAN | 100.00% |
| A | 5012 | SIDI AMEUR | 2 | 1 | MONASTIR | 100.00% |
| A | 4000 | BOUFICHA | 2 | 1 | BOUFICHA | 100.00% |
| A | 3100 | KAIRAOUEN | 2 | 1 | SFAX | 100.00% |
| A | 9032 | DOGGA | 2 | 1 | BEJA | 100.00% |
| A | 2040 | RADES MALEHA | 2 | 1 | BEN AROUS | 100.00% |
| A | 2084 | ARIANA | 2 | 1 | ARIANA | 100.00% |
| A | 2010 | DAOUAR HICHER | 2 | 1 | MANNOUBA | 100.00% |
| A | 1212 | KASSERINE | 2 | 1 | KASSERINE | 100.00% |
| A | 1200 | SBITLA | 2 | 1 | KASSERINE | 100.00% |
| A | 1230 | KASSERINE | 2 | 1 | KASSERINE | 100.00% |
| A | 2015 | CARTHAGE | 2 | 1 | TUNIS | 100.00% |
| A | 4000 | CITE CHABEB | 2 | 1 | SOUSSE | 100.00% |
| A | 5000 | TUNIS | 2 | 1 | TUNIS | 100.00% |
| A | 4026 | SIDI EL HANI | 2 | 1 | SOUSSE | 100.00% |
| A | 4031 | ZAOUIET SOUSSE | 2 | 1 | SOUSSE | 100.00% |
| A | 4000 | KALAA SEGHIRA | 2 | 1 | SOUSSE | 100.00% |
| A | 4025 | MSAKEN | 2 | 1 | SOUSSE | 100.00% |
| A | 4013 | MESAADINE | 2 | 1 | SOUSSE | 100.00% |
| A | 2141 | GAFSA | 2 | 1 | GAFSA | 100.00% |
| A | 2183 | GAFSA | 2 | 1 | GAFSA | 100.00% |
| A | 6010 | CITÉ CHORFA | 2 | 1 | GABES | 100.00% |
| A | 4120 | MELLITA | 2 | 1 | MEDENINE | 100.00% |
| A | 3217 | TATAOUINE | 2 | 1 | TATAOUINE | 100.00% |
| A | 7130 | EL KEF | 2 | 1 | KEF | 100.00% |
| A | 7000 | ZARZOUNA | 2 | 1 | BIZERTE | 100.00% |
| A | 2080 | NKHILET | 2 | 1 | ARIANA | 100.00% |
| A | 2045 | CITE ETTADHAMEN | 2 | 1 | ARIANA | 100.00% |
| A | 5160 | JEM | 2 | 1 | MAHDIA | 100.00% |
| A | 5070 | MOKNINE | 2 | 1 | MONASTIR | 100.00% |
| A | 5025 | BENENE | 2 | 1 | MONASTIR | 100.00% |
| A | 5010 | OUARDANIN | 2 | 1 | MONASTIR | 100.00% |
| A | 5013 | JEMMAL | 2 | 1 | MONASTIR | 100.00% |
| A | 5022 | MENZEL ENOUR | 2 | 1 | MONASTIR | 100.00% |
| A | 5000 | SAHLINE | 2 | 1 | MONASTIR | 100.00% |
| A | 4041 | THRAYET | 2 | 1 | SOUSSE | 100.00% |
| A | 6000 | SELIANA | 2 | 1 | SELIANA | 100.00% |
| A | 6115 | BARGOU | 2 | 1 | SILIANA | 100.00% |
| A | 6100 | TAIEB MAHIRI | 2 | 1 | SILIANA | 100.00% |
| A | 2076 | EL MARSA | 2 | 1 | TUNIS | 100.00% |
| A | 6000 | BAB BHAR | 2 | 1 | GABES | 100.00% |
| A | 2052 | ESSOMRANE | 2 | 1 | TUNIS | 100.00% |
| A | 1095 | ESSIJOUMI | 2 | 1 | TUNIS | 100.00% |
| A | 2087 | CITE BEN YOUNES | 2 | 1 | MANNOUBA | 100.00% |
| A | 2054 | TUNIS | 2 | 1 | BEN AROUS | 100.00% |
| A | 8070 | EL MIDA | 2 | 1 | NABEUL | 100.00% |
| A | 1000 | CITE IBN SINA | 2 | 1 | TUNIS | 100.00% |
| A | 2073 | MANSOURA | 2 | 1 | ARIANA | 100.00% |
| A | 7010 | SEJENEN | 2 | 1 | BIZERTE | 100.00% |
| A | 7053 | BIZERTE | 2 | 1 | BIZERTE | 100.00% |
| A | 7093 | EL ALIA | 2 | 1 | BIZERTE | 100.00% |
| A | 7000 | BIZETE | 2 | 1 | BIZERTE | 100.00% |
| A | 7014 | CITE 7 NOVEMBRE | 2 | 1 | BIZERTE | 100.00% |
| A | 4100 | KOUTINE | 2 | 1 | MEDENINE | 100.00% |
| A | 4145 | HOUMT SOUK | 2 | 1 | MEDENINE | 100.00% |
| A | 6000 | CITE MED ALI | 2 | 1 | GABES | 100.00% |
| A | 6052 | RUE TAREK IBN ZIED | 2 | 1 | GABES | 100.00% |
| A | 6042 | EL HICHA | 2 | 1 | GABES | 100.00% |
| A | 8060 | DAR CHAABNE | 2 | 1 | NABEUL | 100.00% |
| A | 8050 | EL MRAZKA HAMMAMET | 2 | 1 | NABEUL | 100.00% |
| A | 8011 | DAR CHAABENE | 2 | 1 | NABEUL | 100.00% |
| A | 8000 | TAKELSA | 2 | 1 | NABEUL | 100.00% |
| A | 3220 | TATAOUIN | 2 | 1 | TATAOUIN | 100.00% |
| A | 2096 | YASMINET | 2 | 1 | TUNIS | 100.00% |
| A | 2023 | CITE EL FATH | 2 | 1 | TUNIS | 100.00% |
| A | 1142 | BOREJ EL AMRI | 2 | 1 | MANNOUBA | 100.00% |
| A | 2041 | 18 JANVIER | 2 | 1 | ARIANA | 100.00% |
| A | 2080 | CITE MANSOURA | 2 | 1 | 2080 | 100.00% |
| A | 3125 | KAIROUAN | 2 | 1 | KAIROUAN | 100.00% |
| A | 3100 | EL ALAA | 2 | 1 | KAIROUAN | 100.00% |
| A | 7112 | KEF | 2 | 1 | KEF | 100.00% |
| A | 1240 | KASSERINE | 2 | 1 | KASSERINE | 100.00% |
| A | 2076 | MARSA ERRIADH | 1 | 635 | TUNIS | 100.00% |
| A | 2086 | CITE KHALED IBN EL WALID | 1 | 552 | MANNOUBA | 99.64% |
| A | 2037 | CITE ENNASR 2 | 1 | 447 | ARIANA | 100.00% |
| A | 7035 | MENZEL ABDERRAHMAN | 1 | 411 | BIZERTE | 100.00% |
| A | 2042 | ETTAHRIR 1 | 1 | 400 | TUNIS | 100.00% |
| A | 1007 | EL MELLASSINE | 1 | 370 | TUNIS | 100.00% |
| A | 2016 | CARTAGE BYRSA | 1 | 253 | TUNIS | 100.00% |
| A | 8012 | FONDOUK JEDID | 1 | 228 | NABEUL | 100.00% |
| A | 2091 | EL MENZAH 6 | 1 | 185 | ARIANA | 98.92% |
| A | 5120 | OULED CHAMAKH | 1 | 175 | MAHDIA | 100.00% |
| A | 1008 | BAB MENARA | 1 | 173 | TUNIS | 100.00% |
| A | 4144 | EL MOUENSA | 1 | 173 | MEDENINE | 100.00% |
| A | 3027 | SFAX EL JADIDA | 1 | 156 | SFAX | 99.36% |
| A | 9112 | FAYEDH | 1 | 152 | SIDI BOUZID | 100.00% |
| A | 4051 | SOUSSE KHEZAMA | 1 | 151 | SOUSSE | 100.00% |
| A | 1111 | JEBEL EL OUST | 1 | 146 | ZAGHOUAN | 100.00% |
| A | 2053 | EL OUERDIA 4 | 1 | 138 | TUNIS | 100.00% |
| A | 3064 | CITE EL BAHRI | 1 | 120 | SFAX | 100.00% |
| A | 2094 | CITE EL BASSATINE1 | 1 | 119 | ARIANA | 100.00% |
| A | 3020 | MENZEL HEDI CHAKER | 1 | 105 | SFAX | 100.00% |
| A | 4100 | AMRA NOUVELLE | 1 | 105 | MEDENINE | 100.00% |
| A | 1114 | EL BATTAN | 1 | 99 | MANNOUBA | 97.98% |
| A | 1115 | SAOUEF | 1 | 92 | ZAGHOUAN | 100.00% |
| A | 3200 | CITE ENNOUR | 1 | 87 | TATAOUINE | 100.00% |
| A | 2094 | CITE RAFAHA | 1 | 86 | ARIANA | 100.00% |
| A | 7080 | CITE BIR REMEL | 1 | 86 | BIZERTE | 100.00% |
| A | 1082 | CITE EL MAHRAJENE | 1 | 84 | TUNIS | 100.00% |
| A | 2098 | RADES MELIANE | 1 | 83 | BEN AROUS | 100.00% |
| A | 1000 | BAB EL JAZIRA | 1 | 80 | TUNIS | 100.00% |
| A | 2036 | SIDI FREJ | 1 | 77 | ARIANA | 100.00% |
| A | 1135 | CHEBEDDA | 1 | 77 | BEN AROUS | 100.00% |
| A | 1152 | CITE DU LYCEE | 1 | 76 | ZAGHOUAN | 98.68% |
| A | 2130 | CITE ENNOUHOUDH | 1 | 73 | GAFSA | 100.00% |
| A | 5015 | BOU HAJAR | 1 | 72 | MONASTIR | 100.00% |
| A | 1100 | AIN LANSARINE | 1 | 70 | ZAGHOUAN | 100.00% |
| A | 4115 | MELLITA JERBA | 1 | 67 | MEDENINE | 100.00% |
| A | 3062 | SIDI ABBES | 1 | 64 | SFAX | 100.00% |
| A | 4111 | OUM ETTAMAR | 1 | 62 | MEDENINE | 100.00% |
| A | 2083 | JAAFAR 2 | 1 | 62 | ARIANA | 100.00% |
| A | 1095 | BORJ CHAKIR | 1 | 59 | TUNIS | 100.00% |
| A | 4114 | ERRAJA | 1 | 59 | MEDENINE | 100.00% |
| A | 2091 | CITE BELVEDERE 2 | 1 | 58 | ARIANA | 100.00% |
| A | 1153 | EL FEJJA | 1 | 56 | MANNOUBA | 100.00% |
| A | 3013 | MERKEZ CHAABOUNI | 1 | 56 | SFAX | 100.00% |
| A | 4151 | KSAR JEDID | 1 | 52 | MEDENINE | 100.00% |
| A | 4214 | JEMNA | 1 | 52 | KEBILI | 100.00% |
| A | 7130 | CITE BOURGUIBA | 1 | 49 | KEF | 100.00% |
| A | 3074 | EL AOUABED | 1 | 48 | SFAX | 100.00% |
| A | 9021 | SIDI SMAIL | 1 | 47 | BEJA | 100.00% |
| A | 6100 | SALAH | 1 | 46 | SILIANA | 100.00% |
| A | 3061 | SIDI MANSOUR | 1 | 44 | SFAX | 100.00% |
| A | 2190 | SNED | 1 | 44 | GAFSA | 100.00% |
| A | 3099 | EL BOUSTEN | 1 | 40 | SFAX | 100.00% |
| A | 2082 | MEGHIRA INZEL | 1 | 40 | BEN AROUS | 100.00% |
| A | 4134 | CHAMMAKH | 1 | 39 | MEDENINE | 100.00% |
| A | 1006 | EL HALFAOUINE | 1 | 38 | TUNIS | 100.00% |
| A | 6011 | CITE EL IZDIHAR | 1 | 38 | GABES | 100.00% |
| A | 1053 | BERGES DU LAC | 1 | 36 | TUNIS | 100.00% |
| A | 2075 | EL MANSOURA | 1 | 36 | MANNOUBA | 100.00% |
| A | 4133 | ROBBANA | 1 | 36 | MEDENINE | 100.00% |
| A | 3031 | MERKEZ BOUACIDA | 1 | 35 | SFAX | 100.00% |
| A | 2076 | CITE DES JUGES 2 | 1 | 35 | TUNIS | 97.14% |
| A | 1143 | BORJ ETTOUMI | 1 | 35 | MANNOUBA | 100.00% |
| A | 2245 | BEN FARJALLAH | 1 | 35 | TOZEUR | 100.00% |
| A | 8011 | BAYOUB | 1 | 34 | NABEUL | 100.00% |
| A | 9013 | OUED ZARGA | 1 | 33 | BEJA | 100.00% |
| A | 4099 | MSAKEN EL GUEBLIA | 1 | 33 | SOUSSE | 100.00% |
| A | 4054 | CITE SAHLOUL | 1 | 32 | SOUSSE | 100.00% |
| A | 4060 | CITE NOUVELLE | 1 | 32 | SOUSSE | 100.00% |
| A | 3037 | GARGOUR | 1 | 32 | SFAX | 100.00% |
| A | 4212 | OUM SOMAA | 1 | 32 | KEBILI | 100.00% |
| A | 8099 | ZAOUIET JEDIDI | 1 | 30 | NABEUL | 100.00% |
| A | 1059 | EL HAFSIA | 1 | 29 | TUNIS | 100.00% |
| A | 8030 | BATROU | 1 | 29 | NABEUL | 100.00% |
| A | 3113 | AIN JELLOULA | 1 | 29 | KAIROUAN | 100.00% |
| A | 4164 | GRIBIS | 1 | 29 | MEDENINE | 100.00% |
| A | 7021 | CITE BEN AROUS | 1 | 28 | BIZERTE | 100.00% |
| A | 2083 | CITE ESSAHAFA | 1 | 28 | ARIANA | 100.00% |
| A | 2241 | CITE EL IZDIHAR | 1 | 28 | TOZEUR | 100.00% |
| A | 3013 | CITE 2000 | 1 | 27 | SFAX | 100.00% |
| A | 3023 | OUED RMAL | 1 | 26 | SFAX | 100.00% |
| A | 5017 | EL HEDADRA | 1 | 26 | MONASTIR | 100.00% |
| A | 3050 | BOU SAID | 1 | 26 | SFAX | 100.00% |
| A | 2130 | CITE WED LARTA | 1 | 26 | GAFSA | 100.00% |
| A | 4089 | EL KANTAOUI | 1 | 25 | SOUSSE | 100.00% |
| A | 4165 | MAHBOUBINE | 1 | 25 | MEDENINE | 100.00% |
| A | 3142 | EL BATEN | 1 | 25 | KAIROUAN | 100.00% |
| A | 4216 | EL AOUINA | 1 | 24 | KEBILI | 95.83% |
| A | 5027 | ETTIAYRA | 1 | 22 | MONASTIR | 100.00% |
| A | 2053 | CITE BOU HJAR | 1 | 22 | TUNIS | 100.00% |
| A | 4195 | GUECHIINE | 1 | 22 | MEDENINE | 100.00% |
| A | 6100 | RIADH | 1 | 22 | SILIANA | 95.45% |
| A | 3032 | MERKEZ DEROUICHE | 1 | 21 | SFAX | 100.00% |
| A | 8046 | ZAOUIET EL MGAIES | 1 | 21 | NABEUL | 100.00% |
| A | 2012 | EL HABIBIA | 1 | 20 | MANNOUBA | 100.00% |
| A | 3065 | SFAX PORT | 1 | 20 | SFAX | 100.00% |
| A | 6033 | CITE EL AMEL | 1 | 20 | GABES | 100.00% |
| A | 6100 | ZOUHOUR | 1 | 20 | SILIANA | 100.00% |
| A | 8062 | CITE EL MAHRSI 1 | 1 | 19 | NABEUL | 100.00% |
| A | 2052 | CITE ESSAADA | 1 | 19 | TUNIS | 100.00% |
| A | 5041 | MENZEL KHIR | 1 | 19 | MONASTIR | 100.00% |
| A | 2060 | CASINO LA GOULETTE | 1 | 18 | TUNIS | 100.00% |
| A | 2028 | EL BASSATINE | 1 | 18 | MANNOUBA | 100.00% |
| A | 1100 | MHIRIS | 1 | 18 | ZAGHOUAN | 100.00% |
| A | 2098 | RADES MONGIL | 1 | 17 | BEN AROUS | 100.00% |
| A | 4060 | RUE BOUCHOUCHA | 1 | 17 | SOUSSE | 100.00% |
| A | 1140 | ESSAADA | 1 | 17 | ZAGHOUAN | 100.00% |
| A | 5132 | SAKIET EL KHADEM | 1 | 17 | MAHDIA | 100.00% |
| A | 6120 | CITE ABDRABBAH 1 | 1 | 17 | SILIANA | 100.00% |
| A | 2131 | SIDI AICH | 1 | 17 | GAFSA | 100.00% |
| A | 4015 | EL FRADA | 1 | 17 | SOUSSE | 100.00% |
| A | 6042 | EL AKARIT | 1 | 17 | GABES | 100.00% |
| A | 2114 | SIDI BOUBAKER | 1 | 16 | GAFSA | 100.00% |
| A | 3052 | CITE DE LA SANTE | 1 | 16 | SFAX | 100.00% |
| A | 2081 | RAOUED | 1 | 16 | ARIANA | 100.00% |
| A | 4126 | BENI MAAGUEL | 1 | 16 | MEDENINE | 100.00% |
| A | 4293 | EL MANSOURA | 1 | 16 | KEBILI | 100.00% |
| A | 5124 | TLELSA | 1 | 15 | MAHDIA | 100.00% |
| A | 1132 | OUED EZZIT | 1 | 15 | ZAGHOUAN | 100.00% |
| A | 3073 | SBIH | 1 | 15 | SFAX | 100.00% |
| A | 2130 | CITE EZZOUHOUR 1 | 1 | 15 | GAFSA | 100.00% |
| A | 5117 | OULED JABALLAH | 1 | 15 | MAHDIA | 100.00% |
| A | 6111 | EL AKHOUAT | 1 | 15 | SILIANA | 100.00% |
| A | 5122 | MENZEL HACHED | 1 | 14 | MAHDIA | 100.00% |
| A | 4122 | KSAR EL JIRA | 1 | 14 | MEDENINE | 100.00% |
| A | 3151 | ZAAFRANA | 1 | 14 | KAIROUAN | 100.00% |
| A | 5193 | OUED BEJA | 1 | 14 | MAHDIA | 100.00% |
| A | 4263 | JERSINE | 1 | 14 | KEBILI | 100.00% |
| A | 9111 | OUM EL ADHAM | 1 | 14 | SIDI BOUZID | 100.00% |
| A | 9141 | EL MAKAREM | 1 | 14 | SIDI BOUZID | 100.00% |
| A | 1006 | BORJ ZOUARA | 1 | 13 | TUNIS | 100.00% |
| A | 3016 | EL LOUZA | 1 | 13 | SFAX | 100.00% |
| A | 7040 | AIN REKOUB | 1 | 13 | BIZERTE | 100.00% |
| A | 9110 | LABAYEDH | 1 | 13 | SIDI BOUZID | 100.00% |
| A | 6140 | BENI HAZAM | 1 | 13 | SILIANA | 100.00% |
| A | 6024 | NOUVELLE ZRAOUA | 1 | 12 | GABES | 100.00% |
| A | 3150 | AIN SAYADA | 1 | 12 | KAIROUAN | 100.00% |
| A | 8110 | AIN ESSNOUSSI | 1 | 12 | JENDOUBA | 100.00% |
| A | 4020 | BIR JEDID | 1 | 12 | SOUSSE | 100.00% |
| A | 6113 | AIN ACHOUR | 1 | 12 | SILIANA | 100.00% |
| A | 2054 | EL GOUNNA | 1 | 11 | BEN AROUS | 100.00% |
| A | 2170 | CITE DES JEUNES | 1 | 11 | GAFSA | 100.00% |
| A | 6021 | CITE EL IZDIHAR | 1 | 11 | GABES | 100.00% |
| A | 6025 | BENI ZELTEN | 1 | 11 | GABES | 100.00% |
| A | 9061 | ESSKHIRA | 1 | 10 | BEJA | 100.00% |
| A | 7024 | TOUIBIA | 1 | 10 | BIZERTE | 100.00% |
| A | 2141 | MENZEL MIMOUN | 1 | 10 | GAFSA | 100.00% |
| A | 4179 | SIDI MEHREZ | 1 | 9 | MEDENINE | 100.00% |
| A | 1114 | CITE BRIK | 1 | 9 | MANNOUBA | 100.00% |
| A | 4000 | CITE LAOUINA | 1 | 9 | SOUSSE | 100.00% |
| A | 7026 | CITE 7 NOVEMBRE | 1 | 9 | BIZERTE | 100.00% |
| A | 8061 | SIDI DHAHER | 1 | 9 | NABEUL | 100.00% |
| A | 5192 | ZELBA | 1 | 9 | MAHDIA | 100.00% |
| A | 2130 | CITE DES JEUNNES | 1 | 9 | GAFSA | 100.00% |
| A | 1046 | ALI BACH-HAMBA | 1 | 8 | TUNIS | 100.00% |
| A | 1000 | REPUBLIQUE | 1 | 8 | TUNIS | 100.00% |
| A | 3025 | OULED KACEM | 1 | 8 | SFAX | 100.00% |
| A | 1006 | EL TAOUFIK | 1 | 8 | TUNIS | 100.00% |
| A | 1280 | AIN OUM JDOUR | 1 | 8 | KASSERINE | 100.00% |
| A | 1002 | KASSERINE | 1 | 8 | KASSERINE | 100.00% |
| A | 9159 | ESSALAMA | 1 | 8 | SIDI BOUZID | 100.00% |
| A | 3220 | CITE EL BICHER | 1 | 8 | TATAOUINE | 100.00% |
| A | 5127 | ESSAAD | 1 | 8 | MAHDIA | 100.00% |
| A | 9116 | DHOUIBETTE | 1 | 8 | SIDI BOUZID | 100.00% |
| A | 2045 | AIN ZAGHOUEN | 1 | 7 | TUNIS | 100.00% |
| A | 1002 | BAB BHAR | 1 | 7 | TUNIS | 100.00% |
| A | 9040 | AIN EL HAMMAM | 1 | 7 | BEJA | 100.00% |
| A | 3041 | CITE 20 MARS | 1 | 7 | SFAX | 100.00% |
| A | 7021 | CITE CALYPTUS | 1 | 7 | BIZERTE | 100.00% |
| A | 8070 | KSAR SAAD | 1 | 7 | NABEUL | 100.00% |
| A | 9060 | AIN YOUNES | 1 | 7 | BEJA | 100.00% |
| A | 5110 | EL HOUS | 1 | 7 | MAHDIA | 100.00% |
| A | 5031 | CITE 18 JANVIER | 1 | 6 | MONASTIR | 100.00% |
| A | 3130 | AIN EL GHRAB | 1 | 6 | KAIROUAN | 100.00% |
| A | 2053 | EL OUERDIA | 1 | 6 | TUNIS | 100.00% |
| A | 9071 | CITE 02 MARS | 1 | 6 | BEJA | 100.00% |
| A | 7030 | CITE EL OMRANE 2 | 1 | 6 | BIZERTE | 100.00% |
| A | 3223 | CITE CASERNE | 1 | 6 | TATAOUINE | 100.00% |
| A | 5111 | CITE DES INFIRMIERS | 1 | 6 | MAHDIA | 100.00% |
| A | 6122 | DOUKHANIA | 1 | 6 | SILIANA | 100.00% |
| A | 6100 | STEG | 1 | 6 | SILIANA | 100.00% |
| A | 9180 | BOUTIQUE ISSA | 1 | 5 | SIDI BOUZID | 100.00% |
| A | 2094 | JARDINS EL MENZAH 2 | 1 | 5 | ARIANA | 100.00% |
| A | 1082 | EL MENZAH | 1 | 5 | TUNIS | 100.00% |
| A | 6100 | CITE CNRPS | 1 | 5 | SILIANA | 100.00% |
| A | 1110 | GHDIR ELGOLLA | 1 | 5 | MANNOUBA | 100.00% |
| A | 4176 | ARKOU | 1 | 5 | MEDENINE | 100.00% |
| A | 5000 | OUARDANINE | 1 | 5 | MONASTIR | 100.00% |
| A | 4014 | CHIHIA | 1 | 5 | SOUSSE | 100.00% |
| A | 2192 | MAJOURA | 1 | 5 | GAFSA | 100.00% |
| A | 2142 | KEF DERBI | 1 | 5 | GAFSA | 100.00% |
| A | 9121 | BOU ATTOUCH | 1 | 5 | SIDI BOUZID | 100.00% |
| A | 9120 | BATEN EL AGAAG | 1 | 5 | SIDI BOUZID | 100.00% |
| A | 6125 | BORJ MESSAOUDI | 1 | 5 | SILIANA | 100.00% |
| A | 2098 | CITE EL EZZ | 1 | 5 | BEN AROUS | 100.00% |
| A | 4031 | ZOUHOUR | 1 | 5 | SOUSSE | 100.00% |
| A | 4280 | KEBILI BEYEZ | 1 | 4 | KEBILI | 100.00% |
| A | 3026 | AGUEGCHA | 1 | 4 | SFAX | 100.00% |
| A | 5199 | CITE ESSAADA | 1 | 4 | MAHDIA | 100.00% |
| A | 7015 | CITE EL AMEL | 1 | 4 | BIZERTE | 100.00% |
| A | 3194 | SBIKHA | 1 | 4 | KAIROUAN | 100.00% |
| A | 4000 | SFAYA | 1 | 4 | SOUSSE | 100.00% |
| A | 9140 | CITE DES ABRICOTS | 1 | 4 | SIDI BOUZID | 100.00% |
| A | 2130 | OUED LARTA | 1 | 4 | GAFSA | 100.00% |
| A | 5133 | CHAHDA | 1 | 4 | MAHDIA | 100.00% |
| A | 5110 | CHOUARIA | 1 | 4 | MAHDIA | 100.00% |
| A | 9170 | BIR GZAIEL | 1 | 4 | SIDI BOUZID | 100.00% |
| A | 6150 | EL HBABSA | 1 | 4 | SILIANA | 100.00% |
| A | 6111 | LAKHOUET | 1 | 4 | SILIANA | 100.00% |
| A | 4000 | CITE AEROPORT | 1 | 4 | SOUSSE | 100.00% |
| A | 6099 | GABES EL HIDAYA | 1 | 4 | GABES | 100.00% |
| A | 2089 | CITE EL MECHTEL | 1 | 3 | TUNIS | 100.00% |
| A | 1000 | BELLEVUE | 1 | 3 | TUNIS | 100.00% |
| A | 2046 | JARDIN DE CARTHAGE | 1 | 3 | TUNIS | 100.00% |
| A | 6070 | ZRIBA | 1 | 3 | GABES | 100.00% |
| A | 9172 | GOUBRAR | 1 | 3 | SIDI BOUZID | 100.00% |
| A | 3100 | MANSOURA | 1 | 3 | KAIROUAN | 100.00% |
| A | 4023 | KALAA ESGHIRA | 1 | 3 | SOUSSE | 100.00% |
| A | 4000 | LAOUINA | 1 | 3 | SOUSSE | 100.00% |
| A | 5021 | CITE EL KHADHRA | 1 | 3 | MONASTIR | 100.00% |
| A | 5022 | MANZEL NOUR | 1 | 3 | MONASTIR | 100.00% |
| A | 6100 | ONES | 1 | 3 | SILIANA | 100.00% |
| A | 6100 | ONS | 1 | 3 | SILIANA | 100.00% |
| A | 1006 | BAB BHAR | 1 | 3 | TUNIS | 100.00% |
| A | 2015 | JARDINS DE CARTHAGE | 1 | 3 | TUNIS | 100.00% |
| A | 2046 | EL AOUINA | 1 | 2 | TUNIS | 100.00% |
| A | 4000 | ERRIADH | 1 | 2 | SOUSSE | 100.00% |
| A | 5000 | REBAT | 1 | 2 | MONASTIR | 100.00% |
| A | 8011 | MAAMOURA | 1 | 2 | NABEUL | 100.00% |
| A | 1000 | MONTFLEURY | 1 | 2 | TUNIS | 100.00% |
| A | 1000 | BELVEDERE | 1 | 2 | TUNIS | 100.00% |
| A | 2025 | KRAM | 1 | 2 | TUNIS | 100.00% |
| A | 1013 | EL MENZAH 9 A | 1 | 2 | TUNIS | 100.00% |
| A | 1141 | SMENJA | 1 | 2 | ZAGHOUAN | 100.00% |
| A | 4051 | SAHLOUL 3 | 1 | 2 | SOUSSE | 100.00% |
| A | 3000 | SAKIET EDDAIER | 1 | 2 | SFAX | 100.00% |
| A | 2037 | EL MENZAH 7 BIS | 1 | 2 | ARIANA | 100.00% |
| A | 7000 | JARZOUNA | 1 | 2 | BIZERTE | 100.00% |
| A | 8045 | GHARMANE | 1 | 2 | NABEUL | 100.00% |
| A | 8080 | EL GHERIS | 1 | 2 | NABEUL | 100.00% |
| A | 8011 | DAR CHAABEN | 1 | 2 | NABEUL | 100.00% |
| A | 3100 | SEBIKHA | 1 | 2 | KAIROUAN | 100.00% |
| A | 3110 | ESSBIKHA | 1 | 2 | KAIROUAN | 100.00% |
| A | 9014 | BAB BLED | 1 | 2 | BEJA | 100.00% |
| A | 2050 | ARIANA | 1 | 2 | ARIANA | 100.00% |
| A | 8000 | SIDI ACHOUR | 1 | 2 | NABEUL | 100.00% |
| A | 4000 | RIADH | 1 | 2 | SOUSSE | 100.00% |
| A | 4000 | CITE BOUHSINA | 1 | 2 | SOUSSE | 100.00% |
| A | 2091 | EL MENZAH 7 | 1 | 2 | ARIANA | 100.00% |
| A | 4000 | SOUISSE | 1 | 2 | SOUSSE | 100.00% |
| A | 1004 | EL MANZAH | 1 | 2 | ARIANA | 100.00% |
| A | 4024 | SOUSSE | 1 | 2 | SOUSSE | 100.00% |
| A | 3220 | GHOMRASSAN | 1 | 2 | TATAOUINE | 100.00% |
| A | 6000 | BLED | 1 | 2 | GABES | 100.00% |
| A | 4260 | CITE JELAILA | 1 | 2 | KEBILI | 100.00% |
| A | 4000 | SAHLOUL 3 | 1 | 2 | SOUSSE | 100.00% |
| A | 7110 | AIN EL HENCHIR | 1 | 2 | KEF | 100.00% |
| A | 5160 | TOUAHRA | 1 | 2 | MAHDIA | 100.00% |
| A | 5100 | EZAHRA | 1 | 2 | MAHDIA | 100.00% |
| A | 5010 | WARDANINE | 1 | 2 | MONASTIR | 100.00% |
| A | 5034 | CITE EL OMRANE | 1 | 2 | MONASTIR | 100.00% |
| A | 9115 | BIR EL AKERMA | 1 | 2 | SIDI BOUZID | 100.00% |
| A | 6100 | ZRIBA | 1 | 2 | SILIANA | 100.00% |
| A | 1009 | IBN SINA | 1 | 2 | TUNIS | 100.00% |
| A | 1059 | TUNIS EL HAFSIA | 1 | 2 | TUNIS | 100.00% |
| A | 2041 | EL MNIHLA | 1 | 2 | ARIANA | 100.00% |
| A | 6100 | KSAR HDID | 1 | 2 | SILIANA | 100.00% |
| A | 6140 | KESRA | 1 | 2 | SILIANA | 100.00% |
| A | 1007 | SIJOUMI | 1 | 2 | TUNIS | 100.00% |
| A | 2052 | EZZOHOUR | 1 | 2 | TUNIS | 100.00% |
| A | 1006 | EL HAFSIA | 1 | 2 | TUNIS | 100.00% |
| A | 3089 | SFAX | 1 | 2 | SFAX | 100.00% |
| A | 8044 | SIDI BOU ALI | 1 | 2 | NABEUL | 100.00% |
| A | 4023 | CITE ERIADH | 1 | 2 | SOUSSE | 100.00% |
| A | 4031 | CITÉ EZZOUHOUR | 1 | 2 | SOUSSE | 100.00% |
| A | 5000 | SOUSSE | 1 | 2 | SOUSSE | 100.00% |
| A | 7000 | RAS JEBAL | 1 | 2 | BIZERTE | 100.00% |
| A | 7022 | MATEUR | 1 | 2 | BIZERTE | 100.00% |
| A | 2080 | CITE GHAZELLA | 1 | 2 | ARIANA | 100.00% |
| A | 9121 | CEGDEL | 1 | 2 | SIDI BOUZID | 100.00% |
| A | 2100 | MDHILLA | 1 | 2 | GAFSA | 100.00% |
| A | 5089 | MONASTIR | 1 | 2 | MONASTIR | 100.00% |
| A | 5090 | MOKNINE | 1 | 2 | MONASTIR | 100.00% |
| A | 1110 | CITE NASSER | 1 | 2 | MANNOUBA | 100.00% |
| A | 8140 | CITE OUM KETHIR | 1 | 2 | JENDOUBA | 100.00% |
| A | 8070 | KLIBIA | 1 | 2 | NABEUL | 100.00% |
| A | 4000 | CITE ERRIADH | 1 | 2 | SOUSSE | 100.00% |
| A | 4054 | SAHLOUL1 | 1 | 2 | SOUSSE | 100.00% |
| A | 1053 | BERGES DU LAC 2 | 1 | 1 | TUNIS | 100.00% |
| A | 2032 | MNIHLA | 1 | 1 | ARIANA | 100.00% |
| A | 8069 | KELIBIA CHARGUIA | 1 | 1 | NABEUL | 100.00% |
| A | 2016 | EL YASMINA | 1 | 1 | TUNIS | 100.00% |
| A | 2083 | CITE GHAZELLE | 1 | 1 | TUNIS | 100.00% |
| A | 2026 | AMILCAR | 1 | 1 | TUNIS | 100.00% |
| A | 2052 | CITE EZZOUHOUR 2 | 1 | 1 | TUNIS | 100.00% |
| A | 2041 | NOGRA | 1 | 1 | ARIANA | 100.00% |
| A | 2052 | EZZOUHOUR 3 | 1 | 1 | TUNIS | 100.00% |
| A | 3200 | SMAR | 1 | 1 | TATAOUINE | 100.00% |
| A | 2075 | TUNIS | 1 | 1 | TUNIS | 100.00% |
| A | 2046 | AIN ZAGHUAN | 1 | 1 | TUNIS | 100.00% |
| A | 2023 | JEBAL JLOUD | 1 | 1 | TUNIS | 100.00% |
| A | 2070 | GAMARTH | 1 | 1 | GAMARTH | 100.00% |
| A | 2080 | CITE ENNASR | 1 | 1 | ARIANAOUS | 100.00% |
| A | 8011 | HAMMAMET | 1 | 1 | NABEUL | 100.00% |
| A | 2080 | LA GAZELLE | 1 | 1 | L'ARIANA | 100.00% |
| A | 3043 | SFAX | 1 | 1 | SFAX | 100.00% |
| A | 1009 | EL OUARDI | 1 | 1 | TUNIS | 100.00% |
| A | 2034 | ARIANA | 1 | 1 | ARIANA | 100.00% |
| A | 4000 | JAWHRA | 1 | 1 | SOUSSE | 100.00% |
| A | 8050 | BARRAKET ESSAHEL | 1 | 1 | NABEUL | 100.00% |
| A | 2070 | GHAMMART | 1 | 1 | TUNIS | 100.00% |
| A | 4195 | JERBA | 1 | 1 | MEDNINE | 100.00% |
| A | 6180 | BOUA RADA | 1 | 1 | SILIANA | 100.00% |
| A | 1000 | MEGRINE | 1 | 1 | TUNIS | 100.00% |
| A | 2052 | LE BARDO | 1 | 1 | TUNIS | 100.00% |
| A | 8023 | SOMMA | 1 | 1 | NABEUL | 100.00% |
| A | 4017 | HAMMAM SOUSSE | 1 | 1 | SOUSSE | 100.00% |
| A | 8045 | BIR EL JEDAY | 1 | 1 | NABEUL | 100.00% |
| A | 2045 | CITE ESSALAMA | 1 | 1 | TUNIS | 100.00% |
| A | 2089 | CARTHAGE | 1 | 1 | TUNIS | 100.00% |
| A | 5113 | EL AGBA | 1 | 1 | MANOUBA | 100.00% |
| A | 2045 | MARSA | 1 | 1 | TUNIS | 100.00% |
| A | 2037 | MANAR2 | 1 | 1 | ARIANA | 100.00% |
| A | 2018 | RADES | 1 | 1 | BEN AROUS | 100.00% |
| A | 2076 | LA MARSA OUEST | 1 | 1 | TUNIS | 100.00% |
| A | 1004 | EL OMRANE SUPERIEUR | 1 | 1 | TUNIS | 100.00% |
| A | 1009 | AVICENNE | 1 | 1 | TUNIS | 100.00% |
| A | 2052 | BEN AROUS | 1 | 1 | TUNIS | 100.00% |
| A | 1110 | ERIADH | 1 | 1 | MANNOUBA | 100.00% |
| A | 2022 | KALAAT EL ANDALOUS | 1 | 1 | ARIANA | 100.00% |
| A | 1153 | MORNAGUIA | 1 | 1 | MANNOUBA | 100.00% |
| A | 2083 | FOUCHANA | 1 | 1 | BEN AROUS | 100.00% |
| A | 1000 | SIDI HSSINE | 1 | 1 | TUNIS | 100.00% |
| A | 1110 | MORNAGGUIA | 1 | 1 | MANNOUBA | 100.00% |
| A | 1130 | TBORBA | 1 | 1 | MANOUBA | 100.00% |
| A | 1059 | SEJOUMI | 1 | 1 | SEJOUMI | 100.00% |
| A | 2045 | JARDINS DE CARTHAGE | 1 | 1 | TUNIS | 100.00% |
| A | 2010 | TBORBA | 1 | 1 | MANOUBA | 100.00% |
| A | 1142 | NOZHA | 1 | 1 | MANNOUBA | 100.00% |
| A | 1163 | NADHOUR | 1 | 1 | ZAGHOUANE | 100.00% |
| A | 1123 | BIR MCHERGA | 1 | 1 | ZAGHOUAN | 100.00% |
| A | 1095 | SIDI HSSIN | 1 | 1 | TUNIS | 100.00% |
| A | 1003 | EL KHADHRA | 1 | 1 | TUNIS | 100.00% |
| A | 3079 | HAI EL KHIRI | 1 | 1 | SFAX | 100.00% |
| A | 1001 | CHARGUIA | 1 | 1 | TUNIS | 100.00% |
| A | 7080 | MENZEL DJEMIL | 1 | 1 | BIZERTE | 100.00% |
| A | 1008 | RAS TABIA | 1 | 1 | TUNIS | 100.00% |
| A | 6000 | CITE EL MANSOURA | 1 | 1 | GABES | 100.00% |
| A | 9000 | BIZERTE | 1 | 1 | BIZERTE | 100.00% |
| A | 7000 | LA PECHERIE | 1 | 1 | BIZERTE | 100.00% |
| A | 8080 | AIREG SASSE | 1 | 1 | NABEUL | 100.00% |
| A | 8060 | SOMAA | 1 | 1 | NABEUL | 100.00% |
| A | 8024 | SOMAA | 1 | 1 | NABEUL | 100.00% |
| A | 8013 | DAR CHAABANE | 1 | 1 | NABEUL | 100.00% |
| A | 3160 | HAJEB AYOUN | 1 | 1 | KAIROUAN | 100.00% |
| A | 3100 | MENZEL MHIRI | 1 | 1 | KAIROEN | 100.00% |
| A | 4000 | CORNICHE | 1 | 1 | SOUSSE | 100.00% |
| A | 3100 | CHRARDA | 1 | 1 | KAIROUAN | 100.00% |
| A | 3110 | CHEBIKA | 1 | 1 | KAIROUAN | 100.00% |
| A | 6010 | RUE SAADA | 1 | 1 | GABES | 100.00% |
| A | 4000 | KALAA SGHIRA | 1 | 1 | SOUSSE | 100.00% |
| A | 8020 | RIADH | 1 | 1 | NABEUL | 100.00% |
| A | 3150 | ALA | 1 | 1 | KAIROUAN | 100.00% |
| A | 4192 | BEN GUERDANE | 1 | 1 | MEDENINE | 100.00% |
| A | 2056 | RAWED | 1 | 1 | ARIANA | 100.00% |
| A | 2092 | ELMANAR 2 | 1 | 1 | TUNIS | 100.00% |
| A | 2035 | LAOUINA | 1 | 1 | ARIANA | 100.00% |
| A | 2083 | JAAFER 2 | 1 | 1 | ARIANA | 100.00% |
| A | 9080 | GBOLLATE | 1 | 1 | BEJA | 100.00% |
| A | 1053 | JARDINS DU LAC | 1 | 1 | TUNIS | 100.00% |
| A | 8122 | CITE CNRPS | 1 | 1 | JENDOUBA | 100.00% |
| A | 2041 | CITE REPUBLIQUE | 1 | 1 | ARIANA | 100.00% |
| A | 2045 | CITE LES PALMERAIS | 1 | 1 | TUNIS | 100.00% |
| A | 1000 | SIDI HSSIN | 1 | 1 | TUNIS | 100.00% |
| A | 8111 | JENDOUBA | 1 | 1 | JENDOUBA | 100.00% |
| A | 1064 | AL INTILAKA | 1 | 1 | TUNIS | 100.00% |
| A | 8142 | JENDOUBA | 1 | 1 | JENDOUBA | 100.00% |
| A | 1270 | SEBIBA | 1 | 1 | KASSERINE | 100.00% |
| A | 1250 | KASRINE | 1 | 1 | KASRINE | 100.00% |
| A | 2010 | SIDI AMOR | 1 | 1 | MANNOUBA | 100.00% |
| A | 1200 | SBEITLA | 1 | 1 | KASSERINE | 100.00% |
| A | 7035 | CITE ETTAHRIR | 1 | 1 | BIZERTE | 100.00% |
| A | 2071 | MORNAGUIA | 1 | 1 | MANNOUBA | 100.00% |
| A | 1002 | KASRINE | 1 | 1 | TUNIS | 100.00% |
| A | 4030 | GRIMIT | 1 | 1 | SOUSSE | 100.00% |
| A | 4000 | TAFFELA | 1 | 1 | SOUSSE | 100.00% |
| A | 4000 | THRAYET | 1 | 1 | SOUSSE | 100.00% |
| A | 4054 | SAHLOUL3 | 1 | 1 | SOUSSE | 100.00% |
| A | 2078 | CITE KHALIL | 1 | 1 | TUNIS | 100.00% |
| A | 5080 | SOUSSE | 1 | 1 | SOUSSE | 100.00% |
| A | 4054 | KHEZAMA | 1 | 1 | SOUSSE | 100.00% |
| A | 4061 | KALAA KEBIRA | 1 | 1 | SOUSSE | 100.00% |
| A | 4051 | KHZEMA | 1 | 1 | SOUSSE | 100.00% |
| A | 4000 | KONDAR | 1 | 1 | SOUSSE | 100.00% |
| A | 4000 | ZAOUIA | 1 | 1 | SOUSSE | 100.00% |
| A | 4020 | HAMMAM SOUSSE | 1 | 1 | SOUSSE | 100.00% |
| A | 4022 | KALAA KEBIRA | 1 | 1 | SOUSSE | 100.00% |
| A | 4000 | CITE IBN KHALDOUN | 1 | 1 | SOUSSE | 100.00% |
| A | 4000 | CITE JAWHRA | 1 | 1 | SOUSSE | 100.00% |
| A | 2131 | GAFSA | 1 | 1 | GAFSA | 100.00% |
| A | 2130 | CITE IBNOU KHOULDOUN | 1 | 1 | GAFSA | 100.00% |
| A | 2210 | CITE AFH | 1 | 1 | TOZEUR | 100.00% |
| A | 2052 | EZZOUHOUR 1 | 1 | 1 | TUNIS | 100.00% |
| A | 6000 | MTORECH | 1 | 1 | GABES | 100.00% |
| A | 6000 | MATMATA | 1 | 1 | GABES | 100.00% |
| A | 4260 | DOUZE | 1 | 1 | GBELLI | 100.00% |
| A | 4191 | MEDENINE | 1 | 1 | MEDENINE | 100.00% |
| A | 3212 | OULED YAHYA | 1 | 1 | TATAOUINE | 100.00% |
| A | 6120 | LE KEF | 1 | 1 | LE KEF | 100.00% |
| A | 7131 | NEBEUR | 1 | 1 | KEF | 100.00% |
| A | 7100 | TEJROUINE | 1 | 1 | KEF | 100.00% |
| A | 5127 | MAHDIA | 1 | 1 | MAHDIA | 100.00% |
| A | 1091 | OMRAN SUP | 1 | 1 | OMRAN SU | 100.00% |
| A | 2090 | ARIANA | 1 | 1 | ARIANA | 100.00% |
| A | 5146 | KSOUR ESSAF | 1 | 1 | MAHDIA | 100.00% |
| A | 5193 | SIDI ALOUENE | 1 | 1 | MAHDIA | 100.00% |
| A | 1000 | TUNIS MEDINA | 1 | 1 | TUNIS | 100.00% |
| A | 5065 | MONASTIR | 1 | 1 | MONASTIR | 100.00% |
| A | 5010 | OUERDENINE | 1 | 1 | MONASTIR | 100.00% |
| A | 5000 | SKANESS | 1 | 1 | MONASTIR | 100.00% |
| A | 5020 | MENZEL KAMEL | 1 | 1 | MONASTIR | 100.00% |
| A | 5025 | BANNANE | 1 | 1 | MONASTIR | 100.00% |
| A | 5046 | MLICHET | 1 | 1 | MONASTIR | 100.00% |
| A | 9100 | SBZ OUEST | 1 | 1 | SIDI BOUZID | 100.00% |
| A | 6040 | GABES | 1 | 1 | GABES | 100.00% |
| A | 9132 | SIDI BOUZID | 1 | 1 | SIDI BOUZID | 100.00% |
| A | 2016 | CARTHAGE YASMINA | 1 | 1 | TUNIS | 100.00% |
| A | 6131 | SILIANA | 1 | 1 | SILIANA | 100.00% |
| A | 6180 | BARGOU | 1 | 1 | SELIANA | 100.00% |
| A | 6100 | MESKIA 2 | 1 | 1 | SILIANA | 100.00% |
| A | 2074 | MHAMDIA | 1 | 1 | TUNISIE | 100.00% |
| A | 4000 | HAMEM SOUSSE | 1 | 1 | SOUSSE | 100.00% |
| A | 3120 | SIDI AMARA | 1 | 1 | KAIROUAN | 100.00% |
| A | 2021 | CHABAOU | 1 | 1 | MANOUBA | 100.00% |
| A | 6100 | TUNIS | 1 | 1 | SILIANA | 100.00% |
| A | 6180 | BOUAARADA | 1 | 1 | SELIANA | 100.00% |
| A | 6100 | LAAROUSSA | 1 | 1 | SILIANA | 100.00% |
| A | 2035 | AIN ZAGHOUAN | 1 | 1 | ARIANA | 100.00% |
| A | 6100 | SILANA | 1 | 1 | SILIANA | 100.00% |
| A | 6150 | SILIANA | 1 | 1 | SILIANA | 100.00% |
| A | 6100 | RUE 18 JANVIER | 1 | 1 | SILIANA | 100.00% |
| A | 2091 | EL MENZAH | 1 | 1 | ARIANA | 100.00% |
| A | 1000 | SIDI HSINE | 1 | 1 | TUNIS | 100.00% |
| A | 2086 | CITE JEUNESSE | 1 | 1 | MANNOUBA | 100.00% |
| A | 2082 | CITE HIDHAB | 1 | 1 | BEN AROUS | 100.00% |
| A | 2076 | GAMMART | 1 | 1 | TUNIS | 100.00% |
| A | 1007 | MALLASSINE | 1 | 1 | TUNIS | 100.00% |
| A | 8060 | BENI KHIAR PLAGE | 1 | 1 | NABEUL | 100.00% |
| A | 1082 | ARIANA | 1 | 1 | ARIANA | 100.00% |
| A | 1001 | KHAZNADAR | 1 | 1 | TUNIS | 100.00% |
| A | 1000 | AOUINA | 1 | 1 | TUNIS | 100.00% |
| A | 2080 | CITE EL MOSTAKBEL | 1 | 1 | ARIANA | 100.00% |
| A | 2037 | MENZAH 6 | 1 | 1 | ARIANA | 100.00% |
| A | 1089 | ESSAIDA | 1 | 1 | TUNIS | 100.00% |
| A | 8025 | HAMMEM LAGHZEZ | 1 | 1 | NABEUL | 100.00% |
| A | 2068 | EL MOUROUJ 3 | 1 | 1 | BEN AROUS | 100.00% |
| A | 1009 | DJEBAL JELOUD | 1 | 1 | TUNIS | 100.00% |
| A | 2010 | TEBOURBA | 1 | 1 | LA MANOUBA | 100.00% |
| A | 2098 | TUNIS | 1 | 1 | BEN AROUS | 100.00% |
| A | 1143 | TEBOURBA | 1 | 1 | MANNOUBA | 100.00% |
| A | 3000 | SKHIRA | 1 | 1 | SFAX | 100.00% |
| A | 3053 | EL HENCHA | 1 | 1 | SFAX | 100.00% |
| A | 2037 | RIADH ENNASER 2 | 1 | 1 | ARIANA | 100.00% |
| A | 3000 | EL KHALIJ | 1 | 1 | SFAX | 100.00% |
| A | 3020 | MZL CHEKER | 1 | 1 | SFAX | 100.00% |
| A | 1002 | MOUROUJ 5 | 1 | 1 | BEN AROUS | 100.00% |
| A | 1142 | EL HAFSIA | 1 | 1 | TUNIS | 100.00% |
| A | 4000 | KODIET MALEK | 1 | 1 | SOUSSE | 100.00% |
| A | 4026 | SIDI EL HENI | 1 | 1 | SOUSSE | 100.00% |
| A | 4032 | NFIDHA | 1 | 1 | SOUSSE | 100.00% |
| A | 8010 | BOUFICHA | 1 | 1 | NABEUL | 100.00% |
| A | 4030 | SOUSSA | 1 | 1 | SOUSSE | 100.00% |
| A | 4071 | KHEZEMA | 1 | 1 | SOUSSE | 100.00% |
| A | 7034 | EL METLINE | 1 | 1 | BIZERTE | 100.00% |
| A | 7020 | BAZINA | 1 | 1 | BIZERTE | 100.00% |
| A | 7050 | TUNIS | 1 | 1 | BIZERTE | 100.00% |
| A | 7022 | BORJ EL ADOUANI | 1 | 1 | BIZERTE | 100.00% |
| A | 7029 | LA PECHERIE | 1 | 1 | BIZERTE | 100.00% |
| A | 7024 | SOUNINE | 1 | 1 | BIZERTE | 100.00% |
| A | 4100 | BENI KHADECHE | 1 | 1 | MEDENINE | 100.00% |
| A | 4180 | TAOURIT | 1 | 1 | MEDENINE | 100.00% |
| A | 6052 | RUE TAHER HADED | 1 | 1 | GABES | 100.00% |
| A | 6070 | BOU DHAFER | 1 | 1 | GABES | 100.00% |
| A | 6012 | SIDI BOULBA | 1 | 1 | GABES | 100.00% |
| A | 6045 | MARETH | 1 | 1 | GABES | 100.00% |
| A | 6052 | RUE MAKA | 1 | 1 | GABES | 100.00% |
| A | 2046 | AIN ZAGHOUANE NORD | 1 | 1 | LA MARSA | 100.00% |
| A | 1074 | EL MOUROUJ 3 | 1 | 1 | TUNIS | 100.00% |
| A | 1082 | CITE EL KHADHRA | 1 | 1 | TUNIS | 100.00% |
| A | 7061 | BIZERTE | 1 | 1 | BIZERTE | 100.00% |
| A | 8060 | PLAGE DE BENI KHIAR | 1 | 1 | BENI KHIAR | 100.00% |
| A | 8050 | SIDI JEDIDI | 1 | 1 | NABEUL | 100.00% |
| A | 8060 | BNI KHIAR | 1 | 1 | NABEUL | 100.00% |
| A | 8031 | GROMBALIA | 1 | 1 | NABEUL | 100.00% |
| A | 8000 | EL KNAIES | 1 | 1 | NABEUL | 100.00% |
| A | 3253 | DHIBA | 1 | 1 | DHIBA | 100.00% |
| A | 3200 | REMADA | 1 | 1 | TATAOUINE | 100.00% |
| A | 5012 | SAHLIN | 1 | 1 | MONASTIR | 100.00% |
| A | 5061 | SIDI AMER | 1 | 1 | MONASTIR | 100.00% |
| A | 5015 | BOUHAJER | 1 | 1 | MONASTIR | 100.00% |
| A | 5013 | MANZEL KAMEL | 1 | 1 | MONASTIR | 100.00% |
| A | 5031 | KSAR HELAL | 1 | 1 | MONASTIR | 100.00% |
| A | 1125 | RADES | 1 | 1 | BEN AROUS | 100.00% |
| A | 1009 | EL OUERDIA 3 | 1 | 1 | TUNIS | 100.00% |
| A | 2034 | HAMMAM LIF | 1 | 1 | BEN AROUS | 100.00% |
| A | 2074 | ELMOUROUJ 1 | 1 | 1 | BEN AROUS | 100.00% |
| A | 2113 | BEN AROUS | 1 | 1 | BEN AROUS | 100.00% |
| A | 2080 | FOUCHANA | 1 | 1 | BEN AROUS | 100.00% |
| A | 2074 | EL MANARA | 1 | 1 | BEN AROUS | 100.00% |
| A | 1000 | CITE BEN YOUNES | 1 | 1 | TUNIS | 100.00% |
| A | 1110 | MORNEGUIA | 1 | 1 | MANNOUBA | 100.00% |
| A | 1142 | BORJ AMRI | 1 | 1 | MANNOUBA | 100.00% |
| A | 2094 | JARDINS MENZAH | 1 | 1 | ARIANA | 100.00% |
| A | 2014 | ETTADHAMEN | 1 | 1 | ARIANA | 100.00% |
| A | 2035 | CHARGUIA2 | 1 | 1 | ARIANA | 100.00% |
| A | 1000 | ELAGBA | 1 | 1 | TUNIS | 100.00% |
| A | 2130 | ROUTE DE TOZEUR | 1 | 1 | GAFSA | 100.00% |
| A | 3132 | SEBIKHA | 1 | 1 | KAIROUAN | 100.00% |
| A | 1002 | KAIROUAN | 1 | 1 | KAIROUAN | 100.00% |
| A | 2096 | MORNAG | 1 | 1 | BEN AROUS | 100.00% |
| A | 1009 | BEN AROUS | 1 | 1 | BEN AROUS | 100.00% |
| A | 8136 | AIN DRAHEM | 1 | 1 | JANDOUBA | 100.00% |
| A | 8170 | TUNIS | 1 | 1 | JENDOUBA | 100.00% |
| A | 7036 | BIZERTE | 1 | 1 | BIZERTE | 100.00% |
| A | 7032 | LOUATA | 1 | 1 | BIZERTE | 100.00% |
| A | 1233 | KASSERINE | 1 | 1 | KASSERINE | 100.00% |
| A | 5140 | CITE 9 AVRIL | 1 | 1 | MAHDIA | 100.00% |
| A | 2000 | MAHDIA | 1 | 1 | MAHDIA | 100.00% |
| A | 5199 | HIBOUN | 1 | 1 | MAHDIA | 100.00% |
| A | 2092 | MENZAH6 | 1 | 1 | TUNIS | 100.00% |
| A | 4063 | KALAA KEBIRA | 1 | 1 | SOUSSE | 100.00% |
| A | 2045 | BORJ LOUZIR | 1 | 1 | ARIANA | 100.00% |
| A | 2041 | CITE IBN KHALDOUN | 1 | 1 | TUNIS | 100.00% |
| A | 2082 | SEJOUMI | 1 | 1 | BEN AROUS | 100.00% |
| A | 3000 | EL HAJEB | 1 | 1 | SFAX | 100.00% |
| A | 3000 | CITE EL HABIB | 1 | 1 | SFAX | 100.00% |
| A | 3000 | TYNA | 1 | 1 | SFAX | 100.00% |
| A | 2086 | DOUAR HICHR | 1 | 1 | MANNOUBA | 100.00% |
| A | 9115 | REGUEB | 1 | 1 | SIDI BOUZID | 100.00% |
| A | 4180 | HOUMT SOUK JERBA | 1 | 1 | MEDENINE | 100.00% |
| A | 6052 | RUE HABIB BOURGUIBA | 1 | 1 | GABES | 100.00% |
| A | 4159 | BENI KHADECHE | 1 | 1 | MEDENINE | 100.00% |
| A | 2076 | MARSA SAFSAF | 1 | 1 | TUNIS | 100.00% |

## 7.2 Candidate Type B: code_postal -> localite + gouvernorat

| candidate_type | code_postal | candidate_rows | known_pair_rows | recommended_localite | recommended_gouvernorat | dominance_percentage |
| --- | --- | --- | --- | --- | --- | --- |
| B | 7000 | 3728 | 6271 | BIZERTE | BIZERTE | 96.01% |
| B | 2010 | 1988 | 4244 | LA MANNOUBA | MANNOUBA | 97.71% |
| B | 2013 | 1764 | 2789 | BEN AROUS | BEN AROUS | 98.06% |
| B | 4070 | 1677 | 2359 | MSAKEN | SOUSSE | 98.09% |
| B | 4160 | 1442 | 2428 | BEN GUERDANE | MEDENINE | 98.48% |
| B | 8100 | 1232 | 2537 | JENDOUBA | JENDOUBA | 96.06% |
| B | 8060 | 1223 | 690 | BENI KHIAR | NABEUL | 96.23% |
| B | 7050 | 1094 | 1908 | MENZEL BOURGUIBA | BIZERTE | 95.65% |
| B | 8050 | 1015 | 2857 | HAMMAMET | NABEUL | 95.87% |
| B | 1200 | 974 | 1867 | KASSERINE | KASSERINE | 96.14% |
| B | 1053 | 798 | 3055 | BERGE DU LAC | TUNIS | 95.91% |
| B | 5180 | 754 | 1115 | KSOUR ESSAF | MAHDIA | 97.85% |
| B | 4011 | 700 | 857 | HAMMAM SOUSSE | SOUSSE | 95.33% |
| B | 7070 | 684 | 920 | RAS JEBEL | BIZERTE | 96.41% |
| B | 9000 | 678 | 2244 | BEJA | BEJA | 95.10% |
| B | 3021 | 657 | 2120 | SAKIET EZZIT | SFAX | 99.43% |
| B | 6020 | 586 | 815 | EL HAMMA | GABES | 99.75% |
| B | 5190 | 585 | 715 | SIDI ALOUENE | MAHDIA | 96.50% |
| B | 5040 | 553 | 602 | ZERAMDINE | MONASTIR | 96.68% |
| B | 2063 | 481 | 1288 | NOUVELLE MEDINA | BEN AROUS | 98.45% |
| B | 2200 | 440 | 793 | TOZEUR | TOZEUR | 98.87% |
| B | 2240 | 436 | 546 | NEFTA | TOZEUR | 96.89% |
| B | 1001 | 426 | 1680 | REPUBLIQUE | TUNIS | 96.85% |
| B | 8110 | 326 | 771 | TABARKA | JENDOUBA | 97.28% |
| B | 8090 | 302 | 1123 | KELIBIA | NABEUL | 97.33% |
| B | 8042 | 237 | 705 | BIR BOUREGBA | NABEUL | 95.18% |
| B | 7015 | 221 | 235 | RAFRAF | BIZERTE | 96.17% |
| B | 8130 | 196 | 377 | AIN DRAHAM | JENDOUBA | 97.61% |
| B | 8024 | 186 | 352 | TAZARKA | NABEUL | 98.01% |
| B | 8021 | 165 | 348 | BENI KHALLED | NABEUL | 97.70% |
| B | 2096 | 164 | 714 | EL YASMINETTE | BEN AROUS | 97.90% |
| B | 2030 | 144 | 1 | 24 RUE 42878 2030 SEJOUMI | 24 RUE 42878 | 100.00% |
| B | 7014 | 131 | 232 | EL AOUSJA | BIZERTE | 95.69% |
| B | 1057 | 126 | 813 | GAMMART | TUNIS | 97.42% |
| B | 2066 | 117 | 607 | IBN SINA | TUNIS | 98.19% |
| B | 5013 | 114 | 377 | MENZEL KAMEL | MONASTIR | 98.94% |
| B | 2026 | 107 | 242 | SIDI BOUSAID | TUNIS | 95.04% |
| B | 1013 | 104 | 307 | EL MENZAH 9 | TUNIS | 96.42% |
| B | 1064 | 99 | 284 | CITE EL INTILAKA | TUNIS | 95.07% |
| B | 2223 | 96 | 181 | HEZOUA | TOZEUR | 100.00% |
| B | 1074 | 95 | 326 | EL MOUROUJ 2 | TUNIS | 97.24% |
| B | 5014 | 92 | 227 | BENI HASSEN | MONASTIR | 96.92% |
| B | 1111 | 90 | 153 | JEBEL EL OUST | ZAGHOUAN | 95.42% |
| B | 1091 | 85 | 468 | EL OMRANE SUPERIEUR | TUNIS | 97.86% |
| B | 4013 | 73 | 190 | MESSADINE | SOUSSE | 95.26% |
| B | 8115 | 72 | 135 | OUED MLIZ | JENDOUBA | 97.78% |
| B | 4110 | 68 | 261 | BENI KHEDACHE | MEDENINE | 95.02% |
| B | 7020 | 68 | 104 | JOUMINE | BIZERTE | 98.08% |
| B | 1068 | 61 | 170 | ROMMANA | TUNIS | 96.47% |
| B | 5023 | 58 | 159 | TOUZA | MONASTIR | 100.00% |
| B | 5071 | 56 | 143 | AMIRAT EL HOJJEJ | MONASTIR | 99.30% |
| B | 3012 | 56 | 82 | MERKEZ SAHNOUN | SFAX | 95.12% |
| B | 8032 | 55 | 189 | SIDI JEDIDI | NABEUL | 99.47% |
| B | 4144 | 55 | 176 | EL MOUENSA | MEDENINE | 98.30% |
| B | 5033 | 55 | 116 | MENZEL HAYET | MONASTIR | 96.55% |
| B | 5024 | 55 | 107 | MENZEL FERSI | MONASTIR | 99.07% |
| B | 9183 | 54 | 7 | EL ABBADETTE | SIDI BOUZID | 100.00% |
| B | 2084 | 53 | 406 | BORJ CEDRIA | BEN AROUS | 97.29% |
| B | 4214 | 52 | 53 | JEMNA | KEBILI | 98.11% |
| B | 1164 | 51 | 369 | HAMMAM CHATT | BEN AROUS | 98.92% |
| B | 5146 | 49 | 63 | RECHERCHA | MAHDIA | 96.83% |
| B | 9122 | 48 | 211 | CEBBALA | SIDI BOUZID | 96.68% |
| B | 2224 | 48 | 58 | EL MAHASSEN | TOZEUR | 96.55% |
| B | 7012 | 46 | 160 | BAZINA | BIZERTE | 100.00% |
| B | 1240 | 46 | 85 | FERIANA | KASSERINE | 95.29% |
| B | 5151 | 46 | 50 | ZORDA | MAHDIA | 96.00% |
| B | 4231 | 46 | 29 | BECHRI | KEBILI | 100.00% |
| B | 7025 | 44 | 57 | SOUNINE | BIZERTE | 100.00% |
| B | 3027 | 40 | 159 | SFAX EL JADIDA | SFAX | 97.48% |
| B | 2262 | 40 | 34 | DGHOUMES | TOZEUR | 100.00% |
| B | 2043 | 38 | 273 | BEN AROUS SUD | BEN AROUS | 95.60% |
| B | 2055 | 38 | 154 | BIR EL BEY | BEN AROUS | 96.10% |
| B | 6013 | 38 | 121 | SOMBAT | GABES | 98.35% |
| B | 3129 | 38 | 63 | CITE EL HAJJAM | KAIROUAN | 100.00% |
| B | 5054 | 35 | 104 | AMIRAT TOUAZRA | MONASTIR | 100.00% |
| B | 1121 | 34 | 135 | EL MAGREN | ZAGHOUAN | 98.52% |
| B | 4130 | 34 | 87 | MEDENINE EL JEDIDA | MEDENINE | 100.00% |
| B | 4223 | 34 | 43 | FATNASSA | KEBILI | 97.67% |
| B | 7151 | 33 | 23 | MENZEL SALEM | KEF | 100.00% |
| B | 5026 | 33 | 22 | GHENADA | MONASTIR | 95.45% |
| B | 1116 | 32 | 148 | MORNAGUIA 20 MARS | MANNOUBA | 95.95% |
| B | 5045 | 32 | 80 | MZAOUGHA | MONASTIR | 96.25% |
| B | 4115 | 32 | 70 | MELLITA JERBA | MEDENINE | 95.71% |
| B | 4114 | 32 | 61 | ERRAJA | MEDENINE | 96.72% |
| B | 4235 | 31 | 32 | TOMBAR | KEBILI | 96.88% |
| B | 3062 | 29 | 67 | SIDI ABBES | SFAX | 95.52% |
| B | 4212 | 29 | 32 | OUM SOMAA | KEBILI | 100.00% |
| B | 4211 | 29 | 14 | RAHMET | KEBILI | 100.00% |
| B | 8053 | 28 | 50 | GARAAT SASSI | NABEUL | 100.00% |
| B | 4016 | 28 | 50 | BENI KALTHOUM | SOUSSE | 98.00% |
| B | 8033 | 27 | 59 | DIAR EL HOJJEJ | NABEUL | 98.31% |
| B | 3065 | 27 | 20 | SFAX PORT | SFAX | 100.00% |
| B | 4236 | 27 | 16 | BOU ABDALLAH | KEBILI | 100.00% |
| B | 4033 | 26 | 71 | MOUREDDINE | SOUSSE | 95.77% |
| B | 4242 | 26 | 40 | JANAOURA | KEBILI | 100.00% |
| B | 5044 | 24 | 83 | SIDI BANNOUR | MONASTIR | 98.80% |
| B | 6016 | 24 | 61 | ARRAM | GABES | 98.36% |
| B | 8015 | 24 | 36 | MENZEL HORR | NABEUL | 100.00% |
| B | 3031 | 24 | 35 | MERKEZ BOUACIDA | SFAX | 100.00% |
| B | 4232 | 24 | 20 | TENBIB | KEBILI | 100.00% |
| B | 1073 | 23 | 188 | MONTPLAISIR | TUNIS | 98.40% |
| B | 7041 | 23 | 86 | LOUATA | BIZERTE | 97.67% |
| B | 5121 | 23 | 69 | REJICHE | MAHDIA | 98.55% |
| B | 4111 | 22 | 62 | OUM ETTAMAR | MEDENINE | 100.00% |
| B | 4243 | 22 | 17 | BLIDETTE | KEBILI | 100.00% |
| B | 5053 | 21 | 79 | AMIRAT EL FEHOUL | MONASTIR | 98.73% |
| B | 5032 | 21 | 47 | MAZDOUR | MONASTIR | 97.87% |
| B | 2239 | 21 | 28 | CHETAOUA SAHRAOUI | TOZEUR | 96.43% |
| B | 4210 | 21 | 23 | REJIME MAATOUG | KEBILI | 95.65% |
| B | 4121 | 20 | 93 | KOUTINE | MEDENINE | 100.00% |
| B | 4233 | 20 | 19 | RABTA | KEBILI | 100.00% |
| B | 4213 | 20 | 16 | ZAOUIET EL ANES | KEBILI | 100.00% |
| B | 1155 | 19 | 122 | BIR HALIMA | ZAGHOUAN | 95.08% |
| B | 6092 | 19 | 59 | BECHIMA | GABES | 98.31% |
| B | 3131 | 18 | 90 | KAIROUAN SUD | KAIROUAN | 98.89% |
| B | 6026 | 18 | 75 | ZARAT | GABES | 98.67% |
| B | 6051 | 18 | 26 | NAHAL | GABES | 96.15% |
| B | 2012 | 18 | 21 | EL HABIBIA | MANNOUBA | 95.24% |
| B | 4131 | 17 | 81 | HASSI AMOR | MEDENINE | 97.53% |
| B | 6055 | 17 | 70 | DEKHILET TOUJANE | GABES | 100.00% |
| B | 3063 | 16 | 81 | EL KHALIJ | SFAX | 98.77% |
| B | 8035 | 16 | 52 | AZMOUR | NABEUL | 96.15% |
| B | 4263 | 16 | 14 | JERSINE | KEBILI | 100.00% |
| B | 5125 | 15 | 112 | BOU HELAL SUD | MAHDIA | 96.43% |
| B | 4124 | 15 | 54 | EL HICHEM | MEDENINE | 98.15% |
| B | 3099 | 15 | 42 | EL BOUSTEN | SFAX | 95.24% |
| B | 3071 | 15 | 38 | OUED CHAABOUNI | SFAX | 97.37% |
| B | 7031 | 15 | 38 | TAMRA | BIZERTE | 100.00% |
| B | 2044 | 15 | 37 | ERRISSALA | BEN AROUS | 97.30% |
| B | 1231 | 15 | 9 | SIDI SHIL | KASSERINE | 100.00% |
| B | 4194 | 14 | 54 | HAMADI EL GUEBLI | MEDENINE | 100.00% |
| B | 5099 | 14 | 46 | LAMTA | MONASTIR | 97.83% |
| B | 6095 | 14 | 25 | CHENCHOU | GABES | 100.00% |
| B | 4237 | 14 | 14 | TELMINE | KEBILI | 100.00% |
| B | 1075 | 13 | 82 | BAB EL KHADRA | TUNIS | 95.12% |
| B | 3272 | 13 | 68 | EZZAHRA TATAOUINE | TATAOUINE | 98.53% |
| B | 5036 | 13 | 35 | MENZEL HARB | MONASTIR | 97.14% |
| B | 4123 | 13 | 34 | OUALEGH | MEDENINE | 100.00% |
| B | 3037 | 13 | 32 | GARGOUR | SFAX | 100.00% |
| B | 3213 | 12 | 69 | KSAR OUN | TATAOUINE | 98.55% |
| B | 7063 | 12 | 63 | UTIQUE NOUVELLE | BIZERTE | 96.83% |
| B | 8055 | 12 | 53 | DAR ALLOUCHE | NABEUL | 96.23% |
| B | 3074 | 12 | 50 | EL AOUABED | SFAX | 96.00% |
| B | 3072 | 12 | 48 | MERKEZ CHAKER | SFAX | 95.83% |
| B | 3023 | 12 | 27 | OUED RMAL | SFAX | 96.30% |
| B | 5017 | 12 | 26 | EL HEDADRA | MONASTIR | 100.00% |
| B | 3114 | 12 | 25 | MENZEL MHIRI | KAIROUAN | 96.00% |
| B | 8043 | 12 | 24 | BOU JERIDA | NABEUL | 100.00% |
| B | 3293 | 11 | 82 | ROGBA | TATAOUINE | 97.56% |
| B | 4141 | 11 | 69 | BOU GHRARA | MEDENINE | 98.55% |
| B | 4133 | 11 | 37 | ROBBANA | MEDENINE | 97.30% |
| B | 3093 | 11 | 32 | MERKEZ OUALI | SFAX | 96.88% |
| B | 4224 | 11 | 27 | BAZMA | KEBILI | 100.00% |
| B | 2263 | 10 | 45 | BOU HELAL | TOZEUR | 97.78% |
| B | 4134 | 10 | 40 | CHAMMAKH | MEDENINE | 97.50% |
| B | 3067 | 10 | 36 | MERKEZ LAJMI | SFAX | 97.22% |
| B | 8052 | 10 | 33 | NIANOU | NABEUL | 96.97% |
| B | 4156 | 10 | 27 | GHIZEN | MEDENINE | 100.00% |
| B | 8041 | 10 | 26 | KORBOUS | NABEUL | 100.00% |
| B | 7043 | 10 | 23 | BACH HAMBA | BIZERTE | 95.65% |
| B | 6022 | 10 | 19 | EL MDOU | GABES | 100.00% |
| B | 5126 | 9 | 59 | SALAKTA | MAHDIA | 98.31% |
| B | 1193 | 9 | 48 | BIR MCHERGA GARE | ZAGHOUAN | 100.00% |
| B | 3214 | 9 | 37 | TLELET | TATAOUINE | 100.00% |
| B | 5141 | 9 | 22 | CHIBA | MAHDIA | 100.00% |
| B | 3035 | 9 | 20 | EL ATTAYA | SFAX | 100.00% |
| B | 5041 | 9 | 20 | MENZEL KHIR | MONASTIR | 95.00% |
| B | 3198 | 9 | 18 | CITE TABENE | KAIROUAN | 100.00% |
| B | 8034 | 9 | 12 | LEBNA | NABEUL | 100.00% |
| B | 6024 | 9 | 12 | NOUVELLE ZRAOUA | GABES | 100.00% |
| B | 4166 | 9 | 11 | OUED ZBIB | MEDENINE | 100.00% |
| B | 3262 | 8 | 124 | BENI MEHIRA | TATAOUINE | 99.19% |
| B | 3252 | 8 | 76 | MAZTOURIA | TATAOUINE | 97.37% |
| B | 4174 | 8 | 60 | HASSI JERBI | MEDENINE | 100.00% |
| B | 3078 | 8 | 47 | EL HAJEB | SFAX | 97.87% |
| B | 8099 | 8 | 31 | ZAOUIET JEDIDI | NABEUL | 96.77% |
| B | 5030 | 8 | 2 | JEMMAL KHEIREDDINE | MONASTIR | 100.00% |
| B | 1153 | 7 | 57 | EL FEJJA | MANNOUBA | 98.25% |
| B | 6027 | 7 | 48 | BOU ATTOUCHE | GABES | 100.00% |
| B | 3094 | 7 | 30 | CITE BOURGUIBA | SFAX | 96.67% |
| B | 8022 | 7 | 29 | BELLI | NABEUL | 96.55% |
| B | 5043 | 7 | 25 | BIR TAIEB | MONASTIR | 100.00% |
| B | 3039 | 7 | 18 | CAID MHAMED | SFAX | 100.00% |
| B | 4261 | 7 | 17 | ZAAFRANE | KEBILI | 100.00% |
| B | 4112 | 7 | 14 | OUERJIJENE | MEDENINE | 100.00% |
| B | 1211 | 7 | 5 | BOU LAHNECH | KASSERINE | 100.00% |
| B | 4294 | 7 | 3 | SAIDANE | KEBILI | 100.00% |
| B | 4164 | 6 | 29 | GRIBIS | MEDENINE | 100.00% |
| B | 7036 | 6 | 27 | TESKRAYA | BIZERTE | 96.30% |
| B | 4190 | 6 | 23 | SIDI ZAIED | MEDENINE | 100.00% |
| B | 3145 | 6 | 14 | OULED FARJALLAH | KAIROUAN | 100.00% |
| B | 3154 | 6 | 13 | MESSIOUTA | KAIROUAN | 100.00% |
| B | 2124 | 6 | 10 | CITE ESSOUROUR | GAFSA | 100.00% |
| B | 5154 | 6 | 10 | MEHARZA 18 | MAHDIA | 100.00% |
| B | 4132 | 6 | 8 | HALG JEMAL | MEDENINE | 100.00% |
| B | 1216 | 5 | 41 | EL AYOUN | KASSERINE | 100.00% |
| B | 1112 | 5 | 27 | JERADOU | ZAGHOUAN | 100.00% |
| B | 3073 | 5 | 15 | SBIH | SFAX | 100.00% |
| B | 4122 | 5 | 14 | KSAR EL JIRA | MEDENINE | 100.00% |
| B | 3014 | 5 | 10 | BOU THADI | SFAX | 100.00% |
| B | 7153 | 5 | 9 | JAZZA | KEF | 100.00% |
| B | 5062 | 5 | 9 | AMIRAT HATEM | MONASTIR | 100.00% |
| B | 6015 | 5 | 4 | AYOUNE EZZERKINE | GABES | 100.00% |
| B | 4153 | 5 | 4 | RAS JEDIR | MEDENINE | 100.00% |
| B | 7135 | 5 | 4 | AIN SINAN | KEF | 100.00% |
| B | 6099 | 5 | 4 | GABES EL HIDAYA | GABES | 100.00% |
| B | 4045 | 5 | 2 | ESSAD NORD | SOUSSE | 100.00% |
| B | 7071 | 4 | 89 | BIZERTE HACHED | BIZERTE | 98.88% |
| B | 1019 | 4 | 41 | BAB BNET | TUNIS | 97.56% |
| B | 8117 | 4 | 31 | BELLARIGIA | JENDOUBA | 96.77% |
| B | 3143 | 4 | 28 | AIN EL KHAZZAZIA | KAIROUAN | 96.43% |
| B | 4195 | 4 | 23 | GUECHIINE | MEDENINE | 95.65% |
| B | 3032 | 4 | 21 | MERKEZ DEROUICHE | SFAX | 100.00% |
| B | 3261 | 4 | 21 | KSAR EL HEDADA | TATAOUINE | 95.24% |
| B | 3251 | 4 | 17 | KSAR EL MOURABTINE | TATAOUINE | 100.00% |
| B | 7116 | 4 | 16 | BAHRA | KEF | 100.00% |
| B | 8161 | 4 | 14 | OUERGUECH | JENDOUBA | 100.00% |
| B | 5135 | 4 | 14 | NEFFATIA | MAHDIA | 100.00% |
| B | 4154 | 4 | 13 | EL GHRABATE | MEDENINE | 100.00% |
| B | 3235 | 4 | 12 | OUED EL KHIL | TATAOUINE | 100.00% |
| B | 3033 | 4 | 11 | BIR SALAH | SFAX | 100.00% |
| B | 2169 | 4 | 9 | ERRAGOUBA | GAFSA | 100.00% |
| B | 8114 | 4 | 7 | BENI MTIR | JENDOUBA | 100.00% |
| B | 2133 | 4 | 5 | GAFSA CITE DES JEUNES | GAFSA | 100.00% |
| B | 8091 | 4 | 4 | ERRAHMA | NABEUL | 100.00% |
| B | 7132 | 4 | 3 | MAHJOUBA | KEF | 100.00% |
| B | 9083 | 4 | 2 | GRAME | BEJA | 100.00% |
| B | 3079 | 4 | 1 | HAI EL KHIRI | SFAX | 100.00% |
| B | 4193 | 3 | 43 | JEMILA | MEDENINE | 95.35% |
| B | 4059 | 3 | 29 | SOUSSE CORNICHE | SOUSSE | 100.00% |
| B | 3059 | 3 | 25 | EL KHAZZANETTE | SFAX | 100.00% |
| B | 6060 | 3 | 25 | EL HAMMA SUD | GABES | 96.00% |
| B | 7027 | 3 | 17 | METHLINE | BIZERTE | 100.00% |
| B | 6062 | 3 | 16 | BENI GHILOUF | GABES | 100.00% |
| B | 5117 | 3 | 15 | OULED JABALLAH | MAHDIA | 100.00% |
| B | 7141 | 3 | 14 | TELL GHOUZLANE | KEF | 100.00% |
| B | 8063 | 3 | 13 | BOU CHARRAY | NABEUL | 100.00% |
| B | 9011 | 3 | 12 | TABABA | BEJA | 100.00% |
| B | 3075 | 3 | 10 | MERKEZ SGHAR | SFAX | 100.00% |
| B | 3056 | 3 | 10 | OULED BOUSMIR | SFAX | 100.00% |
| B | 3222 | 3 | 9 | CHENINI | TATAOUINE | 100.00% |
| B | 3025 | 3 | 8 | OULED KACEM | SFAX | 100.00% |
| B | 3092 | 3 | 8 | BOU JARBOU | SFAX | 100.00% |
| B | 4062 | 3 | 6 | KALAA EL KEBIRA KSAR | SOUSSE | 100.00% |
| B | 2142 | 3 | 5 | KEF DERBI | GAFSA | 100.00% |
| B | 9024 | 3 | 4 | TOUKABEUR | BEJA | 100.00% |
| B | 7111 | 3 | 4 | OUED MELLEGUE | KEF | 100.00% |
| B | 5133 | 3 | 4 | CHAHDA | MAHDIA | 100.00% |
| B | 4137 | 3 | 3 | ZARZIS ZONE FRANCHE | MEDENINE | 100.00% |
| B | 3153 | 3 | 3 | EL MSAID | KAIROUAN | 100.00% |
| B | 9172 | 3 | 3 | GOUBRAR | SIDI BOUZID | 100.00% |
| B | 2195 | 3 | 3 | ALIM | GAFSA | 100.00% |
| B | 4273 | 3 | 2 | STAFTIMI | KEBILI | 100.00% |
| B | 2019 | 3 | 1 | LE BARDO | TUNIS | 100.00% |
| B | 3112 | 3 | 1 | BEN SALEM | KAIROUAN | 100.00% |
| B | 2068 | 3 | 1 | EL MOUROUJ 3 | BEN AROUS | 100.00% |
| B | 3242 | 2 | 33 | KSAR DEBAB | TATAOUINE | 100.00% |
| B | 4095 | 2 | 25 | AIN MEDHEKER | SOUSSE | 100.00% |
| B | 1215 | 2 | 21 | THELEPTE | KASSERINE | 95.24% |
| B | 9052 | 2 | 20 | HAMMAM SAYALA | BEJA | 95.00% |
| B | 2161 | 2 | 20 | MOULARES GARE | GAFSA | 100.00% |
| B | 3066 | 2 | 16 | ESSAADI | SFAX | 100.00% |
| B | 3091 | 2 | 15 | SIDI SALAH | SFAX | 100.00% |
| B | 3282 | 2 | 15 | KSAR OULED SOLTAN | TATAOUINE | 100.00% |
| B | 1069 | 2 | 13 | HABIB THAMEUR | TUNIS | 100.00% |
| B | 8084 | 2 | 13 | TURKI | NABEUL | 100.00% |
| B | 3085 | 2 | 12 | OUM CHOUCHA | SFAX | 100.00% |
| B | 4127 | 2 | 12 | MEDENINE PERSEVERANCE | MEDENINE | 100.00% |
| B | 3284 | 2 | 9 | BIR THLATHINE | TATAOUINE | 100.00% |
| B | 5066 | 2 | 9 | SOUKRINE | MONASTIR | 100.00% |
| B | 3171 | 2 | 8 | EL KABBARA | KAIROUAN | 100.00% |
| B | 9159 | 2 | 8 | ESSALAMA | SIDI BOUZID | 100.00% |
| B | 5052 | 2 | 8 | BOU OTHMANE | MONASTIR | 100.00% |
| B | 9169 | 2 | 7 | OULED MNASSER | SIDI BOUZID | 100.00% |
| B | 6054 | 2 | 6 | TAMEZRAT | GABES | 100.00% |
| B | 8064 | 2 | 6 | SKALBA | NABEUL | 100.00% |
| B | 8054 | 2 | 6 | EL OUEDIANE | NABEUL | 100.00% |
| B | 4082 | 2 | 6 | SIDI KHELIFA | SOUSSE | 100.00% |
| B | 3271 | 2 | 5 | GUERMESSA | TATAOUINE | 100.00% |
| B | 1271 | 2 | 5 | AIN KHEMAISSIA | KASSERINE | 100.00% |
| B | 8083 | 2 | 3 | RAININE | NABEUL | 100.00% |
| B | 1251 | 2 | 3 | ECHRAYA | KASSERINE | 100.00% |
| B | 5092 | 2 | 3 | EL BEHIRA | MONASTIR | 100.00% |
| B | 7002 | 2 | 3 | CITE MILITAIRE | BIZERTE | 100.00% |
| B | 4199 | 2 | 3 | DAR JERBA | MEDENINE | 100.00% |
| B | 3195 | 2 | 2 | SIDI MESSAOUD | KAIROUAN | 100.00% |
| B | 1285 | 2 | 2 | AIN EDDEFLA | KASSERINE | 100.00% |
| B | 8141 | 2 | 2 | JENTOURA | JENDOUBA | 100.00% |
| B | 4004 | 1 | 107 | SOUSSE | SOUSSE | 100.00% |
| B | 8116 | 1 | 37 | BOU AOUENE | JENDOUBA | 100.00% |
| B | 4099 | 1 | 33 | MSAKEN EL GUEBLIA | SOUSSE | 100.00% |
| B | 7117 | 1 | 23 | KEF OUEST | KEF | 100.00% |
| B | 7094 | 1 | 18 | BORJ CHALLOUF | BIZERTE | 100.00% |
| B | 6132 | 1 | 17 | HAMMAM BIADHA | SILIANA | 100.00% |
| B | 8126 | 1 | 14 | BALTA | JENDOUBA | 100.00% |
| B | 2143 | 1 | 13 | DOUALY GAFSA | GAFSA | 100.00% |
| B | 9139 | 1 | 13 | EL GUELLEL | SIDI BOUZID | 100.00% |
| B | 5150 | 1 | 12 | MAHDIA REPUBLIQUE | MAHDIA | 100.00% |
| B | 3048 | 1 | 10 | SOUK EL FERIANI | SFAX | 100.00% |
| B | 8065 | 1 | 10 | OUED EL KHATEF | NABEUL | 100.00% |
| B | 3193 | 1 | 10 | EL GHABETTE | KAIROUAN | 100.00% |
| B | 4183 | 1 | 10 | OUERSNIA | MEDENINE | 100.00% |
| B | 7072 | 1 | 9 | MENZEL BOURGUIBA ENNAJAH | BIZERTE | 100.00% |
| B | 3057 | 1 | 8 | JEBERNA | SFAX | 100.00% |
| B | 9075 | 1 | 8 | EL HERRI | BEJA | 100.00% |
| B | 8124 | 1 | 7 | EL MARJA | JENDOUBA | 100.00% |
| B | 8121 | 1 | 7 | BABOUCH | JENDOUBA | 100.00% |
| B | 1232 | 1 | 7 | BOU DERYES | KASSERINE | 100.00% |
| B | 3233 | 1 | 6 | GATTOUFA | TATAOUINE | 100.00% |
| B | 1146 | 1 | 6 | SIDI AOUIDETTE | ZAGHOUAN | 100.00% |
| B | 3245 | 1 | 6 | KAMBOUT | TATAOUINE | 100.00% |
| B | 9154 | 1 | 6 | EL BOUAA | SIDI BOUZID | 100.00% |
| B | 9031 | 1 | 5 | EL MZARA | BEJA | 100.00% |
| B | 1245 | 1 | 5 | EL KAMOUR | KASSERINE | 100.00% |
| B | 1222 | 1 | 5 | SAHRAOUI | KASSERINE | 100.00% |
| B | 2192 | 1 | 5 | MAJOURA | GAFSA | 100.00% |
| B | 6056 | 1 | 5 | EZZERKINE | GABES | 100.00% |
| B | 8094 | 1 | 4 | MELLOUL | NABEUL | 100.00% |
| B | 1234 | 1 | 4 | EL GRINE | KASSERINE | 100.00% |
| B | 4143 | 1 | 4 | EL MAGHRAOUIA | MEDENINE | 100.00% |
| B | 3077 | 1 | 4 | DOUAR LOUATA | SFAX | 100.00% |
| B | 1213 | 1 | 3 | BOU CHEBKA | KASSERINE | 100.00% |
| B | 1162 | 1 | 3 | BENT SAIDANE | ZAGHOUAN | 100.00% |
| B | 3049 | 1 | 3 | SFAX MAGREB ARABE | SFAX | 100.00% |
| B | 9015 | 1 | 3 | EL KSAR | BEJA | 100.00% |
| B | 8082 | 1 | 3 | KHANGUET EL HOJJAJ | NABEUL | 100.00% |
| B | 3181 | 1 | 3 | BIR EDDAOULA | KAIROUAN | 100.00% |
| B | 9072 | 1 | 3 | CHAOUECH | BEJA | 100.00% |
| B | 1224 | 1 | 3 | EDDACHRA | KASSERINE | 100.00% |
| B | 2211 | 1 | 3 | DHAFRIA | TOZEUR | 100.00% |
| B | 7123 | 1 | 3 | SIDI AHMED ESSALAH | KEF | 100.00% |
| B | 9151 | 1 | 2 | EL FOUNI | SIDI BOUZID | 100.00% |
| B | 9158 | 1 | 2 | EL MECHE | SIDI BOUZID | 100.00% |
| B | 8069 | 1 | 1 | KELIBIA CHARGUIA | NABEUL | 100.00% |
| B | 8192 | 1 | 1 | EL HAOUAMDIA | JENDOUBA | 100.00% |
| B | 7136 | 1 | 1 | BOU JABEUR | KEF | 100.00% |
| B | 9062 | 1 | 1 | AIN TOUNGA | BEJA | 100.00% |
| B | 1223 | 1 | 1 | CEKHIRATE | KASSERINE | 100.00% |
| B | 6134 | 1 | 1 | SIDI BOUROUIS | SILIANA | 100.00% |
| B | 2122 | 1 | 1 | ZOMRA REDEYEF | GAFSA | 100.00% |
| B | 9084 | 1 | 1 | MENZEL EL GOURCHI | BEJA | 100.00% |

## 7.3 Candidate Type C: localite -> gouvernorat

| candidate_type | localite_client | candidate_rows | known_gouvernorat_rows | recommended_gouvernorat | dominance_percentage |
| --- | --- | --- | --- | --- | --- |
| C | SFAX | 12862 | 16614 | SFAX | 99.95% |
| C | ARIANA | 4722 | 7233 | ARIANA | 99.83% |
| C | SOUSSE | 3824 | 4039 | SOUSSE | 99.85% |
| C | KAIROUAN | 3473 | 1923 | KAIROUAN | 99.58% |
| C | BIZERTE | 3434 | 6062 | BIZERTE | 99.93% |
| C | TATAOUINE | 2800 | 4214 | TATAOUINE | 99.98% |
| C | BEN AROUS | 2769 | 2800 | BEN AROUS | 99.36% |
| C | SIDI BOUZID | 2758 | 4408 | SIDI BOUZID | 99.95% |
| C | GABES | 1993 | 873 | GABES | 100.00% |
| C | MEDENINE | 1730 | 2346 | MEDENINE | 100.00% |
| C | NABEUL | 1553 | 1559 | NABEUL | 99.94% |
| C | CITE ETTADHAMEN | 1517 | 2086 | ARIANA | 99.38% |
| C | LA MARSA | 1396 | 328 | TUNIS | 96.04% |
| C | MONASTIR | 1375 | 2091 | MONASTIR | 99.90% |
| C | JENDOUBA | 1273 | 2451 | JENDOUBA | 99.96% |
| C | ZAGHOUAN | 1232 | 1828 | ZAGHOUAN | 99.95% |
| C | BENI KHIAR | 1121 | 678 | NABEUL | 99.71% |
| C | REGUEB | 1065 | 1852 | SIDI BOUZID | 99.84% |
| C | KEBILI | 1052 | 340 | KEBILI | 100.00% |
| C | GROMBALIA | 985 | 1698 | NABEUL | 100.00% |
| C | TUNIS R P | 984 | 1 | ARIANA | 100.00% |
| C | RADES | 982 | 2299 | BEN AROUS | 99.78% |
| C | MAHDIA | 973 | 941 | MAHDIA | 99.68% |
| C | KORBA | 968 | 1578 | NABEUL | 99.94% |
| C | MOKNINE | 956 | 1046 | MONASTIR | 100.00% |
| C | KASSERINE | 914 | 1826 | KASSERINE | 99.78% |
| C | EL ALIA | 913 | 1200 | BIZERTE | 99.83% |
| C | GAFSA | 908 | 816 | GAFSA | 99.39% |
| C | MSAKEN | 876 | 2325 | SOUSSE | 99.96% |
| C | MATEUR | 845 | 1086 | BIZERTE | 99.91% |
| C | SILIANA | 830 | 596 | SILIANA | 99.66% |
| C | HAMMAMET | 818 | 2754 | NABEUL | 99.85% |
| C | M SAKEN | 735 | 7 | SOUSSE | 100.00% |
| C | METLAOUI | 734 | 315 | GAFSA | 100.00% |
| C | LE BARDO | 732 | 2222 | TUNIS | 99.73% |
| C | SOUASSI | 731 | 777 | MAHDIA | 99.74% |
| C | EL FAHS | 707 | 743 | ZAGHOUAN | 99.73% |
| C | JEMMEL | 688 | 9 | MONASTIR | 100.00% |
| C | LA SOUKRA | 684 | 1219 | ARIANA | 99.26% |
| C | OUED ELLIL | 667 | 1562 | MANNOUBA | 98.98% |
| C | JERBA | 662 | 949 | MEDENINE | 97.58% |
| C | EZZAHROUNI | 633 | 2166 | TUNIS | 99.77% |
| C | ZARZIS | 623 | 445 | MEDENINE | 99.55% |
| C | BEJA | 620 | 2142 | BEJA | 99.86% |
| C | NEFZA | 596 | 924 | BEJA | 99.57% |
| C | MARETH | 569 | 437 | GABES | 99.77% |
| C | KALAA EL KEBIRA | 543 | 646 | SOUSSE | 100.00% |
| C | EZZAHRA | 541 | 1617 | BEN AROUS | 96.23% |
| C | TEBOULBA | 536 | 1416 | MONASTIR | 100.00% |
| C | TAJEROUINE | 530 | 269 | KEF | 99.26% |
| C | MNIHLA | 526 | 1369 | ARIANA | 98.83% |
| C | REDEYEF | 511 | 1542 | GAFSA | 100.00% |
| C | ZERAMDINE | 495 | 588 | MONASTIR | 99.83% |
| C | EL HAMMA | 471 | 816 | GABES | 100.00% |
| C | FOUCHANA | 469 | 1057 | BEN AROUS | 99.81% |
| C | MENZEL BOURGUIBA | 464 | 1833 | BIZERTE | 99.95% |
| C | KALAA KEBIRA | 459 | 65 | SOUSSE | 98.46% |
| C | KSOUR ESSEF | 456 | 8 | MAHDIA | 100.00% |
| C | BOUARGOUB | 445 | 20 | NABEUL | 100.00% |
| C | HAMMAM SOUSSE | 444 | 838 | SOUSSE | 100.00% |
| C | NEFTA | 443 | 531 | TOZEUR | 100.00% |
| C | MOULARES | 438 | 902 | GAFSA | 100.00% |
| C | BIR ALI | 410 | 829 | SFAX | 99.88% |
| C | BEN GUERDANE | 409 | 2398 | MEDENINE | 100.00% |
| C | DAR CHAABANE | 407 | 169 | NABEUL | 98.22% |
| C | AKOUDA | 397 | 680 | SOUSSE | 99.71% |
| C | DOUAR HICHER | 395 | 1809 | MANNOUBA | 99.06% |
| C | TOZEUR | 376 | 789 | TOZEUR | 99.87% |
| C | MORNAGUIA | 365 | 1141 | MANNOUBA | 99.21% |
| C | LE KEF | 343 | 354 | KEF | 98.59% |
| C | EL OUERDIA | 330 | 1169 | TUNIS | 100.00% |
| C | LES BERGES DU LAC 2 | 323 | 15 | TUNIS | 100.00% |
| C | RAS JEBEL | 315 | 890 | BIZERTE | 100.00% |
| C | JEMMAL | 307 | 1468 | MONASTIR | 100.00% |
| C | ML JEMIL | 307 | 5 | BIZERTE | 100.00% |
| C | METOUIA | 304 | 4 | GABES | 100.00% |
| C | TUNIS BELVEDERE | 291 | 815 | TUNIS | 100.00% |
| C | TABARKA | 288 | 752 | JENDOUBA | 100.00% |
| C | SBIBA | 285 | 571 | KASSERINE | 99.65% |
| C | ARIANA NORD | 285 | 5 | ARIANA | 100.00% |
| C | TINJA | 283 | 589 | BIZERTE | 100.00% |
| C | BEKALTA | 278 | 507 | MONASTIR | 98.82% |
| C | MEGRINE | 275 | 637 | BEN AROUS | 99.22% |
| C | JEDAIDA | 274 | 1102 | MANNOUBA | 99.55% |
| C | KSOUR ESSAF | 255 | 1095 | MAHDIA | 99.91% |
| C | EL MOUROUJ | 253 | 2116 | BEN AROUS | 99.15% |
| C | MOHAMEDIA | 253 | 2 | BEN AROUS | 100.00% |
| C | BOU ARGOUB | 247 | 1329 | NABEUL | 100.00% |
| C | BOUHAJLA | 244 | 28 | KAIROUAN | 100.00% |
| C | ENFIDHA | 243 | 372 | SOUSSE | 98.39% |
| C | KSAR HELLAL | 242 | 35 | MONASTIR | 97.14% |
| C | EL JEM | 232 | 373 | MAHDIA | 100.00% |
| C | HERGLA | 232 | 358 | SOUSSE | 100.00% |
| C | SBIKHA | 232 | 250 | KAIROUAN | 99.20% |
| C | FAHS | 232 | 2 | ZAGHOUAN | 100.00% |
| C | HAMMAM LIF | 230 | 1417 | BEN AROUS | 99.93% |
| C | ML BOURG | 225 | 5 | BIZERTE | 100.00% |
| C | EL MIDA | 219 | 246 | NABEUL | 97.97% |
| C | ZAHROUNI | 212 | 6 | TUNIS | 100.00% |
| C | LE KRIB | 209 | 496 | SILIANA | 99.80% |
| C | ML BOURGUIBA | 209 | 6 | BIZERTE | 100.00% |
| C | KHAZNADAR | 208 | 743 | TUNIS | 99.46% |
| C | LE KRAM | 206 | 432 | TUNIS | 100.00% |
| C | SEJNANE | 200 | 605 | BIZERTE | 100.00% |
| C | JARZOUNA | 199 | 643 | BIZERTE | 100.00% |
| C | OUEDREF | 198 | 1 | GABES | 100.00% |
| C | ENFIDA | 191 | 3 | SOUSSE | 100.00% |
| C | SAKIET EDDAIER | 189 | 1183 | SFAX | 100.00% |
| C | SAHLINE | 188 | 258 | MONASTIR | 99.22% |
| C | MORNAG | 187 | 1067 | BEN AROUS | 99.91% |
| C | MAAMOURA | 187 | 13 | NABEUL | 100.00% |
| C | D HICHER | 187 | 1 | ARIANA | 100.00% |
| C | RAFRAF | 186 | 227 | BIZERTE | 100.00% |
| C | MENZEL TEMIME | 183 | 315 | NABEUL | 100.00% |
| C | TAZARKA | 182 | 351 | NABEUL | 99.72% |
| C | BOUMHAL | 180 | 23 | BEN AROUS | 95.65% |
| C | UTIQUE | 179 | 180 | BIZERTE | 100.00% |
| C | KELIBIA | 177 | 1095 | NABEUL | 100.00% |
| C | TEBOURBA | 176 | 545 | MANNOUBA | 98.53% |
| C | BIR ALI BEN KHALIFA | 176 | 3 | SFAX | 100.00% |
| C | METLINE | 174 | 233 | BIZERTE | 99.57% |
| C | HOUMT SOUK | 174 | 34 | MEDENINE | 97.06% |
| C | EL HAOUARIA | 173 | 142 | NABEUL | 99.30% |
| C | EL OMRANE | 171 | 358 | TUNIS | 99.16% |
| C | FERNANA | 169 | 294 | JENDOUBA | 99.66% |
| C | BORJ LOUZIR | 166 | 1107 | ARIANA | 99.64% |
| C | ENNADHOUR | 159 | 307 | ZAGHOUAN | 98.05% |
| C | NAASSEN | 157 | 482 | BEN AROUS | 100.00% |
| C | AIN DRAHAM | 156 | 369 | JENDOUBA | 99.73% |
| C | SAKIET EZZIT | 155 | 2116 | SFAX | 99.95% |
| C | THALA | 155 | 134 | KASSERINE | 100.00% |
| C | MAKTHAR | 151 | 194 | SILIANA | 99.48% |
| C | JERISSA | 149 | 50 | KEF | 100.00% |
| C | MENZEL ENNOUR | 148 | 238 | MONASTIR | 100.00% |
| C | CHORBANE | 148 | 171 | MAHDIA | 99.42% |
| C | RAOUED | 138 | 735 | ARIANA | 100.00% |
| C | CARTHAGE | 138 | 444 | TUNIS | 99.32% |
| C | OUERDANINE | 137 | 214 | MONASTIR | 100.00% |
| C | GHANNOUCHE | 136 | 181 | GABES | 100.00% |
| C | SIDI HASSINE | 130 | 3121 | TUNIS | 100.00% |
| C | SBEITLA | 130 | 248 | KASSERINE | 100.00% |
| C | SOMAA | 129 | 140 | NABEUL | 99.29% |
| C | KSAR SAID | 128 | 463 | TUNIS | 99.57% |
| C | BORDJ LOUZIR | 123 | 3 | ARIANA | 100.00% |
| C | ZAOUIET SOUSSE | 119 | 324 | SOUSSE | 100.00% |
| C | SIDI THABET | 118 | 246 | ARIANA | 99.59% |
| C | TESTOUR | 117 | 93 | BEJA | 100.00% |
| C | MOHAMADIA | 116 | 933 | BEN AROUS | 100.00% |
| C | LAC 2 | 116 | 11 | TUNIS | 100.00% |
| C | DENDEN | 115 | 1132 | MANNOUBA | 98.50% |
| C | GHARDIMAOU | 115 | 414 | JENDOUBA | 100.00% |
| C | NOUVELLE MEDINA | 110 | 1277 | BEN AROUS | 99.92% |
| C | SOLIMAN | 108 | 760 | NABEUL | 99.61% |
| C | EL OUARDIA | 108 | 4 | TUNIS | 100.00% |
| C | BENI KHALLED | 107 | 343 | NABEUL | 100.00% |
| C | HAFFOUZ | 107 | 162 | KAIROUAN | 99.38% |
| C | MANNOUBA | 107 | 5 | MANNOUBA | 100.00% |
| C | K KEBIRA | 106 | 5 | SOUSSE | 100.00% |
| C | SIDI BOU ALI | 105 | 180 | SOUSSE | 98.33% |
| C | KONDAR | 103 | 127 | SOUSSE | 98.43% |
| C | SKHIRA | 103 | 5 | SFAX | 100.00% |
| C | LA GOULETTE | 102 | 323 | TUNIS | 100.00% |
| C | BEMBLA | 96 | 248 | MONASTIR | 99.60% |
| C | AIN CHARFI | 95 | 857 | SFAX | 100.00% |
| C | GHOMRASSEN | 95 | 229 | TATAOUINE | 96.07% |
| C | DAR CHAABANE EL FEHRI | 93 | 10 | NABEUL | 100.00% |
| C | MOUROUJ 5 | 93 | 4 | BEN AROUS | 100.00% |
| C | MARSA | 92 | 1905 | TUNIS | 99.90% |
| C | MENZEL KAMEL | 92 | 375 | MONASTIR | 99.73% |
| C | OUESLATIA | 92 | 143 | KAIROUAN | 100.00% |
| C | MOUROUJ 1 | 92 | 4 | BEN AROUS | 100.00% |
| C | ELJEM | 92 | 1 | MONASTIR | 100.00% |
| C | AOUSJA | 91 | 4 | BIZERTE | 100.00% |
| C | GOUBELLAT | 90 | 114 | BEJA | 100.00% |
| C | JANDOUBA | 90 | 3 | JENDOUBA | 100.00% |
| C | BARRAKET ESSAHEL | 88 | 446 | NABEUL | 100.00% |
| C | SAYADA | 86 | 142 | MONASTIR | 98.59% |
| C | JOUMINE | 85 | 103 | BIZERTE | 100.00% |
| C | SEDJOUMI | 85 | 2 | TUNIS | 100.00% |
| C | BIR BOURAGBA | 84 | 1 | NABEUL | 100.00% |
| C | GHAR EL MELH | 83 | 189 | BIZERTE | 100.00% |
| C | GHRAIBA | 83 | 171 | SFAX | 100.00% |
| C | GHEZALA | 82 | 309 | BIZERTE | 100.00% |
| C | EL BRADAA | 80 | 179 | MAHDIA | 100.00% |
| C | MENZEL BOUZELFA | 79 | 233 | NABEUL | 100.00% |
| C | BENI HASSEN | 79 | 222 | MONASTIR | 100.00% |
| C | MORNEG | 79 | 10 | BEN AROUS | 100.00% |
| C | TEBELBOU | 76 | 6 | GABES | 100.00% |
| C | KHELIDIA | 74 | 169 | BEN AROUS | 99.41% |
| C | MOUROUJ 2 | 74 | 1 | TUNIS | 100.00% |
| C | H.SOUSSE | 73 | 2 | SOUSSE | 100.00% |
| C | ZOUAOUINE | 71 | 110 | BIZERTE | 99.09% |
| C | NVELLE MATMATA | 69 | 1 | GABES | 100.00% |
| C | HAJEB LAYOUN | 68 | 5 | KAIROUAN | 100.00% |
| C | MLE JEMILE | 68 | 3 | BIZERTE | 100.00% |
| C | SIDI HESSINE | 68 | 2 | TUNIS | 100.00% |
| C | MOUROUJ 4 | 67 | 3 | BEN AROUS | 100.00% |
| C | BIR BOUREGBA | 66 | 671 | NABEUL | 100.00% |
| C | KESRA | 66 | 75 | SILIANA | 98.67% |
| C | CHEBIKA | 65 | 125 | KAIROUAN | 100.00% |
| C | EL AZIB | 64 | 168 | BIZERTE | 100.00% |
| C | MATMATA | 64 | 45 | GABES | 100.00% |
| C | BOUCHEMMA | 64 | 8 | GABES | 100.00% |
| C | BNI KHALED | 64 | 1 | NABEUL | 100.00% |
| C | ZARZOUNA | 63 | 12 | BIZERTE | 100.00% |
| C | ESSLOUGUIA | 62 | 106 | BEJA | 100.00% |
| C | GHAR EL MELEH | 62 | 1 | BIZERTE | 100.00% |
| C | SIDI BOULBABA | 61 | 143 | GABES | 100.00% |
| C | SIJOUMI | 61 | 11 | TUNIS | 100.00% |
| C | BORJ EL AMRI | 60 | 369 | MANNOUBA | 100.00% |
| C | AGAREB | 59 | 363 | SFAX | 100.00% |
| C | KSIBET MEDIOUNI | 59 | 11 | MONASTIR | 100.00% |
| C | BIR LAHFAY | 59 | 1 | SIDI BOUZID | 100.00% |
| C | BOU ARADA | 58 | 116 | SILIANA | 100.00% |
| C | TEBOURSOUK | 56 | 186 | BEJA | 100.00% |
| C | SOUK LAHAD | 55 | 2 | SOUSSE | 100.00% |
| C | KHALED IBN WALID | 55 | 1 | MANOUBA | 100.00% |
| C | TOUZA | 54 | 160 | MONASTIR | 100.00% |
| C | CHERAHIL | 54 | 105 | MONASTIR | 99.05% |
| C | GAAFOUR | 53 | 85 | SILIANA | 95.29% |
| C | ETTAHRIR | 53 | 18 | TUNIS | 100.00% |
| C | SIDI EL HANI | 52 | 5 | SOUSSE | 100.00% |
| C | EL MANAR 2 | 51 | 526 | TUNIS | 100.00% |
| C | DAHMANI | 51 | 120 | KEF | 98.33% |
| C | BELLEVUE | 50 | 385 | TUNIS | 100.00% |
| C | ZRIBA | 50 | 113 | ZAGHOUAN | 95.58% |
| C | EL OMRANE SUP | 50 | 1 | TUNIS | 100.00% |
| C | IBN SINA | 49 | 598 | TUNIS | 100.00% |
| C | KALAAT LANDLOUS | 49 | 280 | ARIANA | 100.00% |
| C | FOUSSANA | 49 | 68 | KASSERINE | 100.00% |
| C | BOUROUIS | 49 | 5 | SILIANA | 100.00% |
| C | SIDI BOU SAID | 49 | 1 | TUNIS | 100.00% |
| C | HAIDRA | 48 | 20 | KASSERINE | 100.00% |
| C | ZAGHOUANE | 48 | 1 | ZAGHOUAN | 100.00% |
| C | BENI KHEDACHE | 47 | 249 | MEDENINE | 100.00% |
| C | HAJEB EL AYOUN | 46 | 342 | KAIROUAN | 100.00% |
| C | EL ALA | 46 | 143 | KAIROUAN | 99.30% |
| C | LE SERS | 46 | 115 | KEF | 100.00% |
| C | MJEZ EL BAB | 45 | 4 | BEJA | 100.00% |
| C | CITE 18 JANVIER | 44 | 477 | ARIANA | 98.11% |
| C | CITE EL KHADRA | 43 | 762 | TUNIS | 100.00% |
| C | DAR FADHAL | 43 | 494 | ARIANA | 99.19% |
| C | ZORDA | 43 | 48 | MAHDIA | 100.00% |
| C | NV MATMATA | 43 | 2 | GABES | 100.00% |
| C | SOUNINE | 42 | 58 | BIZERTE | 100.00% |
| C | EL KABBARIA | 42 | 17 | TUNIS | 100.00% |
| C | ENNASR 2 | 42 | 6 | ARIANA | 100.00% |
| C | KHENIS | 40 | 153 | MONASTIR | 100.00% |
| C | REMADA | 40 | 105 | TATAOUINE | 100.00% |
| C | GHAZELA | 40 | 5 | BIZERTE | 100.00% |
| C | BAZINA | 39 | 162 | BIZERTE | 100.00% |
| C | ZRIG | 39 | 81 | GABES | 100.00% |
| C | CARTHAGE BYRSA | 39 | 3 | TUNIS | 100.00% |
| C | EL MENZAH 9 | 38 | 301 | TUNIS | 99.67% |
| C | DOUZ | 38 | 85 | KEBILI | 100.00% |
| C | ARIANA ECOLE | 38 | 1 | ARIANA | 100.00% |
| C | EL KHETMINE | 38 | 1 | BIZERTE | 100.00% |
| C | MENZEL LAHBIB | 38 | 1 | GABES | 100.00% |
| C | CHATT MERIEM | 37 | 150 | SOUSSE | 100.00% |
| C | ELYASMINET | 37 | 1 | BEN AROUS | 100.00% |
| C | OUED MLIZ | 36 | 133 | JENDOUBA | 100.00% |
| C | AJIM | 36 | 121 | MEDENINE | 99.17% |
| C | LES JARDINS DE CARTHAGE | 36 | 7 | TUNIS | 100.00% |
| C | TUNIS CARTHAGE | 36 | 1 | TUNIS | 100.00% |
| C | B LOUZIR | 36 | 1 | ARIANA | 100.00% |
| C | SIDI JEDIDI | 35 | 189 | NABEUL | 100.00% |
| C | BIR LAHMAR | 35 | 171 | TATAOUINE | 99.42% |
| C | MUTUELLE VILLE | 35 | 138 | TUNIS | 99.28% |
| C | CITE EL GHAZALA | 35 | 17 | ARIANA | 100.00% |
| C | MONTFLEURY | 35 | 10 | TUNIS | 100.00% |
| C | LA MANNOUBA | 34 | 4189 | MANNOUBA | 99.88% |
| C | AIN ZAGHOUANE | 34 | 19 | TUNIS | 100.00% |
| C | BENI KHALED | 34 | 4 | NABEUL | 100.00% |
| C | EL KEF | 34 | 1 | KEF | 100.00% |
| C | OULED HAFFOUZ | 33 | 238 | SIDI BOUZID | 99.58% |
| C | SIDI BOUSAID | 33 | 231 | TUNIS | 99.57% |
| C | NASRALLAH | 33 | 127 | KAIROUAN | 98.43% |
| C | KSIBET SOUSSE | 33 | 117 | SOUSSE | 100.00% |
| C | MENZEL SALEM | 33 | 24 | KEF | 95.83% |
| C | BIR MCHERGUA | 33 | 8 | ZAGHOUAN | 100.00% |
| C | SOUK JEDID | 32 | 417 | SIDI BOUZID | 100.00% |
| C | EL MOUROUJ 1 | 32 | 233 | BEN AROUS | 98.71% |
| C | TAKELSA | 32 | 85 | NABEUL | 100.00% |
| C | KALAAT SINANE | 32 | 75 | KEF | 100.00% |
| C | KRAM | 32 | 4 | TUNIS | 100.00% |
| C | BIR ALI BEN KHELIFA | 31 | 471 | SFAX | 100.00% |
| C | BOU SALEM | 31 | 377 | JENDOUBA | 99.73% |
| C | JEBENIANA | 31 | 302 | SFAX | 100.00% |
| C | MENZEL HAYET | 31 | 112 | MONASTIR | 100.00% |
| C | OUARDANINE | 31 | 18 | MONASTIR | 100.00% |
| C | BOUMHEL | 31 | 4 | BEN AROUS | 100.00% |
| C | OUARDIA 1 | 31 | 2 | TUNIS | 100.00% |
| C | H SOUSSE | 31 | 2 | SOUSSE | 100.00% |
| C | KAIRAOUAN | 31 | 1 | KAIRAOUAN | 100.00% |
| C | MIDOUN | 30 | 259 | MEDENINE | 99.61% |
| C | RAS TABIA | 30 | 116 | TUNIS | 100.00% |
| C | RADES MELIANE | 30 | 87 | BEN AROUS | 98.85% |
| C | EL MOUROUJ 3 | 29 | 196 | BEN AROUS | 98.47% |
| C | OUERDIA | 29 | 2 | TUNIS | 100.00% |
| C | EL MAAMOURA | 28 | 132 | NABEUL | 100.00% |
| C | BOUHSINA | 28 | 52 | SOUSSE | 100.00% |
| C | KRIB | 28 | 12 | SILIANA | 100.00% |
| C | SAJNENE | 28 | 2 | BIZERTE | 100.00% |
| C | BORJ CEDRIA | 27 | 397 | BEN AROUS | 100.00% |
| C | HAMMAM CHATT | 27 | 368 | BEN AROUS | 100.00% |
| C | SAIDA | 27 | 292 | SIDI BOUZID | 98.97% |
| C | ESSAIDA | 27 | 139 | MANNOUBA | 99.28% |
| C | SIDI HSINE | 27 | 3 | TUNIS | 100.00% |
| C | MELLASSINE | 27 | 1 | EZZAHROUNI | 100.00% |
| C | MTORRECH | 26 | 89 | GABES | 100.00% |
| C | CITE AGRICOLE | 26 | 46 | SIDI BOUZID | 100.00% |
| C | MSAKEN EST | 26 | 6 | SOUSSE | 100.00% |
| C | ROMANA | 26 | 1 | TUNIS | 100.00% |
| C | J JELOUD | 26 | 1 | TUNIS | 100.00% |
| C | ALAA | 26 | 1 | KAIROUAN | 100.00% |
| C | EL MENZAH 1 | 25 | 334 | TUNIS | 99.40% |
| C | FERIANA | 25 | 82 | KASSERINE | 100.00% |
| C | GABES HACHED | 25 | 50 | GABES | 100.00% |
| C | BOUCHAMMA | 25 | 4 | GABES | 100.00% |
| C | MONFLEURY | 24 | 105 | TUNIS | 100.00% |
| C | EL MANAR 1 | 24 | 37 | TUNIS | 97.30% |
| C | KALAA SEGHIRA | 24 | 3 | SOUSSE | 100.00% |
| C | TATAOUIN | 24 | 2 | TATAOUIN | 100.00% |
| C | MESSAADINE | 24 | 1 | SOUSSE | 100.00% |
| C | EL MEDINA | 23 | 868 | TUNIS | 100.00% |
| C | SIDI ALOUENE | 23 | 692 | MAHDIA | 100.00% |
| C | LE KRAM OUEST | 23 | 230 | TUNIS | 100.00% |
| C | EL MOUROUJ 4 | 23 | 139 | BEN AROUS | 100.00% |
| C | KHEZAMA OUEST | 23 | 93 | SOUSSE | 100.00% |
| C | ENNASER 2 | 23 | 3 | ARIANA | 100.00% |
| C | SIDI HCINE | 23 | 1 | TUNIS | 100.00% |
| C | SAOUAF | 23 | 1 | ZAGHOUANE | 100.00% |
| C | JILMA | 22 | 313 | SIDI BOUZID | 99.68% |
| C | EL AOUSJA | 22 | 222 | BIZERTE | 100.00% |
| C | CEBBALA | 22 | 206 | SIDI BOUZID | 99.51% |
| C | CHERARDA | 22 | 98 | KAIROUAN | 98.98% |
| C | GARAAT SASSI | 22 | 50 | NABEUL | 100.00% |
| C | LA PETITE ARIANA | 22 | 1 | LA PETITE AR | 100.00% |
| C | MENZEL JEMIL | 21 | 1203 | BIZERTE | 100.00% |
| C | BAB SOUIKA | 21 | 243 | TUNIS | 99.59% |
| C | RADES PLAGE | 21 | 221 | BEN AROUS | 100.00% |
| C | EL MOUROUJ 5 | 21 | 136 | BEN AROUS | 100.00% |
| C | KHETMINE | 21 | 121 | BIZERTE | 100.00% |
| C | MENZEL FERSI | 21 | 106 | MONASTIR | 100.00% |
| C | KERKER | 21 | 91 | MAHDIA | 100.00% |
| C | MEDENINE EL JEDIDA | 21 | 87 | MEDENINE | 100.00% |
| C | OMRANE SUPERIEUR | 21 | 5 | TUNIS | 100.00% |
| C | SIDI BOUALI | 21 | 3 | SOUSSE | 100.00% |
| C | GREMDA | 21 | 2 | SFAX | 100.00% |
| C | BENI KHADECHE | 21 | 2 | MEDENINE | 100.00% |
| C | MENZAH 9 | 21 | 1 | ARIANA | 100.00% |
| C | BIZERT | 21 | 1 | BIZERTE | 100.00% |
| C | BAB BHAR | 20 | 2010 | TUNIS | 99.85% |
| C | EL YASMINETTE | 20 | 699 | BEN AROUS | 100.00% |
| C | EL MENZAH 5 | 20 | 268 | ARIANA | 97.76% |
| C | MESSADINE | 20 | 182 | SOUSSE | 100.00% |
| C | SAHLOUL | 20 | 175 | SOUSSE | 100.00% |
| C | CITE EL KHRACHFA | 20 | 32 | MEDENINE | 100.00% |
| C | HENCHIR EL BERNA | 20 | 7 | BIZERTE | 100.00% |
| C | NKHILETTE | 20 | 4 | ARIANA | 100.00% |
| C | CHATT MARIEM | 20 | 4 | SOUSSE | 100.00% |
| C | MOUROUJ 6 | 20 | 3 | BEN AROUS | 100.00% |
| C | SKT EZZIT | 20 | 2 | SFAX | 100.00% |
| C | KSAR HLEL | 20 | 2 | MONASTIR | 100.00% |
| C | ELFAHS | 20 | 1 | ZAGHOUAN | 100.00% |
| C | EL MENZAH 7 | 19 | 205 | ARIANA | 98.05% |
| C | SIDI REZIG | 19 | 111 | BEN AROUS | 99.10% |
| C | LA PECHERIE | 19 | 102 | BIZERTE | 100.00% |
| C | SIDI MAKHLOUF | 19 | 94 | MEDENINE | 100.00% |
| C | LOUATA | 19 | 85 | BIZERTE | 100.00% |
| C | SIDI EL HENI | 19 | 72 | SOUSSE | 100.00% |
| C | REJICHE | 19 | 68 | MAHDIA | 100.00% |
| C | MERKEZ KAANICHE | 19 | 54 | SFAX | 100.00% |
| C | CITE BIR ALI HELLAL | 19 | 34 | MONASTIR | 100.00% |
| C | JAAFER | 19 | 1 | ARIANA | 100.00% |
| C | TUNIS REPUBLIQUE | 19 | 1 | TUNIS | 100.00% |
| C | JEDLIANE | 19 | 1 | GASSRINE | 100.00% |
| C | GHEZALLA | 19 | 1 | BIZERTE | 100.00% |
| C | KSIBET EL MEDIOUNI | 18 | 146 | MONASTIR | 100.00% |
| C | KOUTINE | 18 | 94 | MEDENINE | 100.00% |
| C | BAB SAADOUN | 18 | 65 | TUNIS | 100.00% |
| C | DIAR EL HOJJEJ | 18 | 58 | NABEUL | 100.00% |
| C | KETTANA | 18 | 34 | GABES | 100.00% |
| C | HIBOUN | 18 | 13 | MAHDIA | 100.00% |
| C | KHEZEMA OUEST | 18 | 5 | SOUSSE | 100.00% |
| C | MNARA | 18 | 2 | MONASTIR | 100.00% |
| C | NAASEN | 18 | 1 | BEN AROUS | 100.00% |
| C | KAIROUEN | 18 | 1 | ZAGHOUEN | 100.00% |
| C | MENZEL ABDERRAHMEN | 18 | 1 | BIZERTE | 100.00% |
| C | SIDI DAOUD | 17 | 694 | TUNIS | 98.70% |
| C | CHOTRANA 1 | 17 | 328 | ARIANA | 99.70% |
| C | EL HENCHA | 17 | 93 | SFAX | 98.92% |
| C | KSIBET EL MADIOUNI | 17 | 4 | MONASTIR | 100.00% |
| C | OUEDHREF | 17 | 3 | GABES | 100.00% |
| C | CHAT MARIEM | 17 | 1 | SOUSSE | 100.00% |
| C | MENZEL BOUZALFA | 17 | 1 | NABEUL | 100.00% |
| C | MEZZOUNA | 16 | 215 | SIDI BOUZID | 100.00% |
| C | MONTPLAISIR | 16 | 185 | TUNIS | 100.00% |
| C | MAZDOUR | 16 | 47 | MONASTIR | 100.00% |
| C | EL OUERDIA 1 | 16 | 15 | TUNIS | 100.00% |
| C | BOUHSSINA | 16 | 13 | SOUSSE | 100.00% |
| C | BAB MNARA | 16 | 5 | TUNIS | 100.00% |
| C | BOUHJAR | 16 | 4 | MONASTIR | 100.00% |
| C | BRADAA | 16 | 3 | MAHDIA | 100.00% |
| C | JAAFAR | 16 | 3 | ARIANA | 100.00% |
| C | CITE LA GAZELLE | 16 | 1 | ARIANA | 100.00% |
| C | MOUROUJ4 | 16 | 1 | BEN AROUS | 100.00% |
| C | ELMOUROUJ | 16 | 1 | SILIANA | 100.00% |
| C | ANCIEN BLED | 15 | 313 | GABES | 100.00% |
| C | BEN AROUS SUD | 15 | 262 | BEN AROUS | 100.00% |
| C | CITE HELAL | 15 | 246 | TUNIS | 100.00% |
| C | EL BORJINE | 15 | 82 | SOUSSE | 100.00% |
| C | KALAA EL KHASBA | 15 | 44 | KEF | 100.00% |
| C | MENZEL HORR | 15 | 36 | NABEUL | 100.00% |
| C | MSAKEN OUEST | 15 | 7 | SOUSSE | 100.00% |
| C | KHEZAMA EST | 15 | 5 | SOUSSE | 100.00% |
| C | EL MOHAMADIA | 15 | 2 | BEN AROUS | 100.00% |
| C | MOUROUJ3 | 15 | 1 | BEN AROUS | 100.00% |
| C | . | 15 | 1 | SFAX | 100.00% |
| C | K SGHIRA | 15 | 1 | SOUSSE | 100.00% |
| C | MAKNASSY | 14 | 366 | SIDI BOUZID | 100.00% |
| C | TOUIREF | 14 | 42 | KEF | 100.00% |
| C | KHEZAMA | 14 | 20 | SOUSSE | 100.00% |
| C | GAMARTH | 14 | 1 | GAMARTH | 100.00% |
| C | ETADHAMEN | 14 | 1 | TUNIS | 100.00% |
| C | MEL JEMIL | 14 | 1 | BIZERTE | 100.00% |
| C | ML ABDERAHMEN | 14 | 1 | BIZERTE | 100.00% |
| C | LAAZIB | 14 | 1 | BIZERTE | 100.00% |
| C | BIR MCHERGA | 13 | 265 | ZAGHOUAN | 100.00% |
| C | EL MENZAH 8 | 13 | 159 | ARIANA | 98.74% |
| C | CITE DE LA RTT 2 | 13 | 87 | ARIANA | 100.00% |
| C | SIDI BANNOUR | 13 | 82 | MONASTIR | 100.00% |
| C | ZARAT | 13 | 74 | GABES | 100.00% |
| C | BECHIMA | 13 | 58 | GABES | 100.00% |
| C | BELHOUCHETTE | 13 | 5 | SFAX | 100.00% |
| C | MENZAH 8 | 13 | 2 | ARIANA | 100.00% |
| C | SOKRA | 13 | 2 | ARIANA | 100.00% |
| C | CITE EL GAZELLA | 13 | 1 | ARIANA | 100.00% |
| C | EL ALAA | 13 | 1 | KAIROUAN | 100.00% |
| C | KSIBET CHATT | 13 | 1 | SOUSSE | 100.00% |
| C | BOU MHEL | 12 | 1305 | BEN AROUS | 100.00% |
| C | GAMMART | 12 | 793 | TUNIS | 100.00% |
| C | EL OMRANE SUPERIEUR | 12 | 466 | TUNIS | 100.00% |
| C | MEGRINE CHAKER | 12 | 275 | BEN AROUS | 100.00% |
| C | ESSKHIRA | 12 | 262 | SFAX | 95.80% |
| C | EL AIN | 12 | 254 | SFAX | 100.00% |
| C | NOUVELLE MATMATA | 12 | 175 | GABES | 100.00% |
| C | KERKENAH | 12 | 140 | SFAX | 100.00% |
| C | TAIEB MHIRI | 12 | 124 | SILIANA | 95.16% |
| C | ZAOUIET KONTECH | 12 | 96 | MONASTIR | 100.00% |
| C | MLICHETTE | 12 | 68 | MONASTIR | 100.00% |
| C | KALAA ESGHIRA | 12 | 34 | SOUSSE | 100.00% |
| C | CITE DES OFFICIERS | 12 | 14 | TUNIS | 100.00% |
| C | TOZEUR AEROPORT | 12 | 9 | TOZEUR | 100.00% |
| C | SIDI ABDELHAMID | 12 | 7 | SOUSSE | 100.00% |
| C | RGUEB | 12 | 3 | SIDI BOUZID | 100.00% |
| C | MENZAH | 12 | 2 | TUNIS | 100.00% |
| C | SOUUSE | 12 | 1 | SOUSSE | 100.00% |
| C | EL GHAZELA | 12 | 1 | ARIANA | 100.00% |
| C | MENZAH 6 | 12 | 1 | ARIANA | 100.00% |
| C | ZAGHOUEN | 12 | 1 | TUNIS | 100.00% |
| C | HALFAOUINE | 12 | 1 | TUNIS | 100.00% |
| C | HAMMAM ZRIBA | 11 | 435 | ZAGHOUAN | 100.00% |
| C | EL MENZAH 6 | 11 | 187 | ARIANA | 97.86% |
| C | HEZOUA | 11 | 181 | TOZEUR | 100.00% |
| C | BORJ TOUIL | 11 | 142 | ARIANA | 100.00% |
| C | CITE BOUKHZAR | 11 | 121 | SOUSSE | 100.00% |
| C | NEBEUR | 11 | 51 | KEF | 98.04% |
| C | LAMTA | 11 | 48 | MONASTIR | 100.00% |
| C | EL GUETTAR | 11 | 45 | GAFSA | 100.00% |
| C | KRAM OUEST | 11 | 13 | TUNIS | 100.00% |
| C | KHEZEMA | 11 | 12 | SOUSSE | 100.00% |
| C | EZOUHOUR | 11 | 5 | SOUSSE | 100.00% |
| C | KLIBIA | 11 | 4 | NABEUL | 100.00% |
| C | BELVEDERE | 11 | 2 | TUNIS | 100.00% |
| C | JEBEL JLOUD | 11 | 2 | TUNIS | 100.00% |
| C | KAIRAOUEN | 11 | 1 | SFAX | 100.00% |
| C | GHAR DIMA | 11 | 1 | JENDOUBA | 100.00% |
| C | CITE EL MHIRI | 10 | 4000 | TUNIS | 99.90% |
| C | BIRINE | 10 | 324 | TUNIS | 100.00% |
| C | BIR EL BEY | 10 | 150 | BEN AROUS | 99.33% |
| C | BOU CHEMMA | 10 | 137 | GABES | 100.00% |
| C | CITE ALYSSA 1 | 10 | 116 | BEN AROUS | 100.00% |
| C | EL KNAIES | 10 | 73 | SOUSSE | 98.63% |
| C | THIBAR | 10 | 65 | BEJA | 100.00% |
| C | RECHERCHA | 10 | 61 | MAHDIA | 100.00% |
| C | SALAKTA | 10 | 59 | MAHDIA | 100.00% |
| C | CITE COMMERCIALE 1 | 10 | 29 | MONASTIR | 96.55% |
| C | RADES MONGIL | 10 | 18 | BEN AROUS | 100.00% |
| C | CITE EL KODS | 10 | 12 | MONASTIR | 100.00% |
| C | METLAOUI GARE | 10 | 11 | GAFSA | 100.00% |
| C | KALAA SOGHRA | 10 | 10 | SOUSSE | 100.00% |
| C | BAB EL KHADHRA | 10 | 9 | TUNIS | 100.00% |
| C | KALAA KBIRA | 10 | 8 | SOUSSE | 100.00% |
| C | CITE EL FANKAR | 10 | 7 | GABES | 100.00% |
| C | LAC | 10 | 5 | TUNIS | 100.00% |
| C | LA SOKRA | 10 | 3 | ARIANA | 100.00% |
| C | RIADH EL ANDALOUS | 10 | 3 | ARIANA | 100.00% |
| C | KALAAT ANDALOUS | 10 | 3 | ARIANA | 100.00% |
| C | AMAL | 10 | 2 | MANNOUBA | 100.00% |
| C | JBAL LAHMER | 10 | 2 | EL OMRANE | 100.00% |
| C | MENZEL CHAKER | 10 | 2 | SFAX | 100.00% |
| C | CITE SIDI MOUSSA | 10 | 2 | NABEUL | 100.00% |
| C | BOUMERDESS | 10 | 2 | MAHDIA | 100.00% |
| C | ELKEF | 10 | 1 | ELKEF | 100.00% |
| C | SEJNEN | 10 | 1 | BIZERTE | 100.00% |
| C | SOUSSA | 10 | 1 | SOUSSE | 100.00% |
| C | TYAYRA | 10 | 1 | MONASTIR | 100.00% |
| C | BENI HASSAN | 10 | 1 | MONASTIR | 100.00% |
| C | EL HRAIRIA | 9 | 1055 | TUNIS | 99.91% |
| C | SOUSSE RIADH | 9 | 541 | SOUSSE | 100.00% |
| C | NOUVELLE ARIANA | 9 | 106 | ARIANA | 99.06% |
| C | BENI AICHOUN | 9 | 99 | NABEUL | 100.00% |
| C | MEGRINE RIADH | 9 | 90 | BEN AROUS | 100.00% |
| C | CITE RAFAHA | 9 | 87 | ARIANA | 98.85% |
| C | CITE BOUGATFA 1 | 9 | 84 | TUNIS | 98.81% |
| C | KALAA KEBIRAA | 9 | 74 | SOUSSE | 98.65% |
| C | HBIRA | 9 | 61 | MAHDIA | 98.36% |
| C | CHOUCHET RADES | 9 | 54 | BEN AROUS | 100.00% |
| C | SOUK EL AHAD | 9 | 42 | KEBILI | 100.00% |
| C | BELKHIR | 9 | 40 | GAFSA | 100.00% |
| C | CITE BOU DRISSE | 9 | 35 | MONASTIR | 97.14% |
| C | BAZIM | 9 | 29 | MEDENINE | 96.55% |
| C | GAFSA AEROPORT | 9 | 20 | GAFSA | 100.00% |
| C | BENI FETAIEL | 9 | 20 | MEDENINE | 100.00% |
| C | SEBIKHA | 9 | 5 | KAIROUAN | 100.00% |
| C | RAS JEBAL | 9 | 4 | BIZERTE | 100.00% |
| C | ZAREMDINE | 9 | 3 | MONASTIR | 100.00% |
| C | SLIMANE | 9 | 2 | NABEUL | 100.00% |
| C | REDAYEF | 9 | 2 | GAFSA | 100.00% |
| C | MENZEH 7 | 9 | 1 | ARIANA | 100.00% |
| C | KHLIDIA | 9 | 1 | BEN AROUS | 100.00% |
| C | ENKHILET | 9 | 1 | ARIANA | 100.00% |
| C | BORDJ CEDRIA | 9 | 1 | HAMMAM LIF | 100.00% |
| C | BORDJ LOZIR | 9 | 1 | ARIANA | 100.00% |
| C | MANARET HAMMAMET | 9 | 1 | NABEUL | 100.00% |
| C | KALAA SEGHAIRA | 9 | 1 | SOUSSE | 100.00% |
| C | HABIRA | 9 | 1 | MAHDIA | 100.00% |
| C | AMIRET FHOUL | 9 | 1 | MONASTIR | 100.00% |
| C | EL HICHA | 9 | 1 | GABES | 100.00% |
| C | ROHIA | 8 | 281 | SILIANA | 100.00% |
| C | CHENINI GABES | 8 | 128 | GABES | 100.00% |
| C | SOMBAT | 8 | 119 | GABES | 100.00% |
| C | SMAR | 8 | 95 | TATAOUINE | 100.00% |
| C | EL AYOUN | 8 | 64 | KASSERINE | 98.44% |
| C | DAR ALLOUCHE | 8 | 53 | NABEUL | 100.00% |
| C | AZMOUR | 8 | 50 | NABEUL | 100.00% |
| C | TATAOUINE 7 NOVEMBRE | 8 | 48 | TATAOUINE | 100.00% |
| C | CITE BAYECH | 8 | 42 | GAFSA | 100.00% |
| C | KASSERINE NOUR | 8 | 28 | KASSERINE | 100.00% |
| C | CHENCHOU | 8 | 26 | GABES | 100.00% |
| C | CITE GHAZELLA | 8 | 7 | ARIANA | 100.00% |
| C | LES BERGES DU LAC 1 | 8 | 3 | TUNIS | 100.00% |
| C | ARIANA SUPERIEUR | 8 | 3 | ARIANA | 100.00% |
| C | PETITE ARIANA | 8 | 2 | ARIANA | 100.00% |
| C | KALAAT LANDALOUS | 8 | 2 | L'ARIANA | 100.00% |
| C | SAWAF | 8 | 2 | ZAGHOUAN | 100.00% |
| C | SLIMENE | 8 | 2 | NABEUL | 100.00% |
| C | TATOUINE | 8 | 1 | TUNISIE | 100.00% |
| C | ENNASR2 | 8 | 1 | ARIANA | 100.00% |
| C | CARTHAGE BIRSA | 8 | 1 | TUNIS | 100.00% |
| C | OUARDIA 4 | 8 | 1 | TUNIS | 100.00% |
| C | CTE ETTAHRIR | 8 | 1 | BARDO | 100.00% |
| C | BIR DRESSEN | 8 | 1 | NABEUL | 100.00% |
| C | JBENIANA | 8 | 1 | SFAX | 100.00% |
| C | KT MEDIOUNI | 8 | 1 | MONASTIR | 100.00% |
| C | REPUBLIQUE | 7 | 1651 | TUNIS | 99.82% |
| C | MARSA SAFSAF | 7 | 633 | TUNIS | 99.84% |
| C | JAYARA | 7 | 210 | TUNIS | 100.00% |
| C | CITE ENNASR 1 | 7 | 204 | ARIANA | 96.57% |
| C | CITE AZIZA | 7 | 197 | TUNIS | 100.00% |
| C | HAMMAM EL GHEZAZ | 7 | 123 | NABEUL | 100.00% |
| C | BENNANE | 7 | 119 | MONASTIR | 100.00% |
| C | GUELLALA | 7 | 109 | MEDENINE | 100.00% |
| C | BORJ HAFAIEDH | 7 | 87 | NABEUL | 100.00% |
| C | MZAOUGHA | 7 | 78 | MONASTIR | 100.00% |
| C | BOU REGBA | 7 | 75 | MANNOUBA | 100.00% |
| C | SALAMBO | 7 | 55 | TUNIS | 100.00% |
| C | EL MENZAH 4 | 7 | 47 | TUNIS | 100.00% |
| C | MAHDIA EZZAHRA | 7 | 44 | MAHDIA | 100.00% |
| C | ESSAKIA | 7 | 40 | KEF | 100.00% |
| C | EL HAFSIA | 7 | 33 | TUNIS | 96.97% |
| C | TABEDIT | 7 | 32 | GAFSA | 100.00% |
| C | RADES FORET | 7 | 25 | BEN AROUS | 96.00% |
| C | EL GHEDHABNA | 7 | 21 | MAHDIA | 95.24% |
| C | SAHLOUL 3 | 7 | 12 | SOUSSE | 100.00% |
| C | EL OUERDIA 6 | 7 | 12 | TUNIS | 100.00% |
| C | CENTRE URBAIN NORD | 7 | 9 | TUNIS | 100.00% |
| C | SISSEB | 7 | 8 | KAIROUAN | 100.00% |
| C | HAJEB LAAYOUN | 7 | 6 | KAIROUAN | 100.00% |
| C | DAR CHAABNE | 7 | 4 | NABEUL | 100.00% |
| C | SAHLOUL 2 | 7 | 3 | SOUSSE | 100.00% |
| C | EL MOUROUJ1 | 7 | 3 | BEN AROUS | 100.00% |
| C | JEBAL LAHMAR | 7 | 3 | TUNIS | 100.00% |
| C | BNI HASSEN | 7 | 3 | MONASTIR | 100.00% |
| C | KANTAOUI | 7 | 2 | SOUSSE | 100.00% |
| C | MARSA OUEST | 7 | 2 | TUNIS | 100.00% |
| C | MENZAH 1 | 7 | 2 | TUNIS | 100.00% |
| C | ECHRAF | 7 | 2 | NABEUL | 100.00% |
| C | RDAYEF | 7 | 2 | GAFSA | 100.00% |
| C | KHNISS | 7 | 2 | MONASTIR | 100.00% |
| C | EL WARDIA | 7 | 1 | TUNIS | 100.00% |
| C | JBAL JLOUD | 7 | 1 | TUNIS | 100.00% |
| C | EL MENZAH 9A | 7 | 1 | TUNIS | 100.00% |
| C | ENNFIDHA | 7 | 1 | SOUSSE | 100.00% |
| C | MTORECH | 7 | 1 | GABES | 100.00% |
| C | CITE EL MECHTEL | 6 | 284 | TUNIS | 100.00% |
| C | SIDI FATHALLAH | 6 | 231 | TUNIS | 100.00% |
| C | DHEHIBA | 6 | 108 | TATAOUINE | 100.00% |
| C | SMINJA | 6 | 69 | ZAGHOUAN | 100.00% |
| C | BAJOU | 6 | 55 | BIZERTE | 100.00% |
| C | AIN ZAGHOUEN | 6 | 43 | TUNIS | 97.67% |
| C | KROUSSIA | 6 | 43 | SOUSSE | 100.00% |
| C | DOUGHRA | 6 | 40 | KASSERINE | 100.00% |
| C | BOUARAADA | 6 | 28 | SELIANA | 100.00% |
| C | CITE BEN KILANI | 6 | 25 | GABES | 96.00% |
| C | ABENE | 6 | 19 | NABEUL | 100.00% |
| C | LEBNA | 6 | 16 | NABEUL | 100.00% |
| C | SMENJA | 6 | 14 | ZAGHOUAN | 100.00% |
| C | BAAJLA | 6 | 9 | MAHDIA | 100.00% |
| C | EL MOUROUJ5 | 6 | 5 | BEN AROUS | 100.00% |
| C | LA MARSA OUEST | 6 | 4 | TUNIS | 100.00% |
| C | EL MOUROUJ4 | 6 | 4 | BEN AROUS | 100.00% |
| C | GHANOUCH | 6 | 2 | GABES | 100.00% |
| C | BIR EL BAY | 6 | 2 | BEN AROUS | 100.00% |
| C | MREZGUA | 6 | 2 | NABEUL | 100.00% |
| C | ESSIJOUMI | 6 | 2 | TUNIS | 100.00% |
| C | DAR CHAABENE | 6 | 2 | NABEUL | 100.00% |
| C | ZAOUIT SOUSSE | 6 | 2 | SOUSSE | 100.00% |
| C | LIBYAN | 6 | 1 | BEN AROUS | 100.00% |
| C | MENZEL TMIME | 6 | 1 | NABEUL | 100.00% |
| C | EL MARSA | 6 | 1 | TUNIS | 100.00% |
| C | HAFOUZ | 6 | 1 | ZAGHOUAN | 100.00% |
| C | BOUMHAL BASSATINE | 6 | 1 | BEN AROUS | 100.00% |
| C | EL KEDOUA | 6 | 1 | NABEUL | 100.00% |
| C | RUE TAHER HADED | 6 | 1 | GABES | 100.00% |
| C | CHEBBAOU | 6 | 1 | MANNOUBA | 100.00% |
| C | MASJED AISSA | 6 | 1 | MONASTIR | 100.00% |
| C | BIR EL HAFFEY | 5 | 598 | SIDI BOUZID | 100.00% |
| C | CITE KHALED IBN EL WALID | 5 | 553 | MANNOUBA | 99.46% |
| C | CITE IBN KHALDOUN I | 5 | 516 | TUNIS | 100.00% |
| C | EZZOUHOUR 4 | 5 | 377 | TUNIS | 100.00% |
| C | BEN OUN | 5 | 186 | SIDI BOUZID | 100.00% |
| C | EL OUERDIA 4 | 5 | 143 | TUNIS | 100.00% |
| C | CITE EL WIFAK | 5 | 93 | BEN AROUS | 96.77% |
| C | MONJI SLIM | 5 | 85 | SILIANA | 95.29% |
| C | CHARGUIA 1 | 5 | 85 | ARIANA | 98.82% |
| C | CHARGUIA 2 | 5 | 75 | ARIANA | 100.00% |
| C | BARNOUSSA | 5 | 69 | KEF | 98.55% |
| C | MOUREDDINE | 5 | 68 | SOUSSE | 100.00% |
| C | EL MOUROUJ 6 | 5 | 49 | BEN AROUS | 97.96% |
| C | TAMRA | 5 | 38 | BIZERTE | 100.00% |
| C | BIR MOUKRA | 5 | 32 | ZAGHOUAN | 100.00% |
| C | KORBOUS | 5 | 26 | NABEUL | 100.00% |
| C | NAHAL | 5 | 25 | GABES | 100.00% |
| C | CITE BAKHTIT | 5 | 18 | TATAOUINE | 100.00% |
| C | SBIH | 5 | 15 | SFAX | 100.00% |
| C | AIN FAROUA | 5 | 14 | BIZERTE | 100.00% |
| C | SAHLOUL 1 | 5 | 9 | SOUSSE | 100.00% |
| C | LAFAYETTE | 5 | 6 | TUNIS | 100.00% |
| C | NFIDHA | 5 | 5 | SOUSSE | 100.00% |
| C | BIR HLIMA | 5 | 4 | ZAGHOUAN | 100.00% |
| C | THRAYET | 5 | 4 | SOUSSE | 100.00% |
| C | SIDI HASSIN | 5 | 3 | TUNIS | 100.00% |
| C | MIDA | 5 | 3 | NABEUL | 100.00% |
| C | SIDI MADHKOUR | 5 | 3 | NABEUL | 100.00% |
| C | AMDOUN | 5 | 3 | BEJA | 100.00% |
| C | SAHLOUL2 | 5 | 2 | SOUSSE | 100.00% |
| C | AVICENNE | 5 | 2 | TUNIS | 100.00% |
| C | EL MALLASSINE | 5 | 2 | TUNIS | 100.00% |
| C | SIDI HSSIN | 5 | 2 | TUNIS | 100.00% |
| C | HENCHA | 5 | 2 | SFAX | 100.00% |
| C | ZARMDINE | 5 | 2 | MONASTIR | 100.00% |
| C | GHAMMART | 5 | 1 | TUNIS | 100.00% |
| C | AL INTILAKA | 5 | 1 | TUNIS | 100.00% |
| C | MANAR2 | 5 | 1 | ARIANA | 100.00% |
| C | SIDI HSIN | 5 | 1 | TUNIS | 100.00% |
| C | BORJ ELAMRI | 5 | 1 | MANNOUBA | 100.00% |
| C | M EL JEMIL | 5 | 1 | BIZERTE | 100.00% |
| C | BEZINA | 5 | 1 | BIZERTE | 100.00% |
| C | GRAMBALIA | 5 | 1 | TUNIS | 100.00% |
| C | MENZAH6 | 5 | 1 | TUNIS | 100.00% |
| C | GHANNOUCH | 5 | 1 | GABES | 100.00% |
| C | BANEN | 5 | 1 | MONASTIR | 100.00% |
| C | ZERMADINE | 5 | 1 | MONASTIR | 100.00% |
| C | KALAA ESSGHIRA | 4 | 498 | SOUSSE | 100.00% |
| C | BOU FICHA | 4 | 412 | SOUSSE | 100.00% |
| C | MENZEL BOUZAIENE | 4 | 205 | SIDI BOUZID | 100.00% |
| C | TEBOULBOU | 4 | 138 | GABES | 100.00% |
| C | BOU ROUIS | 4 | 121 | SILIANA | 100.00% |
| C | BIR HALIMA | 4 | 116 | ZAGHOUAN | 100.00% |
| C | LA REPUBLIQUE | 4 | 101 | SILIANA | 96.04% |
| C | DIBOUZVILLE | 4 | 91 | TUNIS | 100.00% |
| C | MERKEZ SAHNOUN | 4 | 79 | SFAX | 100.00% |
| C | HASSI AMOR | 4 | 79 | MEDENINE | 100.00% |
| C | ARIANA ESSOUGHRA | 4 | 78 | ARIANA | 100.00% |
| C | ARGOUB EZZAATAR | 4 | 71 | BEJA | 100.00% |
| C | MAHDIA HIBOUN | 4 | 61 | MAHDIA | 100.00% |
| C | ARRAM | 4 | 60 | GABES | 100.00% |
| C | CHOTRANA 2 | 4 | 50 | ARIANA | 100.00% |
| C | CHAOUAT | 4 | 44 | MANNOUBA | 100.00% |
| C | MOOTMAR | 4 | 39 | MONASTIR | 100.00% |
| C | CHOTRANA 3 | 4 | 37 | ARIANA | 97.30% |
| C | BEJAOUA 2 | 4 | 37 | ARIANA | 100.00% |
| C | KHEIREDDINE | 4 | 33 | TUNIS | 100.00% |
| C | CITE DES MEDECINS | 4 | 32 | TUNIS | 100.00% |
| C | BECHRI | 4 | 29 | KEBILI | 100.00% |
| C | HAZEG | 4 | 28 | SFAX | 100.00% |
| C | TESKRAYA | 4 | 26 | BIZERTE | 100.00% |
| C | MELLITA | 4 | 24 | SFAX | 95.83% |
| C | LALA | 4 | 16 | GAFSA | 100.00% |
| C | KRIB GARE | 4 | 15 | SILIANA | 100.00% |
| C | CITE EL MELLESSINE | 4 | 13 | KEF | 100.00% |
| C | CITE SIDI AMOR | 4 | 12 | NABEUL | 100.00% |
| C | JARDINS DE CARTHAGE | 4 | 10 | TUNIS | 100.00% |
| C | JIBINIANA | 4 | 8 | SFAX | 100.00% |
| C | DAMOUS | 4 | 8 | NABEUL | 100.00% |
| C | RAOUED PLAGE | 4 | 8 | ARIANA | 100.00% |
| C | SKALBA | 4 | 6 | NABEUL | 100.00% |
| C | SIDI JAMELEDDINE | 4 | 6 | NABEUL | 100.00% |
| C | SIDI BOUROUIS | 4 | 5 | SILIANA | 100.00% |
| C | EL OMRAN | 4 | 4 | TUNIS | 100.00% |
| C | EL FAHES | 4 | 4 | ZAGHOUAN | 100.00% |
| C | CHEBBA | 4 | 3 | MAHDIA | 100.00% |
| C | KHEZEMA EST | 4 | 3 | SOUSSE | 100.00% |
| C | CITE LES PINS | 4 | 2 | TUNIS | 100.00% |
| C | CARTHAGE HANNIBAL | 4 | 2 | TUNIS | 100.00% |
| C | FATHALLAH | 4 | 2 | TUNIS | 100.00% |
| C | CITE DHAMENE 2 | 4 | 2 | MANNOUBA | 100.00% |
| C | TUNIS JEBBARI | 4 | 1 | TUNIS | 100.00% |
| C | CITE ENNASER 2 | 4 | 1 | ARIANA | 100.00% |
| C | CITE ENNASSIM | 4 | 1 | ZAGHOUAN | 100.00% |
| C | CITÉ INTILAKA | 4 | 1 | TUNIS | 100.00% |
| C | ENNKHILET | 4 | 1 | ARIANA | 100.00% |
| C | MANAR1 | 4 | 1 | ARIANA | 100.00% |
| C | HAMMAM CHAT | 4 | 1 | TUNIS | 100.00% |
| C | ESALEMA | 4 | 1 | MANNOUBA | 100.00% |
| C | HAFSIA | 4 | 1 | TUNIS | 100.00% |
| C | EL MENZAH8 | 4 | 1 | ARIANA | 100.00% |
| C | HAMMAMAT | 4 | 1 | NABEUL | 100.00% |
| C | BOUGATFA | 4 | 1 | BIZERTE | 100.00% |
| C | ESSOMRANE | 4 | 1 | TUNIS | 100.00% |
| C | HAMMAMAET | 4 | 1 | NABEUL | 100.00% |
| C | CORNICHE | 4 | 1 | SOUSSE | 100.00% |
| C | RAWED | 4 | 1 | ARIANA | 100.00% |
| C | SERES | 4 | 1 | KEF | 100.00% |
| C | BENENE | 4 | 1 | MONASTIR | 100.00% |
| C | SIDIBOUZID | 4 | 1 | SIDI BOUZID | 100.00% |
| C | SELYANA | 4 | 1 | TUNIS | 100.00% |
| C | MALLASSINE | 4 | 1 | TUNIS | 100.00% |
| C | M EL ABDERRAHMEN | 4 | 1 | BIZERTE | 100.00% |
| C | CITE ENNASR 2 | 3 | 448 | ARIANA | 99.78% |
| C | CITE EL BASSATINE1 | 3 | 121 | ARIANA | 98.35% |
| C | EL BATTAN | 3 | 99 | MANNOUBA | 97.98% |
| C | OUDHREF | 3 | 92 | GABES | 100.00% |
| C | CITE MZERAA | 3 | 87 | GAFSA | 100.00% |
| C | CITE ENNOUHOUDH | 3 | 84 | GAFSA | 97.62% |
| C | BENI RABIA | 3 | 82 | SOUSSE | 100.00% |
| C | EL MAY | 3 | 81 | MEDENINE | 100.00% |
| C | BORTAL HAYDER | 3 | 76 | TUNIS | 100.00% |
| C | AIN GHELAL | 3 | 60 | BIZERTE | 100.00% |
| C | SKANES | 3 | 59 | MONASTIR | 100.00% |
| C | CHAABET EL MREZGA | 3 | 58 | NABEUL | 100.00% |
| C | CITE THAMEUR | 3 | 44 | TUNIS | 100.00% |
| C | SNED | 3 | 44 | GAFSA | 100.00% |
| C | AMILCAR | 3 | 43 | TUNIS | 100.00% |
| C | CITE MAGROUN | 3 | 41 | GAFSA | 100.00% |
| C | CITE GHARNATA | 3 | 39 | NABEUL | 100.00% |
| C | CITE BOU AKROUCHA | 3 | 35 | BEN AROUS | 100.00% |
| C | NIANOU | 3 | 33 | NABEUL | 100.00% |
| C | SIDI ASSAKER | 3 | 33 | MAHDIA | 100.00% |
| C | SOUIHEL | 3 | 30 | MEDENINE | 100.00% |
| C | BELLI | 3 | 29 | NABEUL | 100.00% |
| C | EL FAOUAR | 3 | 25 | KEBILI | 100.00% |
| C | CITE BADRANI | 3 | 24 | SFAX | 100.00% |
| C | CHIBA | 3 | 23 | MAHDIA | 100.00% |
| C | CHAFAI | 3 | 22 | KASSERINE | 100.00% |
| C | BIR MROUA | 3 | 19 | NABEUL | 100.00% |
| C | SOUSSE IBN KHALDOUN | 3 | 19 | SOUSSE | 100.00% |
| C | AHEL JEMIAA | 3 | 19 | SOUSSE | 100.00% |
| C | BENI SAID | 3 | 18 | BEJA | 100.00% |
| C | EL NAHLI | 3 | 14 | ARIANA | 100.00% |
| C | ZAAFRANA | 3 | 14 | KAIROUAN | 100.00% |
| C | CITE BIR HMEM | 3 | 13 | BIZERTE | 100.00% |
| C | BLED EL HADHAR | 3 | 12 | TOZEUR | 100.00% |
| C | JARDIN DE CARTHAGE | 3 | 10 | TUNIS | 100.00% |
| C | CITE FATEH | 3 | 9 | ARIANA | 100.00% |
| C | AIN JAFFEL | 3 | 8 | SIDI BOUZID | 100.00% |
| C | CITE DAR EL AMEN | 3 | 6 | KAIROUAN | 100.00% |
| C | GROMBELIA | 3 | 5 | NABEUL | 100.00% |
| C | BORJ ESSOUFI | 3 | 5 | BEN AROUS | 100.00% |
| C | BAB SAADOUN GARE | 3 | 4 | TUNIS | 100.00% |
| C | RUE MOHAMED ALI | 3 | 4 | SOUSSE | 100.00% |
| C | SIDI FRAJ | 3 | 3 | ARIANA | 100.00% |
| C | CITÉ EZZOUHOUR | 3 | 3 | SOUSSE | 100.00% |
| C | LAC2 | 3 | 2 | TUNIS | 100.00% |
| C | KEROUAN | 3 | 2 | KEROUAN | 100.00% |
| C | CITE 22 JANVIER | 3 | 2 | MONASTIR | 100.00% |
| C | BHIRA | 3 | 1 | BIZERTE | 100.00% |
| C | MANZEH 7 | 3 | 1 | ARIANA | 100.00% |
| C | EL MENZAH6 | 3 | 1 | TUNIS | 100.00% |
| C | EL MOUROUJ2 | 3 | 1 | BEN AROUS | 100.00% |
| C | CHABAOU | 3 | 1 | MANOUBA | 100.00% |
| C | BEB EL KHADHRA | 3 | 1 | TUNIS | 100.00% |
| C | FAHES | 3 | 1 | KAIROUAN | 100.00% |
| C | KALLAT ANDALOUS | 3 | 1 | ARIANA | 100.00% |
| C | SFAX VILLE | 3 | 1 | SFAX | 100.00% |
| C | YASMINET | 3 | 1 | TUNIS | 100.00% |
| C | MENZEL HAREB | 3 | 1 | MONASTIR | 100.00% |
| C | BENI KHERA | 3 | 1 | NABEUL | 100.00% |
| C | AIN JLOULA | 3 | 1 | KAIROUAN | 100.00% |
| C | BIR BEY | 3 | 1 | BEN AROUS | 100.00% |
| C | GOUBELAT | 3 | 1 | BEJA | 100.00% |
| C | OMRAN | 3 | 1 | TUNIS | 100.00% |
| C | ESAADA | 3 | 1 | ZAGHOUAN | 100.00% |
| C | TAFFELA | 3 | 1 | SOUSSE | 100.00% |
| C | K KOBRA | 3 | 1 | SOUSSE | 100.00% |
| C | DEGUECH | 3 | 1 | GAFSA | 100.00% |
| C | NV MATMATTA | 3 | 1 | GABES | 100.00% |
| C | CITE EL EZDIHAR | 3 | 1 | TOZEUR | 100.00% |
| C | MATMATA NOUVELLE | 3 | 1 | GABES | 100.00% |
| C | KSOUR | 3 | 1 | KEF | 100.00% |
| C | BOUGATFA 2 | 3 | 1 | BIZERTE | 100.00% |
| C | OURDANINE | 3 | 1 | MONASTIR | 100.00% |
| C | MLICHET | 3 | 1 | MONASTIR | 100.00% |
| C | SOUSSE MEDINA | 3 | 1 | SOUSSE | 100.00% |
| C | GHZALA | 3 | 1 | BIZERTE | 100.00% |
| C | SEJENEN | 3 | 1 | BIZERTE | 100.00% |
| C | RUE TAREK IBN ZIED | 3 | 1 | GABES | 100.00% |
| C | CITE EL FATH | 3 | 1 | TUNIS | 100.00% |
| C | BERGE DU LAC | 2 | 2932 | TUNIS | 100.00% |
| C | MAHRAS | 2 | 1124 | SFAX | 100.00% |
| C | MEJEZ EL BAB | 2 | 639 | BEJA | 100.00% |
| C | KSAR HELAL | 2 | 513 | MONASTIR | 100.00% |
| C | JAAFAR 1 | 2 | 353 | ARIANA | 100.00% |
| C | DAR CHAABANE ELFEHRI | 2 | 327 | NABEUL | 100.00% |
| C | SOUSSE EZZOUHOUR | 2 | 284 | SOUSSE | 100.00% |
| C | EL MOUENSA | 2 | 173 | MEDENINE | 100.00% |
| C | ROMMANA | 2 | 165 | TUNIS | 100.00% |
| C | SFAX EL JADIDA | 2 | 156 | SFAX | 99.36% |
| C | BAB DJEDID | 2 | 131 | TUNIS | 100.00% |
| C | LE KRAM EST | 2 | 98 | TUNIS | 100.00% |
| C | SAOUEF | 2 | 92 | ZAGHOUAN | 100.00% |
| C | LESSOUDA | 2 | 90 | SIDI BOUZID | 100.00% |
| C | EL KHALIJ | 2 | 82 | SFAX | 98.78% |
| C | BAB EL KHADRA | 2 | 80 | TUNIS | 100.00% |
| C | CITE MODERNE | 2 | 69 | GAFSA | 100.00% |
| C | EL AROUSSA | 2 | 68 | SILIANA | 100.00% |
| C | JAAFAR 2 | 2 | 62 | ARIANA | 100.00% |
| C | TYNA | 2 | 62 | SFAX | 100.00% |
| C | ERRAJA | 2 | 61 | MEDENINE | 98.36% |
| C | EL FEJJA | 2 | 57 | MANNOUBA | 98.25% |
| C | EL MAHASSEN | 2 | 56 | TOZEUR | 100.00% |
| C | SIDI EL BECHIR | 2 | 56 | TUNIS | 100.00% |
| C | CITE DE LE LIBERTE | 2 | 56 | SFAX | 96.43% |
| C | EL HEKAIMA | 2 | 56 | MAHDIA | 100.00% |
| C | BENI KALTHOUM | 2 | 50 | SOUSSE | 100.00% |
| C | JERBA AEROPORT | 2 | 48 | MEDENINE | 100.00% |
| C | CHATT ESSALEM | 2 | 46 | GABES | 100.00% |
| C | OULED SALAH | 2 | 45 | MAHDIA | 100.00% |
| C | CITE ALI BOURGUIBA | 2 | 39 | ARIANA | 100.00% |
| C | ERRISSALA | 2 | 38 | BEN AROUS | 100.00% |
| C | OUED CHAABOUNI | 2 | 37 | SFAX | 100.00% |
| C | CITE DES JUGES 2 | 2 | 36 | TUNIS | 97.22% |
| C | BERGES DU LAC | 2 | 36 | TUNIS | 100.00% |
| C | MENZEL HARB | 2 | 34 | MONASTIR | 100.00% |
| C | ARGOUB ERROUMI | 2 | 34 | MANNOUBA | 100.00% |
| C | SOUSSE CORNICHE | 2 | 29 | SOUSSE | 100.00% |
| C | CITE BEN AROUS | 2 | 29 | BIZERTE | 96.55% |
| C | BIR DRASSEN | 2 | 28 | NABEUL | 100.00% |
| C | GHIZEN | 2 | 27 | MEDENINE | 100.00% |
| C | MENZEL BEL OUAER | 2 | 27 | SOUSSE | 100.00% |
| C | MENZEL MHIRI | 2 | 25 | KAIROUAN | 96.00% |
| C | TOUJANE | 2 | 25 | GABES | 100.00% |
| C | BIR TAIEB | 2 | 25 | MONASTIR | 100.00% |
| C | EL MAISRA | 2 | 23 | NABEUL | 100.00% |
| C | OULED AMEUR | 2 | 23 | SOUSSE | 100.00% |
| C | GHENADA | 2 | 21 | MONASTIR | 100.00% |
| C | ESSAADI | 2 | 20 | SFAX | 100.00% |
| C | KSAR HELAL RIADH | 2 | 18 | MONASTIR | 100.00% |
| C | METHLINE | 2 | 17 | BIZERTE | 100.00% |
| C | SIDI AICH | 2 | 17 | GAFSA | 100.00% |
| C | CITE EL WAHAT | 2 | 16 | TUNIS | 100.00% |
| C | BIR EL KASSAA | 2 | 16 | BEN AROUS | 100.00% |
| C | BAGHDADI | 2 | 16 | MONASTIR | 100.00% |
| C | CITE PRESIDENT | 2 | 15 | GAFSA | 100.00% |
| C | CAP ZBIB | 2 | 14 | BIZERTE | 100.00% |
| C | BORJ ZOUARA | 2 | 13 | TUNIS | 100.00% |
| C | EL OUERDIA 5 | 2 | 13 | TUNIS | 100.00% |
| C | CHAAL | 2 | 13 | SFAX | 100.00% |
| C | EL LOUZA | 2 | 13 | SFAX | 100.00% |
| C | EL MOUTBASTA | 2 | 11 | KAIROUAN | 100.00% |
| C | BENI ABDELAZIZ | 2 | 10 | NABEUL | 100.00% |
| C | CITE BAB ETTOUB | 2 | 10 | GAFSA | 100.00% |
| C | EL GUEBLINE | 2 | 9 | MEDENINE | 100.00% |
| C | ESSALAMA | 2 | 8 | SIDI BOUZID | 100.00% |
| C | ESSAAD | 2 | 8 | MAHDIA | 100.00% |
| C | BIR HEDDI | 2 | 7 | KEF | 100.00% |
| C | OULED MNASSER | 2 | 7 | SIDI BOUZID | 100.00% |
| C | BARGUIA | 2 | 7 | GABES | 100.00% |
| C | CITE EL JAZIA | 2 | 7 | MONASTIR | 100.00% |
| C | CITE AZAIEZ | 2 | 6 | GABES | 100.00% |
| C | CITE 02 MARS | 2 | 6 | BEJA | 100.00% |
| C | ZAOUET SOUSSE | 2 | 6 | SOUSSE | 100.00% |
| C | CITE BOU JAAFAR | 2 | 6 | NABEUL | 100.00% |
| C | STEG | 2 | 6 | SILIANA | 100.00% |
| C | GAFSA GARE | 2 | 6 | GAFSA | 100.00% |
| C | JARDINS EL MENZAH 2 | 2 | 5 | ARIANA | 100.00% |
| C | KEF DERBI | 2 | 5 | GAFSA | 100.00% |
| C | EL MOUISSETTE | 2 | 5 | SOUSSE | 100.00% |
| C | 2 MARS | 2 | 4 | ARIANA | 100.00% |
| C | EL MANAR 3 | 2 | 4 | TUNIS | 100.00% |
| C | RUE IBN KHOLDOUN | 2 | 4 | SOUSSE | 100.00% |
| C | CITE ELKHADHRA | 2 | 3 | MANNOUBA | 100.00% |
| C | RAININE | 2 | 3 | NABEUL | 100.00% |
| C | SIDI MBAREK | 2 | 3 | BEJA | 100.00% |
| C | DAR CHAAABNE | 2 | 3 | NABEUL | 100.00% |
| C | SAHLOUL3 | 2 | 3 | SOUSSE | 100.00% |
| C | JAMEL | 2 | 3 | MONASTIR | 100.00% |
| C | CITE GOURRAIA | 2 | 3 | MONASTIR | 100.00% |
| C | BOUKHZAR | 2 | 3 | SOUSSE | 100.00% |
| C | BOREJ LOUZIR | 2 | 3 | ARIANA | 100.00% |
| C | ARIANA SOGHRA | 2 | 2 | ARIANA | 100.00% |
| C | CITE NASSER | 2 | 2 | MANNOUBA | 100.00% |
| C | CITE EZZOUHOUR 4 | 2 | 2 | GAFSA | 100.00% |
| C | EL MENZAH 7 BIS | 2 | 2 | ARIANA | 100.00% |
| C | EL HAWARIA | 2 | 2 | NABEUL | 100.00% |
| C | DAR CHAABEN | 2 | 2 | NABEUL | 100.00% |
| C | BIR CHELLOUF | 2 | 2 | NABEUL | 100.00% |
| C | ESSBIKHA | 2 | 2 | KAIROUAN | 100.00% |
| C | HAMAM SOUSSE | 2 | 2 | SOUSSE | 100.00% |
| C | KHZEMA | 2 | 2 | SOUSSE | 100.00% |
| C | SAHLOUL1 | 2 | 2 | SOUSSE | 100.00% |
| C | NKHILET | 2 | 2 | ARIANA | 100.00% |
| C | EL MOUROUJ6 | 2 | 2 | BEN AROUS | 100.00% |
| C | BIZETE | 2 | 2 | BIZERTE | 100.00% |
| C | MDHILA | 2 | 2 | GAFSA | 100.00% |
| C | KELIBIA CHARGUIA | 2 | 1 | NABEUL | 100.00% |
| C | MANZEH 8 | 2 | 1 | SOUSSE | 100.00% |
| C | MANZEH 5 | 2 | 1 | ARIANA | 100.00% |
| C | NOGRA | 2 | 1 | ARIANA | 100.00% |
| C | BAB SADOUN | 2 | 1 | TUNIS | 100.00% |
| C | EL KHADRA | 2 | 1 | TUNIS | 100.00% |
| C | MENZAH 4 | 2 | 1 | TUNIS | 100.00% |
| C | EL OUARDIA1 | 2 | 1 | TUNIS | 100.00% |
| C | CITE AMEL | 2 | 1 | GAFSA | 100.00% |
| C | M HAMDIA | 2 | 1 | BEN AROUS | 100.00% |
| C | GAMMATH | 2 | 1 | TUNIS | 100.00% |
| C | MANZEH | 2 | 1 | TUNIS | 100.00% |
| C | JARDINS DE L'AOUINA | 2 | 1 | ARIANA | 100.00% |
| C | JARDINS MENZAH | 2 | 1 | ARIANA | 100.00% |
| C | MHEMDIA | 2 | 1 | BEN AROUS | 100.00% |
| C | SOMMA | 2 | 1 | NABEUL | 100.00% |
| C | MENZEH 6 | 2 | 1 | TUNIS | 100.00% |
| C | HAMMAMT | 2 | 1 | NABEUL | 100.00% |
| C | CHRAF | 2 | 1 | BEKALTA | 100.00% |
| C | SEBIBA | 2 | 1 | KASSERINE | 100.00% |
| C | MORNAGUI | 2 | 1 | A | 100.00% |
| C | EL OUARDIA 4 | 2 | 1 | TUNIS | 100.00% |
| C | JDEIDA | 2 | 1 | ARIANA | 100.00% |
| C | EL MOUROUJ II | 2 | 1 | BEN AROUS | 100.00% |
| C | RUE MAHMOUD MATRI | 2 | 1 | MONASTIR | 100.00% |
| C | ML JMIL | 2 | 1 | BIZERTE | 100.00% |
| C | CITE ENOUR | 2 | 1 | GAFSA | 100.00% |
| C | UITIQUE | 2 | 1 | BIZERTE | 100.00% |
| C | BIR JEDEY | 2 | 1 | NABEUL | 100.00% |
| C | HAJEB AYOUN | 2 | 1 | KAIROUAN | 100.00% |
| C | THERAYET | 2 | 1 | SOUSSE | 100.00% |
| C | ENNACER | 2 | 1 | MANNOUBA | 100.00% |
| C | DOGGA | 2 | 1 | BEJA | 100.00% |
| C | RADES MALEHA | 2 | 1 | BEN AROUS | 100.00% |
| C | MORNAGIA | 2 | 1 | TUNIS | 100.00% |
| C | SIDI HENI | 2 | 1 | SOUSSE | 100.00% |
| C | MESAADINE | 2 | 1 | SOUSSE | 100.00% |
| C | HAMA | 2 | 1 | GABES | 100.00% |
| C | CITÉ CHORFA | 2 | 1 | GABES | 100.00% |
| C | TEJROUINE | 2 | 1 | KEF | 100.00% |
| C | DAHMENI | 2 | 1 | KEF | 100.00% |
| C | JEM | 2 | 1 | MAHDIA | 100.00% |
| C | OUARDANIN | 2 | 1 | MONASTIR | 100.00% |
| C | ZERMDINE | 2 | 1 | MONASTIR | 100.00% |
| C | CITE 20MARS | 2 | 1 | ZAGHOUAN | 100.00% |
| C | MENZEL ENOUR | 2 | 1 | MONASTIR | 100.00% |
| C | ENASER | 2 | 1 | MNIHLA | 100.00% |
| C | TAIEB MAHIRI | 2 | 1 | SILIANA | 100.00% |
| C | CITE EZOUHOUR | 2 | 1 | SOUSSE | 100.00% |
| C | JARDIN D'EL MENZAH | 2 | 1 | TUNIS | 100.00% |
| C | CITE EZDIHAR | 2 | 1 | BEN AROUS | 100.00% |
| C | AIN KMICHA | 2 | 1 | NABEUL | 100.00% |
| C | EL ZAHRA | 2 | 1 | BEN AROUS | 100.00% |
| C | EL METLINE | 2 | 1 | BIZERTE | 100.00% |
| C | CITE MED ALI | 2 | 1 | GABES | 100.00% |
| C | EL MRAZKA HAMMAMET | 2 | 1 | NABEUL | 100.00% |
| C | SAHLOUL I | 2 | 1 | SOUSSE | 100.00% |
| C | MASDOUR | 2 | 1 | MONASTIR | 100.00% |
| C | EL OUARDIA 5 | 2 | 1 | TUNIS | 100.00% |
| C | BOREJ EL AMRI | 2 | 1 | MANNOUBA | 100.00% |
| C | WESLATIA | 2 | 1 | KAIROUAN | 100.00% |
| C | LE BELVEDERE | 2 | 1 | TUNIS | 100.00% |
| C | MARSA ERRIADH | 1 | 636 | TUNIS | 100.00% |
| C | MENZEL ABDERRAHMAN | 1 | 412 | BIZERTE | 100.00% |
| C | ETTAHRIR 1 | 1 | 400 | TUNIS | 100.00% |
| C | BOU HAJLA | 1 | 376 | KAIROUAN | 100.00% |
| C | EL MELLASSINE | 1 | 370 | TUNIS | 100.00% |
| C | CARTAGE BYRSA | 1 | 253 | TUNIS | 100.00% |
| C | FONDOUK JEDID | 1 | 229 | NABEUL | 100.00% |
| C | OULED CHAMAKH | 1 | 176 | MAHDIA | 100.00% |
| C | BAB MENARA | 1 | 173 | TUNIS | 100.00% |
| C | FAYEDH | 1 | 152 | SIDI BOUZID | 100.00% |
| C | SOUSSE KHEZAMA | 1 | 151 | SOUSSE | 100.00% |
| C | JEBEL EL OUST | 1 | 148 | ZAGHOUAN | 100.00% |
| C | CITE EL BAHRI | 1 | 121 | SFAX | 100.00% |
| C | MENZEL HEDI CHAKER | 1 | 105 | SFAX | 100.00% |
| C | AMRA NOUVELLE | 1 | 105 | MEDENINE | 100.00% |
| C | CITE 25 JUILLET | 1 | 99 | TUNIS | 100.00% |
| C | KAIROUAN SUD | 1 | 90 | KAIROUAN | 100.00% |
| C | CITE BIR REMEL | 1 | 86 | BIZERTE | 100.00% |
| C | BAB EL JAZIRA | 1 | 80 | TUNIS | 100.00% |
| C | CHEBEDDA | 1 | 77 | BEN AROUS | 100.00% |
| C | HEDI CHAKER | 1 | 76 | TUNIS | 98.68% |
| C | BOU HAJAR | 1 | 72 | MONASTIR | 100.00% |
| C | AIN LANSARINE | 1 | 70 | ZAGHOUAN | 100.00% |
| C | MELLITA JERBA | 1 | 67 | MEDENINE | 100.00% |
| C | SIDI ABBES | 1 | 66 | SFAX | 100.00% |
| C | OUM ETTAMAR | 1 | 62 | MEDENINE | 100.00% |
| C | UTIQUE NOUVELLE | 1 | 61 | BIZERTE | 100.00% |
| C | EL AMAIEM | 1 | 61 | ZAGHOUAN | 98.36% |
| C | BORJ CHAKIR | 1 | 59 | TUNIS | 100.00% |
| C | CITE BELVEDERE 2 | 1 | 58 | ARIANA | 100.00% |
| C | MERKEZ CHAABOUNI | 1 | 56 | SFAX | 100.00% |
| C | KSAR JEDID | 1 | 52 | MEDENINE | 100.00% |
| C | JEMNA | 1 | 52 | KEBILI | 100.00% |
| C | EL AOUABED | 1 | 48 | SFAX | 100.00% |
| C | EL HAJEB | 1 | 47 | SFAX | 100.00% |
| C | SIDI SMAIL | 1 | 47 | BEJA | 100.00% |
| C | CITE EL FAOUZ | 1 | 46 | BEN AROUS | 97.83% |
| C | SALAH | 1 | 46 | SILIANA | 100.00% |
| C | BOU HELAL | 1 | 45 | TOZEUR | 97.78% |
| C | EL BOUSTEN | 1 | 41 | SFAX | 100.00% |
| C | MEGHIRA INZEL | 1 | 40 | BEN AROUS | 100.00% |
| C | CHAMMAKH | 1 | 40 | MEDENINE | 100.00% |
| C | EL HALFAOUINE | 1 | 38 | TUNIS | 100.00% |
| C | ROBBANA | 1 | 36 | MEDENINE | 100.00% |
| C | MERKEZ BOUACIDA | 1 | 35 | SFAX | 100.00% |
| C | EL YASMINA | 1 | 35 | TUNIS | 100.00% |
| C | BORJ ETTOUMI | 1 | 35 | MANNOUBA | 100.00% |
| C | BEN FARJALLAH | 1 | 35 | TOZEUR | 100.00% |
| C | BAYOUB | 1 | 34 | NABEUL | 100.00% |
| C | CITE EL OMRANE 1 | 1 | 34 | BIZERTE | 100.00% |
| C | OUED ZARGA | 1 | 33 | BEJA | 100.00% |
| C | GARGOUR | 1 | 33 | SFAX | 100.00% |
| C | MSAKEN EL GUEBLIA | 1 | 33 | SOUSSE | 100.00% |
| C | AIN EL KHARARIB | 1 | 33 | JENDOUBA | 96.97% |
| C | CITE SAHLOUL | 1 | 32 | SOUSSE | 100.00% |
| C | TANTANA | 1 | 32 | SOUSSE | 100.00% |
| C | OUM SOMAA | 1 | 32 | KEBILI | 100.00% |
| C | CITE ERRIADH 1 | 1 | 32 | MONASTIR | 96.88% |
| C | BATROU | 1 | 30 | NABEUL | 100.00% |
| C | ZAOUIET JEDIDI | 1 | 30 | NABEUL | 100.00% |
| C | AIN JELLOULA | 1 | 29 | KAIROUAN | 100.00% |
| C | GRIBIS | 1 | 29 | MEDENINE | 100.00% |
| C | JERADOU | 1 | 28 | ZAGHOUAN | 96.43% |
| C | CITE ESSAHAFA | 1 | 28 | ARIANA | 100.00% |
| C | OUED RMAL | 1 | 27 | SFAX | 100.00% |
| C | CITE 2000 | 1 | 27 | SFAX | 100.00% |
| C | EL KANTAOUI | 1 | 26 | SOUSSE | 100.00% |
| C | EL HEDADRA | 1 | 26 | MONASTIR | 100.00% |
| C | BOU SAID | 1 | 26 | SFAX | 100.00% |
| C | EL BATEN | 1 | 26 | KAIROUAN | 100.00% |
| C | ENNAGR | 1 | 26 | SOUSSE | 100.00% |
| C | CITE WED LARTA | 1 | 26 | GAFSA | 100.00% |
| C | CITE BOU HJAR | 1 | 25 | TUNIS | 100.00% |
| C | MAHBOUBINE | 1 | 25 | MEDENINE | 100.00% |
| C | SIDI ALI CHEBAB | 1 | 25 | BIZERTE | 96.00% |
| C | MAGHRAOUA | 1 | 25 | BIZERTE | 96.00% |
| C | CITE HACHED 2 | 1 | 24 | BEN AROUS | 95.83% |
| C | EL KRARIA | 1 | 23 | SOUSSE | 95.65% |
| C | CITE EL MANDRA | 1 | 22 | NABEUL | 95.45% |
| C | CITE ENNAJET | 1 | 22 | MANNOUBA | 100.00% |
| C | GUECHIINE | 1 | 22 | MEDENINE | 100.00% |
| C | MERKEZ DEROUICHE | 1 | 21 | SFAX | 100.00% |
| C | ZAOUIET EL MGAIES | 1 | 21 | NABEUL | 100.00% |
| C | EL HABIBIA | 1 | 21 | MANNOUBA | 100.00% |
| C | BEDAR | 1 | 21 | NABEUL | 95.24% |
| C | HICHER | 1 | 21 | SOUSSE | 95.24% |
| C | CITE EL MAHRSI 1 | 1 | 20 | NABEUL | 100.00% |
| C | CITE EL MOUROUJ 3 | 1 | 20 | BEN AROUS | 95.00% |
| C | DHRAA | 1 | 20 | SIDI BOUZID | 100.00% |
| C | SFAX PORT | 1 | 20 | SFAX | 100.00% |
| C | CASINO LA GOULETTE | 1 | 19 | TUNIS | 100.00% |
| C | MENZEL KHIR | 1 | 19 | MONASTIR | 100.00% |
| C | MHIRIS | 1 | 18 | ZAGHOUAN | 100.00% |
| C | BECHKA | 1 | 18 | SFAX | 100.00% |
| C | MEZRAYA | 1 | 17 | MEDENINE | 100.00% |
| C | RUE BOUCHOUCHA | 1 | 17 | SOUSSE | 100.00% |
| C | SAKIET EL KHADEM | 1 | 17 | MAHDIA | 100.00% |
| C | BENI MAAGUEL | 1 | 17 | MEDENINE | 100.00% |
| C | CITE ABDRABBAH 1 | 1 | 17 | SILIANA | 100.00% |
| C | EL AKARIT | 1 | 17 | GABES | 100.00% |
| C | SAHEB JEBEL | 1 | 16 | NABEUL | 100.00% |
| C | SIDI BOUBAKER | 1 | 16 | GAFSA | 100.00% |
| C | TLELSA | 1 | 15 | MAHDIA | 100.00% |
| C | CITE HEDI NOUIRA | 1 | 15 | ARIANA | 100.00% |
| C | OUED EZZIT | 1 | 15 | ZAGHOUAN | 100.00% |
| C | EL AKHOUAT | 1 | 15 | SILIANA | 100.00% |
| C | MENZEL HACHED | 1 | 14 | MAHDIA | 100.00% |
| C | KSAR EL JIRA | 1 | 14 | MEDENINE | 100.00% |
| C | CITE EL EZZ | 1 | 14 | BEN AROUS | 100.00% |
| C | OUED BEJA | 1 | 14 | MAHDIA | 100.00% |
| C | JERSINE | 1 | 14 | KEBILI | 100.00% |
| C | OUM EL ADHAM | 1 | 14 | SIDI BOUZID | 100.00% |
| C | EL MAKAREM | 1 | 14 | SIDI BOUZID | 100.00% |
| C | BAB EL FALLA | 1 | 13 | TUNIS | 100.00% |
| C | DOUALY GAFSA | 1 | 13 | GAFSA | 100.00% |
| C | AIN REKOUB | 1 | 13 | BIZERTE | 100.00% |
| C | LABAYEDH | 1 | 13 | SIDI BOUZID | 100.00% |
| C | BENI HAZAM | 1 | 13 | SILIANA | 100.00% |
| C | NOUVELLE ZRAOUA | 1 | 12 | GABES | 100.00% |
| C | AIN SAYADA | 1 | 12 | KAIROUAN | 100.00% |
| C | AIN ESSNOUSSI | 1 | 12 | JENDOUBA | 100.00% |
| C | AIN ACHOUR | 1 | 12 | SILIANA | 100.00% |
| C | BENI ZELTEN | 1 | 11 | GABES | 100.00% |
| C | CARTAGE | 1 | 10 | TUNIS | 100.00% |
| C | TOUIBIA | 1 | 10 | BIZERTE | 100.00% |
| C | MENZEL MIMOUN | 1 | 10 | GAFSA | 100.00% |
| C | CITE ESSADAKA | 1 | 10 | BIZERTE | 100.00% |
| C | OUED EL KHATEF | 1 | 10 | NABEUL | 100.00% |
| C | RIADH 2 | 1 | 9 | SILIANA | 100.00% |
| C | SIDI MEHREZ | 1 | 9 | MEDENINE | 100.00% |
| C | CITE BRIK | 1 | 9 | MANNOUBA | 100.00% |
| C | SIDI SHIL | 1 | 9 | KASSERINE | 100.00% |
| C | REMATHI | 1 | 9 | GABES | 100.00% |
| C | ZELBA | 1 | 9 | MAHDIA | 100.00% |
| C | DHOUIBETTE | 1 | 9 | SIDI BOUZID | 100.00% |
| C | CITE DES JEUNNES | 1 | 9 | GAFSA | 100.00% |
| C | ALI BACH-HAMBA | 1 | 8 | TUNIS | 100.00% |
| C | EL TAOUFIK | 1 | 8 | TUNIS | 100.00% |
| C | AIN OUM JDOUR | 1 | 8 | KASSERINE | 100.00% |
| C | CITE EL BICHER | 1 | 8 | TATAOUINE | 100.00% |
| C | AIN EL HAMMAM | 1 | 7 | BEJA | 100.00% |
| C | CITE EL FETH | 1 | 7 | ARIANA | 100.00% |
| C | CITE CALYPTUS | 1 | 7 | BIZERTE | 100.00% |
| C | KSAR SAAD | 1 | 7 | NABEUL | 100.00% |
| C | AIN YOUNES | 1 | 7 | BEJA | 100.00% |
| C | EL HOUS | 1 | 7 | MAHDIA | 100.00% |
| C | GATRANA | 1 | 7 | SIDI BOUZID | 100.00% |
| C | CITE EL OMRANE 2 | 1 | 6 | BIZERTE | 100.00% |
| C | RAFRAF PLAGE | 1 | 6 | BIZERTE | 100.00% |
| C | CITE CASERNE | 1 | 6 | TATAOUINE | 100.00% |
| C | L INDEPENDANCE | 1 | 6 | SILIANA | 100.00% |
| C | LAKHOUET | 1 | 6 | SILIANA | 100.00% |
| C | BOUTIQUE ISSA | 1 | 5 | SIDI BOUZID | 100.00% |
| C | CITE KHALIL | 1 | 5 | TUNIS | 100.00% |
| C | BOUCHA | 1 | 5 | ZAGHOUAN | 100.00% |
| C | SOUGHAS | 1 | 5 | ZAGHOUAN | 100.00% |
| C | ARKOU | 1 | 5 | MEDENINE | 100.00% |
| C | MAJOURA | 1 | 5 | GAFSA | 100.00% |
| C | CHAHDA | 1 | 5 | MAHDIA | 100.00% |
| C | BOU ATTOUCH | 1 | 5 | SIDI BOUZID | 100.00% |
| C | BATEN EL AGAAG | 1 | 5 | SIDI BOUZID | 100.00% |
| C | BORJ MESSAOUDI | 1 | 5 | SILIANA | 100.00% |
| C | EL HBABSA | 1 | 5 | SILIANA | 100.00% |
| C | CITE ZARROUK | 1 | 5 | BIZERTE | 100.00% |
| C | KEBILI BEYEZ | 1 | 4 | KEBILI | 100.00% |
| C | AGUEGCHA | 1 | 4 | SFAX | 100.00% |
| C | CITE EQUIPEMENT | 1 | 4 | ZAGHOUAN | 100.00% |
| C | AIN BATTOUM | 1 | 4 | ZAGHOUAN | 100.00% |
| C | EZZAOUIA | 1 | 4 | ARIANA | 100.00% |
| C | MREZGA | 1 | 4 | NABEUL | 100.00% |
| C | SFAYA | 1 | 4 | SOUSSE | 100.00% |
| C | OUED LARTA | 1 | 4 | GAFSA | 100.00% |
| C | CHOUARIA | 1 | 4 | MAHDIA | 100.00% |
| C | BIR GZAIEL | 1 | 4 | SIDI BOUZID | 100.00% |
| C | ONS | 1 | 4 | SILIANA | 100.00% |
| C | ONES | 1 | 4 | SILIANA | 100.00% |
| C | GABES EL HIDAYA | 1 | 4 | GABES | 100.00% |
| C | BOUHCINA | 1 | 3 | SOUSSE | 100.00% |
| C | EL HALFA | 1 | 3 | NABEUL | 100.00% |
| C | GOUBRAR | 1 | 3 | SIDI BOUZID | 100.00% |
| C | TOUAHRA | 1 | 3 | MAHDIA | 100.00% |
| C | MANZEL NOUR | 1 | 3 | MONASTIR | 100.00% |
| C | PLACE PASTEUR | 1 | 2 | GAFSA | 100.00% |
| C | REBAT | 1 | 2 | MONASTIR | 100.00% |
| C | SKANES MONASTIR | 1 | 2 | MONASTIR | 100.00% |
| C | EL OUERDIA 3 | 1 | 2 | TUNIS | 100.00% |
| C | EL MENZAH 9 A | 1 | 2 | TUNIS | 100.00% |
| C | GHARMANE | 1 | 2 | NABEUL | 100.00% |
| C | CHBIKA | 1 | 2 | KAIROUAN | 100.00% |
| C | BAB BLED | 1 | 2 | BEJA | 100.00% |
| C | CITE EL WARD | 1 | 2 | BEN AROUS | 100.00% |
| C | SIDI ACHOUR | 1 | 2 | NABEUL | 100.00% |
| C | KESIBET SOUSSE | 1 | 2 | SOUSSE | 100.00% |
| C | CITE BOUHSINA | 1 | 2 | SOUSSE | 100.00% |
| C | SOUISSE | 1 | 2 | SOUSSE | 100.00% |
| C | SIDI ELHANI | 1 | 2 | SOUSSE | 100.00% |
| C | ZAOUIA | 1 | 2 | SOUSSE | 100.00% |
| C | EL MANZAH | 1 | 2 | ARIANA | 100.00% |
| C | GHOMRASSAN | 1 | 2 | TATAOUINE | 100.00% |
| C | BLED | 1 | 2 | GABES | 100.00% |
| C | CITE JELAILA | 1 | 2 | KEBILI | 100.00% |
| C | AIN EL HENCHIR | 1 | 2 | KEF | 100.00% |
| C | WARDANINE | 1 | 2 | MONASTIR | 100.00% |
| C | SKANESS | 1 | 2 | MONASTIR | 100.00% |
| C | BIR EL AKERMA | 1 | 2 | SIDI BOUZID | 100.00% |
| C | HAMEM SOUSSE | 1 | 2 | SOUSSE | 100.00% |
| C | SILANA | 1 | 2 | SILIANA | 100.00% |
| C | TUNIS EL HAFSIA | 1 | 2 | TUNIS | 100.00% |
| C | BORJ EL OUZIR | 1 | 2 | ARIANA | 100.00% |
| C | KSAR HDID | 1 | 2 | SILIANA | 100.00% |
| C | JARDIN EL MENZAH | 1 | 2 | ARIANA | 100.00% |
| C | EZZOHOUR | 1 | 2 | TUNIS | 100.00% |
| C | RUE OMAR IBN EL KHATTAB | 1 | 2 | SOUSSE | 100.00% |
| C | TAOURIT | 1 | 2 | MEDENINE | 100.00% |
| C | CEGDEL | 1 | 2 | SIDI BOUZID | 100.00% |
| C | ELBASSATINE | 1 | 2 | MANNOUBA | 100.00% |
| C | CITE OUM KETHIR | 1 | 2 | JENDOUBA | 100.00% |
| C | BERGES DU LAC 2 | 1 | 1 | TUNIS | 100.00% |
| C | NORD | 1 | 1 | 1610-041100 | 100.00% |
| C | CITE GHAZELLE | 1 | 1 | TUNIS | 100.00% |
| C | URBAIN NORD | 1 | 1 | TUNIS | 100.00% |
| C | EL HABIB | 1 | 1 | SFAX | 100.00% |
| C | EZZOUHOUR 3 | 1 | 1 | TUNIS | 100.00% |
| C | AIN ZAGHUAN | 1 | 1 | TUNIS | 100.00% |
| C | CARTHAGE PRÉSIDENCE | 1 | 1 | TUNIS | 100.00% |
| C | EL OUARDI | 1 | 1 | TUNIS | 100.00% |
| C | JAWHRA | 1 | 1 | SOUSSE | 100.00% |
| C | BOUA RADA | 1 | 1 | SILIANA | 100.00% |
| C | JBEL LAHMER | 1 | 1 | TUNIS | 100.00% |
| C | CARTHAGE SALAMBO | 1 | 1 | TUNIS | 100.00% |
| C | BIR EL JEDAY | 1 | 1 | NABEUL | 100.00% |
| C | JASMIN | 1 | 1 | SILIANA | 100.00% |
| C | CITE ENTILAKA | 1 | 1 | BIZERTE | 100.00% |
| C | ZAGHOIAN | 1 | 1 | NABEUL | 100.00% |
| C | EL MENZEH | 1 | 1 | TUNIS | 100.00% |
| C | KALAAT EL ANDALOUS | 1 | 1 | ARIANA | 100.00% |
| C | FARHAT HACHED | 1 | 1 | SILIANA | 100.00% |
| C | MORNAGGUIA | 1 | 1 | MANNOUBA | 100.00% |
| C | MORNEGUE | 1 | 1 | BEN AROUS | 100.00% |
| C | LES JARDINS D'EL MENZAH 2 | 1 | 1 | ARIANA | 100.00% |
| C | CHARCHARA | 1 | 1 | ZAGHOUAN | 100.00% |
| C | SAKIET EDDAYER | 1 | 1 | SFAX | 100.00% |
| C | SIDI BOUZIDI | 1 | 1 | MONASTIR | 100.00% |
| C | HAI EL KHIRI | 1 | 1 | SFAX | 100.00% |
| C | MENZEL DJEMIL | 1 | 1 | BIZERTE | 100.00% |
| C | MANZEL ABDERAHMEN | 1 | 1 | BIZERTE | 100.00% |
| C | CITE FARHAT HACHED | 1 | 1 | BEN AROUS | 100.00% |
| C | CITE MOUROUJ | 1 | 1 | MOUNASTIR | 100.00% |
| C | TUNIS 1 | 1 | 1 | TUNIS | 100.00% |
| C | AIREG SASSE | 1 | 1 | NABEUL | 100.00% |
| C | MALOUL | 1 | 1 | NABEUL | 100.00% |
| C | BORJ SIDRIA | 1 | 1 | BEN AROUSS | 100.00% |
| C | RUE SAADA | 1 | 1 | GABES | 100.00% |
| C | ALA | 1 | 1 | KAIROUAN | 100.00% |
| C | ELALA | 1 | 1 | KAIROUAN | 100.00% |
| C | ELMANAR 2 | 1 | 1 | TUNIS | 100.00% |
| C | JAAFER 2 | 1 | 1 | ARIANA | 100.00% |
| C | GBOLLATE | 1 | 1 | BEJA | 100.00% |
| C | JARDINS DU LAC | 1 | 1 | TUNIS | 100.00% |
| C | MATER | 1 | 1 | BIZERT | 100.00% |
| C | CITE REPUBLIQUE | 1 | 1 | ARIANA | 100.00% |
| C | KASSEINE | 1 | 1 | KASSERINE | 100.00% |
| C | RMADA | 1 | 1 | MONASTIR | 100.00% |
| C | GRIMIT | 1 | 1 | SOUSSE | 100.00% |
| C | GSAR | 1 | 1 | GAFSA | 100.00% |
| C | CITE NACER | 1 | 1 | GAFSA | 100.00% |
| C | CITE IBNOU KHOULDOUN | 1 | 1 | GAFSA | 100.00% |
| C | EZZOUHOUR 1 | 1 | 1 | TUNIS | 100.00% |
| C | NAHEL | 1 | 1 | GABES | 100.00% |
| C | DOUZE | 1 | 1 | GBELLI | 100.00% |
| C | HAMMEM CHATT | 1 | 1 | BEN AROUS | 100.00% |
| C | CITE 3 AOUT | 1 | 1 | KEF | 100.00% |
| C | OMRAN SUP | 1 | 1 | OMRAN SU | 100.00% |
| C | BAB BRAH | 1 | 1 | TUNIS | 100.00% |
| C | MSEKEN | 1 | 1 | SOUSSE | 100.00% |
| C | TUNIS MEDINA | 1 | 1 | TUNIS | 100.00% |
| C | ELMENZAH | 1 | 1 | ELMENZAH | 100.00% |
| C | OUERDENINE | 1 | 1 | MONASTIR | 100.00% |
| C | SAYDA | 1 | 1 | MONASTIR | 100.00% |
| C | JEMEL | 1 | 1 | SIDI BOUZID | 100.00% |
| C | BANNANE | 1 | 1 | MONASTIR | 100.00% |
| C | BIR HFAY | 1 | 1 | SIDI BOUZID | 100.00% |
| C | SBZ OUEST | 1 | 1 | SIDI BOUZID | 100.00% |
| C | HABIB BOURGUIBA | 1 | 1 | SILIANA | 100.00% |
| C | CARTHAGE YASMINA | 1 | 1 | TUNIS | 100.00% |
| C | MESKIA 2 | 1 | 1 | SILIANA | 100.00% |
| C | BOUAARADA | 1 | 1 | SELIANA | 100.00% |
| C | SILIANAN | 1 | 1 | SILIANAN | 100.00% |
| C | BAB LAASAL | 1 | 1 | TUNIS | 100.00% |
| C | RUE ALI BELHOUANE | 1 | 1 | SILIANA | 100.00% |
| C | MELLASINE | 1 | 1 | TUNIS | 100.00% |
| C | EL MALASSINE | 1 | 1 | TUNIS | 100.00% |
| C | EL MANZAH 4 | 1 | 1 | TUNIS | 100.00% |
| C | BENI KHIAR PLAGE | 1 | 1 | NABEUL | 100.00% |
| C | ENTILAKA | 1 | 1 | MANNOUBA | 100.00% |
| C | NELL MEDINA | 1 | 1 | BEN AROUS | 100.00% |
| C | EL FOLLA | 1 | 1 | TUNIS | 100.00% |
| C | EL OUERDIA1 | 1 | 1 | TUNIS | 100.00% |
| C | CARTHAGE DERMECH | 1 | 1 | TUNIS | 100.00% |
| C | HAMMEM LAGHZEZ | 1 | 1 | NABEUL | 100.00% |
| C | DJEBAL JELOUD | 1 | 1 | TUNIS | 100.00% |
| C | RIADH ENNASER 2 | 1 | 1 | ARIANA | 100.00% |
| C | - | 1 | 1 | MANOUBA | 100.00% |
| C | MZL CHEKER | 1 | 1 | SFAX | 100.00% |
| C | ELOUINA | 1 | 1 | SOUSSE | 100.00% |
| C | CITE NARJES | 1 | 1 | TUNIS | 100.00% |
| C | NOUR JAAFAR | 1 | 1 | ARIANA | 100.00% |
| C | MARSA PLAGE | 1 | 1 | TUNIS | 100.00% |
| C | CITE ENNASIM | 1 | 1 | TUNIS | 100.00% |
| C | KODIET MALEK | 1 | 1 | SOUSSE | 100.00% |
| C | RUE 7 NOVEMBRE | 1 | 1 | SOUSSE | 100.00% |
| C | CITE ECHABEB | 1 | 1 | SOUSSE | 100.00% |
| C | BENI AOUF | 1 | 1 | BIZERTE | 100.00% |
| C | BORJ EL ADOUANI | 1 | 1 | BIZERTE | 100.00% |
| C | RAGOUBA | 1 | 1 | GAFSA | 100.00% |
| C | MERETH | 1 | 1 | GABES | 100.00% |
| C | BOU DHAFER | 1 | 1 | GABES | 100.00% |
| C | SIDI BOULBA | 1 | 1 | GABES | 100.00% |
| C | RUE AHMED TELILI | 1 | 1 | GABES | 100.00% |
| C | RUE MAKA | 1 | 1 | GABES | 100.00% |
| C | AIN ZAGHOUANE NORD | 1 | 1 | LA MARSA | 100.00% |
| C | PLAGE DE BENI KHIAR | 1 | 1 | BENI KHIAR | 100.00% |
| C | BNI KHIAR | 1 | 1 | NABEUL | 100.00% |
| C | CITE ROMMANA | 1 | 1 | TUNIS | 100.00% |
| C | ELMNARA | 1 | 1 | MONASTIR | 100.00% |
| C | SAHLIN | 1 | 1 | MONASTIR | 100.00% |
| C | KALLA KEBIRA | 1 | 1 | SOUSSE | 100.00% |
| C | BOUHAJER | 1 | 1 | MONASTIR | 100.00% |
| C | ZAOUIT KONTECH | 1 | 1 | MONASTIR | 100.00% |
| C | MANZEL KAMEL | 1 | 1 | MONASTIR | 100.00% |
| C | MEGRIN | 1 | 1 | BEN AROUS | 100.00% |
| C | KABARIYA | 1 | 1 | TUNIS | 100.00% |
| C | ELMOUROUJ 1 | 1 | 1 | BEN AROUS | 100.00% |
| C | CITE RABTA | 1 | 1 | BEN AROUS | 100.00% |
| C | CITE ELHANA | 1 | 1 | BEN AROUS | 100.00% |
| C | EL MANARA | 1 | 1 | BEN AROUS | 100.00% |
| C | MORNEGUIA | 1 | 1 | MANNOUBA | 100.00% |
| C | BORJ AMRI | 1 | 1 | MANNOUBA | 100.00% |
| C | CHARGUIA2 | 1 | 1 | ARIANA | 100.00% |
| C | ROUTE DE TOZEUR | 1 | 1 | GAFSA | 100.00% |
| C | CITE ONS | 1 | 1 | TUNIS | 100.00% |
| C | JARDIN EL MENZAH 1 | 1 | 1 | ARIANA | 100.00% |
| C | SISEB | 1 | 1 | KAIROUAN | 100.00% |
| C | RAWAD | 1 | 1 | ARIANA | 100.00% |
| C | GUASSRINE | 1 | 1 | GUASSRINE | 100.00% |
| C | CITE CHEAB | 1 | 1 | KASSERINE | 100.00% |
| C | CITE ETTAMIR | 1 | 1 | SOUSSE | 100.00% |
| C | SFAX SUD | 1 | 1 | SFAX | 100.00% |
| C | ROUABI | 1 | 1 | BIZERTE | 100.00% |
| C | DOUAR HICHR | 1 | 1 | MANNOUBA | 100.00% |
| C | HOUMT SOUK JERBA | 1 | 1 | MEDENINE | 100.00% |
| C | LAC1 | 1 | 1 | TUNIS | 100.00% |

## 8. Recommended Next Actions

- Review probable_moral_or_incomplete_profile as a diagnostic flag only; do not recode client type directly from these indicators.
- Implement any accepted personal-field cleanups later in etl/transform/clean_clients.py, before loading dim_client.
- Use the geographic candidate tables as review queues for deterministic normalization rules; keep a human-approved whitelist for corrections.
- Do not mutate iris_dw.dim_client directly; rerun the loader after transform-level fixes are approved.
