CREATE OR REPLACE FUNCTION create_course_employee_contents()
RETURNS TRIGGER AS $$
BEGIN
  /*
   * После добавления пользователя к курсу (course_employees),
   * автоматически создаёт связанные записи в course_employee_contents
   * для всех содержимых данного курса (contents).
   *
   * Каждой записи присваивается новый UUID, статус 'pending',
   * время обновления — текущее.
   *
   * Триггер срабатывает ПОСЛЕ вставки записи в таблицу course_employees.
   */
  INSERT INTO course_employee_contents (
    id,
    course_employee_id,
    content_id,
    status,
    updated_at
  )
  SELECT
    uuid_generate_v4(),
    NEW.id,
    cc.id,
    'pending',
    now()
  FROM contents cc
  WHERE cc.course_id = NEW.course_id;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_create_course_employee_contents
AFTER INSERT ON course_employees
FOR EACH ROW
EXECUTE FUNCTION create_course_employee_contents();
