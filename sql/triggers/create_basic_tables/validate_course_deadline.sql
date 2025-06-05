CREATE OR REPLACE FUNCTION validate_course_deadline()
RETURNS TRIGGER AS $$
DECLARE
    max_content_deadline TIMESTAMPTZ;
BEGIN
    IF NEW.deadline IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT MAX(deadline)
    INTO max_content_deadline
    FROM contents
    WHERE course_id = NEW.id AND deadline IS NOT NULL;

    IF max_content_deadline IS NOT NULL AND NEW.deadline < max_content_deadline THEN
        RAISE EXCEPTION 'Course deadline (%s) cannot be earlier than latest content deadline (%s)!', 
            NEW.deadline, max_content_deadline;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_course_deadline
BEFORE UPDATE OR INSERT ON courses
FOR EACH ROW
EXECUTE FUNCTION validate_course_deadline();
