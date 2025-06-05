CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE OR REPLACE FUNCTION notify_manager_course_comment()
RETURNS TRIGGER AS $$
DECLARE
    _course_id UUID;
    course_title TEXT;
    _manager_id UUID;
    user_nickname TEXT;
BEGIN
    SELECT course_id INTO _course_id FROM contents WHERE id = NEW.content_id;

    SELECT manager_id INTO _manager_id FROM courses WHERE id = _course_id;

    IF NEW.user_id = _manager_id THEN
        RETURN NEW;
    END IF;

    SELECT title INTO course_title FROM courses WHERE id = _course_id;

    SELECT username INTO user_nickname FROM users WHERE id = NEW.user_id;

    INSERT INTO notifications (id, message, is_read, created_at, user_id)
    VALUES (
        uuid_generate_v4(),
        'Under your course "' || course_title || '", user ' || user_nickname || ' left a comment!',
        FALSE,
        NOW(),
        _manager_id
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_notify_manager_course_comment
AFTER INSERT ON comments
FOR EACH ROW
EXECUTE FUNCTION notify_manager_course_comment();
