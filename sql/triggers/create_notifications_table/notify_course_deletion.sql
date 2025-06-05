CREATE OR REPLACE FUNCTION notify_course_deletion()
RETURNS TRIGGER AS $$
DECLARE
  course_title TEXT := OLD.title;
  _manager_id UUID := OLD.manager_id;
BEGIN
  INSERT INTO notifications (id, message, is_read, created_at, user_id)
  VALUES (
    uuid_generate_v4(),
    'You have deleted your course "' || course_title || '"!',
    FALSE,
    NOW(),
    _manager_id
  );
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_notify_course_deletion
BEFORE DELETE ON courses
FOR EACH ROW
EXECUTE FUNCTION notify_course_deletion();
