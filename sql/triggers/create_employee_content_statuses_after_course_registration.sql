CREATE OR REPLACE FUNCTION create_employee_content_statuses()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO employee_content_statuses (
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

CREATE TRIGGER trg_create_employee_content_statuses
AFTER INSERT ON course_employees
FOR EACH ROW
EXECUTE FUNCTION create_employee_content_statuses();
