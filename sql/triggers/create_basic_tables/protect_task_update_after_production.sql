CREATE OR REPLACE FUNCTION protect_task_update_after_production()
RETURNS TRIGGER AS $$
DECLARE
    course_status BOOLEAN;
BEGIN
    /*
     * Запрещает обновление записи задачи (tasks),
     * если связанный с ней курс (через contents) уже помечен как произведённый (is_produced = TRUE).
     *
     * Выполняется поиск курса по task_id, связанной записи contents и проверка статуса is_produced.
     * Если курс произведён — выбрасывает исключение.
     *
     * Триггер срабатывает ДО обновления записи в таблице tasks.
     */
    SELECT is_produced INTO course_status
    FROM contents c
    JOIN courses cr ON c.course_id = cr.id
    WHERE c.task_id = OLD.id
    LIMIT 1;

    IF course_status = TRUE THEN
        RAISE EXCEPTION 'Cannot update task after course is produced!';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_protect_task_update
BEFORE UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION protect_task_update_after_production();
