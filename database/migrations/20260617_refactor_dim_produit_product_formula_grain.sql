BEGIN;

ALTER TABLE iris_dw.dim_produit
    ADD COLUMN IF NOT EXISTS libelle_formule TEXT,
    ADD COLUMN IF NOT EXISTS libelle_famille_produit TEXT;

UPDATE iris_dw.dim_produit
SET
    code_produit = COALESCE(NULLIF(btrim(code_produit), ''), 'UNKNOWN'),
    code_formule = COALESCE(NULLIF(btrim(code_formule), ''), 'UNKNOWN'),
    produit_natural_key =
        COALESCE(NULLIF(btrim(code_produit), ''), 'UNKNOWN')
        || '|'
        || COALESCE(NULLIF(btrim(code_formule), ''), 'UNKNOWN'),
    updated_at = now()
WHERE produit_sk <> 0;

UPDATE iris_dw.dim_produit
SET
    produit_natural_key = 'UNKNOWN',
    code_produit = 'UNKNOWN',
    libelle_produit = COALESCE(libelle_produit, 'UNKNOWN'),
    code_formule = 'UNKNOWN',
    libelle_formule = COALESCE(libelle_formule, 'UNKNOWN'),
    code_famille_produit = COALESCE(code_famille_produit, 'UNKNOWN'),
    libelle_famille_produit = COALESCE(libelle_famille_produit, 'UNKNOWN'),
    updated_at = now()
WHERE produit_sk = 0;

ALTER TABLE iris_dw.dim_produit
    ALTER COLUMN code_produit SET NOT NULL,
    ALTER COLUMN code_formule SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'dim_produit_code_produit_code_formule_uk'
          AND conrelid = 'iris_dw.dim_produit'::regclass
    ) THEN
        ALTER TABLE iris_dw.dim_produit
            ADD CONSTRAINT dim_produit_code_produit_code_formule_uk
            UNIQUE (code_produit, code_formule);
    END IF;
END $$;

COMMENT ON TABLE iris_dw.dim_produit IS
'Dimension produit / formule assurance. Grain: code_produit + code_formule.';

COMMIT;
