CREATE OR REPLACE FUNCTION check_content_type_task_theory()
RETURNS TRIGGER AS $$
BEGIN
  IF (NEW.task_id IS NOT NULL AND NEW.theory_id IS NOT NULL) THEN
    RAISE EXCEPTION 'Поля task_id и theory_id не могут быть заполнены одновременно!';
  ELSIF (NEW.task_id IS NULL AND NEW.theory_id IS NULL) THEN
    RAISE EXCEPTION 'Одно из полей task_id или theory_id должно быть заполнено!';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_content_type_task_theory ON contents;

CREATE TRIGGER trg_check_content_type_task_theory
BEFORE INSERT OR UPDATE ON contents
FOR EACH ROW
EXECUTE FUNCTION check_content_type_task_theory();
