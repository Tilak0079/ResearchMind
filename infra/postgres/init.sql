-- Runs automatically the FIRST time the postgres container starts
-- (Docker only runs files in docker-entrypoint-initdb.d/ on an empty database).
--
-- Enables gen_random_uuid(), which the schema in architecture doc Section 5
-- relies on for every primary key (paper_id, chunk_id, session_id).
CREATE EXTENSION IF NOT EXISTS pgcrypto;