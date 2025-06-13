CREATE OR REPLACE FUNCTION protect_produced_content_update()
RETURNS TRIGGER AS $$
DECLARE
    course_status BOOLEAN;
BEGIN
    /*
     * Ограничивает обновление содержимого курса (таблица contents),
     * если курс уже помечен как "produced" (is_produced = TRUE).
     *
     * После производства курса можно изменять только поле deadline.
     * Попытка изменить title, task_id, theory_id, course_id или created_at вызовет исключение.
     *
     * Триггер вызывается ДО обновления записи.
     */
    SELECT is_produced INTO course_status FROM courses WHERE id = OLD.course_id;

    IF course_status = TRUE THEN
        IF (NEW.title IS DISTINCT FROM OLD.title)
           OR (NEW.task_id IS DISTINCT FROM OLD.task_id)
           OR (NEW.theory_id IS DISTINCT FROM OLD.theory_id)
           OR (NEW.course_id IS DISTINCT FROM OLD.course_id)
           OR (NEW.created_at IS DISTINCT FROM OLD.created_at) THEN
            RAISE EXCEPTION 'Only deadline can be updated after course is produced!';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_protect_produced_content_update
BEFORE UPDATE ON contents
FOR EACH ROW
EXECUTE FUNCTION protect_produced_content_update();
