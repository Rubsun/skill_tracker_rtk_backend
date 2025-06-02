CREATE OR REPLACE FUNCTION check_course_manager_role()
RETURNS TRIGGER AS $$
DECLARE
  role_count INT;
BEGIN
  SELECT COUNT(*) INTO role_count FROM user_roles WHERE user_id = NEW.manager_id AND role = 'manager';
  IF role_count = 0 THEN
    RAISE EXCEPTION 'Курс может быть создан только пользователем с ролью manager!';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_course_manager_role
BEFORE INSERT OR UPDATE ON courses
FOR EACH ROW
EXECUTE FUNCTION check_course_manager_role();
