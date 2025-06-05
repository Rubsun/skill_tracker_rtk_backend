CREATE OR REPLACE FUNCTION notify_employee_course_completed()
RETURNS TRIGGER AS $$
DECLARE
  _employee_id UUID;
  _course_id UUID;
  total_contents INT;
  done_contents INT;
  course_title TEXT;
  _is_completed BOOLEAN;
  _manager_id UUID;
  employee_username TEXT;
  _passing_percent INT;
  done_percent NUMERIC;
BEGIN
  SELECT employee_id, course_id, is_completed
  INTO _employee_id, _course_id, _is_completed
  FROM course_employees
  WHERE id = NEW.course_employee_id;

  IF _is_completed THEN
    RETURN NEW;
  END IF;

  SELECT COUNT(*) INTO total_contents
  FROM contents
  WHERE course_id = _course_id;

  IF total_contents = 0 THEN
    RETURN NEW;
  END IF;

  SELECT COUNT(*) INTO done_contents
  FROM course_employee_contents ecs
  JOIN contents c ON ecs.content_id = c.id
  WHERE ecs.course_employee_id = NEW.course_employee_id
    AND ecs.status = 'done'
    AND c.course_id = _course_id;

  SELECT passing_percent INTO _passing_percent FROM courses WHERE id = _course_id;

  done_percent := (done_contents::NUMERIC / total_contents::NUMERIC) * 100;

  IF done_percent >= _passing_percent THEN
    SELECT title, manager_id INTO course_title, _manager_id FROM courses WHERE id = _course_id;

    SELECT username INTO employee_username FROM users WHERE id = _employee_id;

    INSERT INTO notifications (id, message, is_read, created_at, user_id)
    VALUES (
      uuid_generate_v4(),
      'You have successfully completed the "' || course_title || '" course!',
      FALSE,
      NOW(),
      _employee_id
    );

    INSERT INTO notifications (id, message, is_read, created_at, user_id)
    VALUES (
      uuid_generate_v4(),
      'The user ' || employee_username || ' has successfully completed your "' || course_title || '" course.',
      FALSE,
      NOW(),
      _manager_id
    );

    UPDATE course_employees
    SET is_completed = TRUE
    WHERE id = NEW.course_employee_id;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_notify_employee_course_completed
AFTER UPDATE OF status ON course_employee_contents
FOR EACH ROW
EXECUTE FUNCTION notify_employee_course_completed();
