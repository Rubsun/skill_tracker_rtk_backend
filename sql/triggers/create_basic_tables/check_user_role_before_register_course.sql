CREATE OR REPLACE FUNCTION check_course_employee_role()
RETURNS TRIGGER AS $$
DECLARE
  role_count INT;
  course_manager_id UUID;
BEGIN
  SELECT COUNT(*) INTO role_count
  FROM user_roles
  WHERE user_id = NEW.employee_id AND role = 'employee';

  IF role_count = 0 THEN
    RAISE EXCEPTION 'Only a user with the employee role can register for the courses!';
  END IF;

  SELECT manager_id INTO course_manager_id
  FROM courses
  WHERE id = NEW.course_id;

  IF course_manager_id = NEW.employee_id THEN
    RAISE EXCEPTION 'A user cannot register for a course they created!';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_course_employee_role
BEFORE INSERT OR UPDATE ON course_employees
FOR EACH ROW
EXECUTE FUNCTION check_course_employee_role();
