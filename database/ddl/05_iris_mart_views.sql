-- ============================================================
-- IRISv2 - 05_iris_mart_views.sql
-- Objectif : vues métier consommables
-- Schéma   : iris_mart
-- ============================================================


-- ============================================================
-- 1. vw_worklist_investigation
-- Objectif : liste priorisée des dossiers à examiner
-- Grain    : 1 ligne par sinistre × garantie
-- ============================================================

CREATE OR REPLACE VIEW iris_mart.vw_worklist_investigation AS
WITH active_fraud_run AS (
    SELECT run_id
    FROM iris_score.scoring_run
    WHERE run_type = 'FRAUD'
      AND is_active = true
      AND status = 'SUCCESS'
    LIMIT 1
),
active_vhs_run AS (
    SELECT run_id
    FROM iris_score.scoring_run
    WHERE run_type = 'VHS'
      AND is_active = true
      AND status = 'SUCCESS'
    LIMIT 1
),
rule_summary AS (
    SELECT
        frd.sinistre_sk,
        frd.run_id,
        COUNT(*) AS rules_triggered_count,
        STRING_AGG(frd.rule_code, ', ' ORDER BY frd.rule_code) AS triggered_rules
    FROM iris_score.fact_fraud_rule_detail frd
    GROUP BY frd.sinistre_sk, frd.run_id
),
latest_cross AS (
    SELECT DISTINCT ON (c.sinistre_sk)
        c.sinistre_sk,
        c.inspection_sk,
        c.score_cross,
        c.delai_inspection_sinistre_jours
    FROM iris_score.fact_inspection_sinistre_cross c
    JOIN active_fraud_run afr
        ON c.run_id = afr.run_id
    ORDER BY c.sinistre_sk, c.score_cross DESC NULLS LAST
)
SELECT
    ROW_NUMBER() OVER (
        ORDER BY
            CASE fs.risk_level
                WHEN 'ELEVE' THEN 1
                WHEN 'MOYEN' THEN 2
                WHEN 'FAIBLE' THEN 3
                WHEN 'NORMAL' THEN 4
                ELSE 5
            END,
            fs.score_global DESC NULLS LAST,
            f.montant_total DESC NULLS LAST
    ) AS rank_priority,

    f.sinistre_sk,
    f.num_sinistre,

    g.code_garantie,
    g.libelle_garantie,

    c.client_sk,
    c.num_client,
    c.code_nature_client,
    c.gouvernorat_client,

    ct.num_contrat,
    ct.num_avenant,
    ct.num_mise_a_jour,

    v.vehicule_sk,
    v.immatriculation,
    v.vin,
    v.marque,
    v.modele,

    p.code_produit,
    p.libelle_produit,

    d.date_val AS date_survenance,
    dd.date_val AS date_declaration,

    f.montant_total,
    f.montant_total_net,

    f.delai_declaration_jours,
    f.anciennete_contrat_jours,
    f.is_declaration_antidatee,
    f.is_declaration_tardive,
    f.is_sinistre_avant_contrat,
    f.is_sinistre_precoce,

    fs.score_rule_norm,
    fs.score_ml,
    fs.score_cross,
    fs.score_global,
    fs.risk_level,
    fs.confidence_level,

    rs.rules_triggered_count,
    rs.triggered_rules,

    vs.vhs_score_displayed,
    vs.safety_grade,
    vs.vhs_decision,
    vs.is_drivable,

    CASE
        WHEN fs.risk_level = 'ELEVE' THEN 'Priorité élevée selon scoring fraude'
        WHEN f.is_sinistre_avant_contrat THEN 'Sinistre avant début contrat'
        WHEN f.is_declaration_antidatee THEN 'Déclaration antidatée'
        WHEN f.is_declaration_tardive THEN 'Déclaration tardive'
        WHEN fs.score_ml IS NOT NULL AND fs.score_ml >= 0.50 THEN 'Comportement atypique détecté'
        WHEN rs.rules_triggered_count > 0 THEN 'Règles fraude déclenchées'
        ELSE 'Aucun signal majeur'
    END AS main_reason

FROM iris_dw.fact_sinistre f
LEFT JOIN iris_dw.dim_client c
    ON f.client_sk = c.client_sk
LEFT JOIN iris_dw.dim_contrat ct
    ON f.contrat_sk = ct.contrat_sk
LEFT JOIN iris_dw.dim_vehicule v
    ON f.vehicule_sk = v.vehicule_sk
LEFT JOIN iris_dw.dim_produit p
    ON f.produit_sk = p.produit_sk
LEFT JOIN iris_dw.dim_garantie g
    ON f.garantie_sk = g.garantie_sk
LEFT JOIN iris_dw.dim_date d
    ON f.date_survenance_sk = d.date_sk
LEFT JOIN iris_dw.dim_date dd
    ON f.date_declaration_sk = dd.date_sk
LEFT JOIN active_fraud_run afr
    ON true
LEFT JOIN iris_score.fact_fraud_score fs
    ON f.sinistre_sk = fs.sinistre_sk
   AND fs.run_id = afr.run_id
LEFT JOIN rule_summary rs
    ON f.sinistre_sk = rs.sinistre_sk
   AND rs.run_id = afr.run_id
LEFT JOIN latest_cross lc
    ON f.sinistre_sk = lc.sinistre_sk
LEFT JOIN active_vhs_run avr
    ON true
LEFT JOIN iris_score.fact_vhs_score vs
    ON lc.inspection_sk = vs.inspection_sk
   AND vs.run_id = avr.run_id;


COMMENT ON VIEW iris_mart.vw_worklist_investigation IS
'Liste priorisée des dossiers à examiner par le gestionnaire fraude.';


-- ============================================================
-- 2. vw_dossier_360
-- Objectif : fiche complète d’un dossier sinistre
-- Grain    : 1 ligne par sinistre × garantie
-- ============================================================

CREATE OR REPLACE VIEW iris_mart.vw_dossier_360 AS
WITH active_fraud_run AS (
    SELECT run_id
    FROM iris_score.scoring_run
    WHERE run_type = 'FRAUD'
      AND is_active = true
      AND status = 'SUCCESS'
    LIMIT 1
),
rule_summary AS (
    SELECT
        frd.sinistre_sk,
        frd.run_id,
        STRING_AGG(frd.rule_code, ', ' ORDER BY frd.rule_code) AS triggered_rules
    FROM iris_score.fact_fraud_rule_detail frd
    GROUP BY frd.sinistre_sk, frd.run_id
)
SELECT
    f.sinistre_sk,
    f.num_sinistre,
    f.sinistre_natural_key,

    c.client_sk,
    c.num_client,
    c.code_nature_client,
    c.sexe,
    c.date_naissance,
    c.gouvernorat_client,
    c.localite_client,

    ct.contrat_sk,
    ct.num_contrat,
    ct.num_avenant,
    ct.num_mise_a_jour,
    ct.situation_contrat,

    v.vehicule_sk,
    v.immatriculation,
    v.vin,
    v.marque,
    v.modele,
    v.genre_vehicule,
    v.usage_vehicule,

    p.code_produit,
    p.libelle_produit,

    g.code_garantie,
    g.libelle_garantie,

    cs.code_cause_sinistre,
    cs.code_nature_sinistre,
    cs.code_sous_nature_sinistre,

    ds.date_val AS date_survenance,
    dd.date_val AS date_declaration,
    doo.date_val AS date_ouverture,
    dc.date_val AS date_cloture,

    f.montant_evaluation_initiale,
    f.montant_declare,
    f.montant_total,
    f.montant_total_net,

    f.code_etat_sinistre,
    f.etat_garantie,
    f.motif_cloture,

    f.delai_declaration_jours,
    f.delai_ouverture_jours,
    f.anciennete_contrat_jours,

    f.is_declaration_antidatee,
    f.is_declaration_tardive,
    f.is_sinistre_avant_contrat,
    f.is_sinistre_precoce,

    fs.score_rule_norm,
    fs.score_ml,
    fs.score_cross,
    fs.score_global,
    fs.risk_level,
    fs.confidence_level,

    rs.triggered_rules

FROM iris_dw.fact_sinistre f
LEFT JOIN iris_dw.dim_client c
    ON f.client_sk = c.client_sk
LEFT JOIN iris_dw.dim_contrat ct
    ON f.contrat_sk = ct.contrat_sk
LEFT JOIN iris_dw.dim_vehicule v
    ON f.vehicule_sk = v.vehicule_sk
LEFT JOIN iris_dw.dim_produit p
    ON f.produit_sk = p.produit_sk
LEFT JOIN iris_dw.dim_garantie g
    ON f.garantie_sk = g.garantie_sk
LEFT JOIN iris_dw.dim_cause_sinistre cs
    ON f.cause_sinistre_sk = cs.cause_sinistre_sk
LEFT JOIN iris_dw.dim_date ds
    ON f.date_survenance_sk = ds.date_sk
LEFT JOIN iris_dw.dim_date dd
    ON f.date_declaration_sk = dd.date_sk
LEFT JOIN iris_dw.dim_date doo
    ON f.date_ouverture_sk = doo.date_sk
LEFT JOIN iris_dw.dim_date dc
    ON f.date_cloture_sk = dc.date_sk
LEFT JOIN active_fraud_run afr
    ON true
LEFT JOIN iris_score.fact_fraud_score fs
    ON f.sinistre_sk = fs.sinistre_sk
   AND fs.run_id = afr.run_id
LEFT JOIN rule_summary rs
    ON f.sinistre_sk = rs.sinistre_sk
   AND rs.run_id = afr.run_id;


COMMENT ON VIEW iris_mart.vw_dossier_360 IS
'Vue dossier 360 : sinistre, client, contrat, véhicule, garantie, montants, flags et score actif.';


-- ============================================================
-- 3. vw_dashboard_global
-- Objectif : KPIs globaux pour Power BI
-- Grain    : 1 ligne globale
-- ============================================================

CREATE OR REPLACE VIEW iris_mart.vw_dashboard_global AS
WITH active_fraud_run AS (
    SELECT run_id
    FROM iris_score.scoring_run
    WHERE run_type = 'FRAUD'
      AND is_active = true
      AND status = 'SUCCESS'
    LIMIT 1
)
SELECT
    COUNT(*) AS nombre_sinistres,
    SUM(f.montant_total) AS montant_total_sinistres,
    SUM(f.montant_total_net) AS montant_total_net,

    COUNT(*) FILTER (WHERE f.is_declaration_antidatee = true) AS nombre_declarations_antidatees,
    COUNT(*) FILTER (WHERE f.is_declaration_tardive = true) AS nombre_declarations_tardives,
    COUNT(*) FILTER (WHERE f.is_sinistre_avant_contrat = true) AS nombre_sinistres_avant_contrat,
    COUNT(*) FILTER (WHERE f.is_sinistre_precoce = true) AS nombre_sinistres_precoces,

    COUNT(*) FILTER (WHERE fs.risk_level = 'NORMAL') AS dossiers_normal,
    COUNT(*) FILTER (WHERE fs.risk_level = 'FAIBLE') AS dossiers_faible,
    COUNT(*) FILTER (WHERE fs.risk_level = 'MOYEN') AS dossiers_moyen,
    COUNT(*) FILTER (WHERE fs.risk_level = 'ELEVE') AS dossiers_eleve,

    AVG(fs.score_global) AS score_global_moyen

FROM iris_dw.fact_sinistre f
LEFT JOIN active_fraud_run afr
    ON true
LEFT JOIN iris_score.fact_fraud_score fs
    ON f.sinistre_sk = fs.sinistre_sk
   AND fs.run_id = afr.run_id;


COMMENT ON VIEW iris_mart.vw_dashboard_global IS
'KPIs globaux IRIS pour dashboard Power BI.';


-- ============================================================
-- 4. vw_client_behavior
-- Objectif : comportement historique client
-- Grain    : 1 ligne par client
-- ============================================================

CREATE OR REPLACE VIEW iris_mart.vw_client_behavior AS
WITH active_fraud_run AS (
    SELECT run_id
    FROM iris_score.scoring_run
    WHERE run_type = 'FRAUD'
      AND is_active = true
      AND status = 'SUCCESS'
    LIMIT 1
)
SELECT
    c.client_sk,
    c.num_client,
    c.code_nature_client,
    c.sexe,
    c.gouvernorat_client,
    c.localite_client,

    COUNT(f.sinistre_sk) AS nb_sinistres,
    COUNT(DISTINCT f.vehicule_sk) AS nb_vehicules,
    SUM(f.montant_total) AS montant_total_sinistres,

    COUNT(*) FILTER (WHERE fs.risk_level = 'MOYEN') AS nb_dossiers_moyen,
    COUNT(*) FILTER (WHERE fs.risk_level = 'ELEVE') AS nb_dossiers_eleve,

    MAX(ds.date_val) AS dernier_sinistre

FROM iris_dw.dim_client c
LEFT JOIN iris_dw.fact_sinistre f
    ON c.client_sk = f.client_sk
LEFT JOIN iris_dw.dim_date ds
    ON f.date_survenance_sk = ds.date_sk
LEFT JOIN active_fraud_run afr
    ON true
LEFT JOIN iris_score.fact_fraud_score fs
    ON f.sinistre_sk = fs.sinistre_sk
   AND fs.run_id = afr.run_id
GROUP BY
    c.client_sk,
    c.num_client,
    c.code_nature_client,
    c.sexe,
    c.gouvernorat_client,
    c.localite_client;


COMMENT ON VIEW iris_mart.vw_client_behavior IS
'Historique comportement client : sinistres, montants et niveaux de risque actifs.';


-- ============================================================
-- 5. vw_vehicle_history
-- Objectif : historique véhicule
-- Grain    : 1 ligne par véhicule
-- ============================================================

CREATE OR REPLACE VIEW iris_mart.vw_vehicle_history AS
WITH active_vhs_run AS (
    SELECT run_id
    FROM iris_score.scoring_run
    WHERE run_type = 'VHS'
      AND is_active = true
      AND status = 'SUCCESS'
    LIMIT 1
),
latest_vhs AS (
    SELECT DISTINCT ON (vs.vehicule_sk)
        vs.vehicule_sk,
        vs.vhs_score_displayed,
        vs.safety_grade,
        vs.vhs_decision,
        vs.is_drivable,
        vs.scored_at
    FROM iris_score.fact_vhs_score vs
    JOIN active_vhs_run avr
        ON vs.run_id = avr.run_id
    ORDER BY vs.vehicule_sk, vs.scored_at DESC
)
SELECT
    v.vehicule_sk,
    v.immatriculation,
    v.vin,
    v.marque,
    v.modele,
    v.genre_vehicule,
    v.usage_vehicule,
    v.motorisation,

    COUNT(DISTINCT f.sinistre_sk) AS nb_sinistres,
    COUNT(DISTINCT i.inspection_sk) AS nb_inspections,
    SUM(f.montant_total) AS montant_total_sinistres,

    lv.vhs_score_displayed AS dernier_vhs_score,
    lv.safety_grade AS dernier_safety_grade,
    lv.vhs_decision AS derniere_vhs_decision,
    lv.is_drivable AS dernier_is_drivable

FROM iris_dw.dim_vehicule v
LEFT JOIN iris_dw.fact_sinistre f
    ON v.vehicule_sk = f.vehicule_sk
LEFT JOIN iris_dw.fact_inspection i
    ON v.vehicule_sk = i.vehicule_sk
LEFT JOIN latest_vhs lv
    ON v.vehicule_sk = lv.vehicule_sk
GROUP BY
    v.vehicule_sk,
    v.immatriculation,
    v.vin,
    v.marque,
    v.modele,
    v.genre_vehicule,
    v.usage_vehicule,
    v.motorisation,
    lv.vhs_score_displayed,
    lv.safety_grade,
    lv.vhs_decision,
    lv.is_drivable;


COMMENT ON VIEW iris_mart.vw_vehicle_history IS
'Historique véhicule : sinistres, inspections et dernier score VHS actif.';


-- ============================================================
-- 6. vw_score_explanation
-- Objectif : explication des règles déclenchées
-- Grain    : 1 ligne par sinistre × règle déclenchée
-- ============================================================

CREATE OR REPLACE VIEW iris_mart.vw_score_explanation AS
WITH active_fraud_run AS (
    SELECT run_id
    FROM iris_score.scoring_run
    WHERE run_type = 'FRAUD'
      AND is_active = true
      AND status = 'SUCCESS'
    LIMIT 1
)
SELECT
    f.num_sinistre,
    f.sinistre_sk,

    g.code_garantie,
    g.libelle_garantie,

    fs.score_global,
    fs.risk_level,
    fs.confidence_level,

    r.rule_code,
    COALESCE(dr.rule_name, r.rule_code) AS rule_name,
    dr.rule_category,

    r.observed_value,
    r.threshold_value,
    r.rule_weight,
    r.rule_contribution

FROM iris_score.fact_fraud_rule_detail r
JOIN active_fraud_run afr
    ON r.run_id = afr.run_id
JOIN iris_dw.fact_sinistre f
    ON r.sinistre_sk = f.sinistre_sk
LEFT JOIN iris_dw.dim_garantie g
    ON f.garantie_sk = g.garantie_sk
LEFT JOIN iris_score.fact_fraud_score fs
    ON r.fraud_score_sk = fs.fraud_score_sk
LEFT JOIN iris_score.dim_fraud_rule dr
    ON r.rule_sk = dr.rule_sk;


COMMENT ON VIEW iris_mart.vw_score_explanation IS
'Explication du score fraude : règles déclenchées par dossier.';