CREATE OR REPLACE FUNCTION protect_theory_update_after_production()
RETURNS TRIGGER AS $$
DECLARE
    course_status BOOLEAN;
BEGIN
    SELECT is_produced INTO course_status
    FROM contents c
    JOIN courses cr ON c.course_id = cr.id
    WHERE c.theory_id = OLD.id
    LIMIT 1;

    IF course_status = TRUE THEN
        RAISE EXCEPTION 'Cannot update theory after course is produced!';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_protect_theory_update
BEFORE UPDATE ON theories
FOR EACH ROW
EXECUTE FUNCTION protect_theory_update_after_production();
