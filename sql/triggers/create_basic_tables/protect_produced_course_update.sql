CREATE OR REPLACE FUNCTION protect_produced_course_update()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.is_produced = TRUE THEN
        IF (NEW.title IS DISTINCT FROM OLD.title)
           OR (NEW.manager_id IS DISTINCT FROM OLD.manager_id)
           OR (NEW.is_produced IS DISTINCT FROM OLD.is_produced)
           OR (NEW.created_at IS DISTINCT FROM OLD.created_at) THEN
            RAISE EXCEPTION 'Only description and deadline can be updated after course is produced!';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_protect_produced_course_update
BEFORE UPDATE ON courses
FOR EACH ROW
EXECUTE FUNCTION protect_produced_course_update();
