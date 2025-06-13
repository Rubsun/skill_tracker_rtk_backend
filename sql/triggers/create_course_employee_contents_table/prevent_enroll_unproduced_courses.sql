CREATE OR REPLACE FUNCTION prevent_enroll_unproduced_courses()
RETURNS TRIGGER AS $$
BEGIN
    /*
     * Запрещает регистрацию пользователя на курс (course_employees),
     * если курс ещё не произведён (is_produced != TRUE).
     *
     * При попытке добавить запись, где course_id с курсом без production,
     * выбрасывается исключение.
     *
     * Триггер срабатывает ДО вставки записи в таблицу course_employees.
     */
    IF NOT EXISTS (
        SELECT 1 FROM courses
        WHERE id = NEW.course_id AND is_produced = TRUE
    ) THEN
        RAISE EXCEPTION 'Cannot enroll in an unproduced course!';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_enroll_unproduced_courses
BEFORE INSERT ON course_employees
FOR EACH ROW
EXECUTE FUNCTION prevent_enroll_unproduced_courses();
