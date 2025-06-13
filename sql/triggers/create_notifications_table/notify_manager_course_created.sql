CREATE OR REPLACE FUNCTION notify_manager_course_produced()
RETURNS TRIGGER AS $$
BEGIN
  /*
   * Уведомляет менеджера курса при изменении статуса курса на "произведённый".
   *
   * При обновлении записи courses,
   * если is_produced изменился с FALSE на TRUE,
   * добавляет уведомление менеджеру о публикации курса с названием NEW.title.
   *
   * Триггер срабатывает ПОСЛЕ обновления записи courses.
   */
  IF OLD.is_produced = FALSE AND NEW.is_produced = TRUE THEN
    INSERT INTO notifications (id, message, is_read, created_at, user_id)
    VALUES (
      uuid_generate_v4(),
      'You have created and published the "' || NEW.title || '" course.',
      FALSE,
      NOW(),
      NEW.manager_id
    );
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_notify_manager_course_produced
AFTER UPDATE ON courses
FOR EACH ROW
EXECUTE FUNCTION notify_manager_course_produced();
