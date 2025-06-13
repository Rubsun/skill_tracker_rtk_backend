CREATE OR REPLACE FUNCTION notify_manager_course_enrollment()
RETURNS TRIGGER AS $$
DECLARE
    course_title TEXT;
    _manager_id UUID;
    user_email TEXT;
BEGIN
    /*
     * Уведомляет менеджера курса о новом участнике.
     *
     * При добавлении записи о регистрации пользователя на курс (course_employees),
     * добавляет уведомление менеджеру с сообщением о том,
     * что пользователь с user_email записался на курс course_title.
     *
     * Триггер срабатывает ПОСЛЕ вставки записи в таблицу course_employees.
     */
    SELECT title, manager_id INTO course_title, _manager_id FROM courses WHERE id = NEW.course_id;

    SELECT email INTO user_email FROM users WHERE id = NEW.employee_id;

    INSERT INTO notifications (id, message, is_read, created_at, user_id)
    VALUES (
        uuid_generate_v4(),
        'User ' || user_email || ' has signed up for your "' || course_title || '" course!',
        FALSE,
        NOW(),
        _manager_id
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_notify_manager_course_enrollment
AFTER INSERT ON course_employees
FOR EACH ROW
EXECUTE FUNCTION notify_manager_course_enrollment();
