CREATE OR REPLACE FUNCTION check_user_roles()
RETURNS TRIGGER AS $$
DECLARE
  user_exists INT;
  roles_count INT;
BEGIN
  SELECT COUNT(*) INTO user_exists FROM users WHERE id = NEW.id;
  IF user_exists = 0 THEN
    RAISE EXCEPTION 'Пользователь с id % не существует!', NEW.id;
  END IF;

  SELECT COUNT(*) INTO roles_count FROM user_roles WHERE user_id = NEW.id;
  IF roles_count = 0 THEN
    RAISE EXCEPTION 'Пользователь должен иметь хотя бы одну роль!';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_user_roles ON users;

CREATE TRIGGER trg_check_user_roles
AFTER INSERT OR UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION check_user_roles();
