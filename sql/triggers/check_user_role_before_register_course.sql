CREATE OR REPLACE FUNCTION check_course_employee_role()
RETURNS TRIGGER AS $$
DECLARE
  user_exists INT;
  role_count INT;
BEGIN
  SELECT COUNT(*) INTO user_exists FROM users WHERE id = NEW.manager_id;
  IF user_exists = 0 THEN
    RAISE EXCEPTION 'Пользователь с id % не существует!', NEW.manager_id;
  END IF;

  SELECT COUNT(*) INTO role_count FROM user_roles WHERE user_id = NEW.employee_id AND role = 'employee';
  IF role_count = 0 THEN
    RAISE EXCEPTION 'Только пользователь с ролью employee может регистрироваться на курсы!';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_course_employee_role
BEFORE INSERT OR UPDATE ON course_employees
FOR EACH ROW
EXECUTE FUNCTION check_course_employee_role();
