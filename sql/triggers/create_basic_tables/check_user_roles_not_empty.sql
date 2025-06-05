CREATE OR REPLACE FUNCTION check_user_roles_not_empty()
RETURNS TRIGGER AS $$
DECLARE
    roles_count INT;
BEGIN
    IF (TG_OP = 'DELETE') THEN
        SELECT COUNT(*) INTO roles_count FROM user_roles WHERE user_id = OLD.user_id AND id <> OLD.id;
        IF roles_count = 0 THEN
            RAISE EXCEPTION 'User must have at least one role!';
        END IF;
    ELSIF (TG_OP = 'UPDATE') THEN
        IF OLD.user_id IS DISTINCT FROM NEW.user_id THEN
            SELECT COUNT(*) INTO roles_count FROM user_roles WHERE user_id = OLD.user_id AND id <> OLD.id;
            IF roles_count = 0 THEN
                RAISE EXCEPTION 'User must have at least one role!';
            END IF;
        END IF;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_user_roles_not_empty
BEFORE DELETE OR UPDATE ON user_roles
FOR EACH ROW
EXECUTE FUNCTION check_user_roles_not_empty();
