CREATE TABLE IF NOT EXISTS iris_admin.etl_step_run (
    step_run_id BIGSERIAL PRIMARY KEY,
    etl_run_id TEXT NOT NULL REFERENCES iris_admin.etl_run(etl_run_id),
    step_name TEXT NOT NULL,
    step_order INTEGER,
    script_path TEXT,
    started_at TIMESTAMP NOT NULL DEFAULT now(),
    ended_at TIMESTAMP,
    status TEXT NOT NULL,
    input_count INTEGER,
    output_count INTEGER,
    rejected_count INTEGER,
    warning_count INTEGER,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT etl_step_run_status_chk
        CHECK (status IN ('STARTED', 'SUCCESS', 'FAILED', 'SKIPPED'))
);

COMMENT ON TABLE iris_admin.etl_step_run IS
'Suivi détaillé des étapes ETL rattachées à un etl_run.';

CREATE INDEX IF NOT EXISTS idx_etl_step_run_etl_run_id
    ON iris_admin.etl_step_run(etl_run_id);

CREATE INDEX IF NOT EXISTS idx_etl_step_run_status
    ON iris_admin.etl_step_run(status);

CREATE INDEX IF NOT EXISTS idx_etl_step_run_started_at
    ON iris_admin.etl_step_run(started_at);
