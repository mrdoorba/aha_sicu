-- Assign roles to BD team users in the production database.
--
-- Provisioning Process:
--   1. Run provision-users.py to create Firebase Auth accounts
--   2. Have ALL users log in once at the app URL (dev: https://aha-coms-sicu-dev.web.app)
--      (the backend auto-creates user records with role='member' on first login)
--   3. Replace the placeholder UIDs below with real UIDs from provision-users.py output
--   4. Run this script against the production Neon PostgreSQL database:
--      psql $DATABASE_URL -f scripts/assign-roles.sql
--
-- DATABASE_URL can be retrieved from Secret Manager:
--   gcloud secrets versions access latest --secret=aha_coms_sicu_prod_db_password
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

-- System owner (admin role) — handers@ahaace.com
UPDATE users SET role = 'admin'
WHERE firebase_uid = 'J7S2Y4A8W9XcyvKxR8OCnCNL8Ry2'
  AND role != 'admin';

-- BD team leader — marwah@ahabd.com
UPDATE users SET role = 'leader'
WHERE firebase_uid = 'aPoacvrKhlhZHVgJCPKhCHdmc7Q2'
  AND role != 'leader';

-- BD team members (keep default 'member' role — no UPDATE needed)
-- Member: yusuf@ahabd.com — firebase_uid = '59cBh87nfhgqWe3VVQ3RPKYXo5s2'

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
