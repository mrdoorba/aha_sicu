-- Assign roles to BD team users in the production database.
--
-- Provisioning Process:
--   1. Run provision-users.py to create Firebase Auth accounts
--   2. Have ALL users log in once at https://aha-sicu-prod.web.app
--      (the backend auto-creates user records with role='member' on first login)
--   3. Replace the placeholder UIDs below with real UIDs from provision-users.py output
--   4. Run this script against the production Neon PostgreSQL database:
--      psql $DATABASE_URL -f scripts/assign-roles.sql
--
-- DATABASE_URL can be retrieved from Secret Manager:
--   gcloud secrets versions access latest --secret=aha_sicu_prod_db_url
--
-- Role definitions:
--   admin  — System owner, full access
--   leader — BD team leader, can view all evaluations
--   member — BD team member, standard evaluation access
--
-- IMPORTANT: Users MUST have logged in at least once before running this script.
-- The backend auto-creates the user record on first login (Story 1.2).
-- If a user hasn't logged in yet, the UPDATE will affect 0 rows.

BEGIN;

-- System owner (admin role)
UPDATE users SET role = 'admin'
WHERE firebase_uid = 'REPLACE_WITH_ADMIN_UID'
  AND role != 'admin';

-- BD team leader
UPDATE users SET role = 'leader'
WHERE firebase_uid = 'REPLACE_WITH_LEADER_UID'
  AND role != 'leader';

-- BD team members (keep default 'member' role — no UPDATE needed)
-- These are listed for documentation purposes:
-- Member 1: firebase_uid = 'REPLACE_WITH_MEMBER1_UID'
-- Member 2: firebase_uid = 'REPLACE_WITH_MEMBER2_UID'
-- Member 3: firebase_uid = 'REPLACE_WITH_MEMBER3_UID'

COMMIT;

-- Verify results
SELECT firebase_uid, email, role, created_at, last_login
FROM users
ORDER BY
  CASE role
    WHEN 'admin' THEN 1
    WHEN 'leader' THEN 2
    WHEN 'member' THEN 3
  END;
