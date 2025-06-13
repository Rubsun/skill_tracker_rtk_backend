CREATE OR REPLACE FUNCTION check_course_employee_role()
RETURNS TRIGGER AS $$
DECLARE
  role_count INT;
  course_manager_id UUID;
BEGIN
  /*
   * Проверяет два условия при регистрации пользователя на курс (таблица course_employees):
   * 1. Пользователь (employee_id) должен иметь роль 'employee'.
   * 2. Пользователь не может зарегистрироваться на курс, которым он управляет (не быть менеджером курса).
   *
   * Если условия не выполняются, выбрасываются соответствующие исключения.
   *
   * Триггер вызывается ДО вставки или обновления записи в таблице course_employees.
   */
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
