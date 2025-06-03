CREATE OR REPLACE FUNCTION check_course_employee_role()
RETURNS TRIGGER AS $$
DECLARE
  role_count INT;
BEGIN
  SELECT COUNT(*) INTO role_count FROM user_roles WHERE user_id = NEW.employee_id AND role = 'employee';
  IF role_count = 0 THEN
    RAISE EXCEPTION 'Only a user with the employee role can register for the courses!';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_course_employee_role
BEFORE INSERT OR UPDATE ON course_employees
FOR EACH ROW
EXECUTE FUNCTION check_course_employee_role();
