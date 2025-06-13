CREATE OR REPLACE FUNCTION check_content_type_task_theory()
RETURNS TRIGGER AS $$
BEGIN
  /*
   * Проверяет корректность заполнения полей task_id и theory_id в таблице contents.
   * Условие:
   * - task_id и theory_id не могут быть заполнены одновременно.
   * - Один из них должен быть обязательно заполнен.
   *
   * Выбрасывает исключение при нарушении условий.
   *
   * Триггер вызывается ДО вставки или обновления записи.
   */
  IF (NEW.task_id IS NOT NULL AND NEW.theory_id IS NOT NULL) THEN
    RAISE EXCEPTION 'The task_id and theory_id fields cannot be filled in at the same time!';
  ELSIF (NEW.task_id IS NULL AND NEW.theory_id IS NULL) THEN
    RAISE EXCEPTION 'One of the task_id or theory_id fields must be filled in!';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_content_type_task_theory
BEFORE INSERT OR UPDATE ON contents
FOR EACH ROW
EXECUTE FUNCTION check_content_type_task_theory();
