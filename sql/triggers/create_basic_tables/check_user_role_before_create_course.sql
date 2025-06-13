CREATE OR REPLACE FUNCTION check_course_manager_role()
RETURNS TRIGGER AS $$
DECLARE
  role_count INT;
BEGIN
  /*
   * Проверяет, что пользователь, указанный как менеджер курса (manager_id),
   * действительно обладает ролью 'manager' в таблице user_roles.
   *
   * Если роль отсутствует, выбрасывает исключение.
   *
   * Триггер вызывается ДО вставки или обновления записи в таблице courses.
   */
  SELECT COUNT(*) INTO role_count FROM user_roles WHERE user_id = NEW.manager_id AND role = 'manager';
  IF role_count = 0 THEN
    RAISE EXCEPTION 'The course can only be created by a user with the manager role!';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_course_manager_role
BEFORE INSERT OR UPDATE ON courses
FOR EACH ROW
EXECUTE FUNCTION check_course_manager_role();
