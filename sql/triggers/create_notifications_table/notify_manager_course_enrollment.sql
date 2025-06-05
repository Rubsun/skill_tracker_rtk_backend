CREATE OR REPLACE FUNCTION notify_manager_course_enrollment()
RETURNS TRIGGER AS $$
DECLARE
    course_title TEXT;
    _manager_id UUID;
    user_nickname TEXT;
BEGIN
    SELECT title, manager_id INTO course_title, _manager_id FROM courses WHERE id = NEW.course_id;

    SELECT username INTO user_nickname FROM users WHERE id = NEW.employee_id;

    INSERT INTO notifications (id, message, is_read, created_at, user_id)
    VALUES (
        uuid_generate_v4(),
        'User ' || user_nickname || ' has signed up for your "' || course_title || '" course!',
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
