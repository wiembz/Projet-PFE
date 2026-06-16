-- ============================================================
-- IRISv2 - 00_create_schemas.sql
-- Objectif : création des schémas principaux de la base IRIS
-- ============================================================

CREATE SCHEMA IF NOT EXISTS iris_admin;
CREATE SCHEMA IF NOT EXISTS iris_dw;
CREATE SCHEMA IF NOT EXISTS iris_score;
CREATE SCHEMA IF NOT EXISTS iris_mart;

COMMENT ON SCHEMA iris_admin IS
'Schéma technique : logs ETL, rejets, contrôles qualité, suivi des runs.';

COMMENT ON SCHEMA iris_dw IS
'Data Warehouse métier : dimensions, faits et flags factuels ETL.';

COMMENT ON SCHEMA iris_score IS
'Résultats de scoring versionnés : scoring fraude, VHS, règles déclenchées, run_id.';

COMMENT ON SCHEMA iris_mart IS
'Vues métier consommables par Power BI, la plateforme IRIS et le futur agent.';