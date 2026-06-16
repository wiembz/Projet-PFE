-- ============================================================
-- IRISv2 - 01_iris_admin.sql
-- Objectif : tables techniques pour traçabilité ETL
-- ============================================================

CREATE TABLE IF NOT EXISTS iris_admin.etl_run (
    etl_run_id TEXT PRIMARY KEY,
    run_name TEXT NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT now(),
    ended_at TIMESTAMP,
    status TEXT NOT NULL,
    source_snapshot TEXT,
    input_count INTEGER,
    output_count INTEGER,
    rejected_count INTEGER,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

COMMENT ON TABLE iris_admin.etl_run IS
'Suivi des exécutions ETL : début, fin, statut, volumes et erreurs.';


CREATE TABLE IF NOT EXISTS iris_admin.etl_rejected_record (
    rejection_id BIGSERIAL PRIMARY KEY,
    etl_run_id TEXT REFERENCES iris_admin.etl_run(etl_run_id),
    source_name TEXT NOT NULL,
    source_file TEXT,
    source_row_number INTEGER,
    target_table TEXT,
    rejection_reason TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'WARNING',
    raw_payload JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

COMMENT ON TABLE iris_admin.etl_rejected_record IS
'Lignes rejetées ou non exploitables pendant l’ETL avec raison et payload source.';


CREATE TABLE IF NOT EXISTS iris_admin.data_quality_check (
    check_id BIGSERIAL PRIMARY KEY,
    etl_run_id TEXT REFERENCES iris_admin.etl_run(etl_run_id),
    check_name TEXT NOT NULL,
    schema_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    expected_value TEXT,
    observed_value TEXT,
    status TEXT NOT NULL,
    checked_at TIMESTAMP NOT NULL DEFAULT now()
);

COMMENT ON TABLE iris_admin.data_quality_check IS
'Résultats des contrôles qualité : volumes, nulls, doublons, FK orphans.';