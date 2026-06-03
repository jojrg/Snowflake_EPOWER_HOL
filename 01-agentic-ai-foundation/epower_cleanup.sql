-- ========================================================================
-- EPOWER Energy Demo - Full Cleanup Script
-- Run with ACCOUNTADMIN role to ensure all objects can be dropped.
--
-- This script handles cleanup for ALL modules (1, 2, 3, 4).
-- It is safe to run even if only some modules were deployed.
--
-- DEPENDENCY ORDER:
--   1. Remove agent from Snowflake Intelligence
--   2. Detach network policy from Postgres instance (Module 2)
--   3. Drop Postgres instance (Module 2)
--   4. Drop network policy and rule (Module 2)
--   5. Drop integrations
--   6. Drop database (includes all schemas, tables, views, etc.)
--   7. Drop warehouse
--   8. Drop role
-- ========================================================================

USE ROLE ACCOUNTADMIN;
USE WAREHOUSE EPOWER_COMPUTE;

-- ========================================================================
-- STEP 1: REMOVE AGENT FROM SNOWFLAKE INTELLIGENCE
-- ========================================================================
BEGIN
    ALTER SNOWFLAKE INTELLIGENCE snowflake_intelligence_object_default 
        DROP AGENT EPOWER_DEMO.EPOWER_GOLD.EPOWER_AGENT;
EXCEPTION
    WHEN OTHER THEN NULL;
END;

-- ========================================================================
-- STEP 2: DETACH NETWORK POLICY FROM POSTGRES INSTANCE (Module 2)
-- Must happen BEFORE dropping the network policy. A policy cannot be
-- dropped while still assigned to an entity.
-- ========================================================================
BEGIN
    ALTER POSTGRES INSTANCE MY_EPOWER_PORTAL UNSET NETWORK_POLICY;
EXCEPTION
    WHEN OTHER THEN NULL;  -- Instance may not exist if Module 2 was not run
END;

-- ========================================================================
-- STEP 3: DROP POSTGRES INSTANCE (Module 2)
-- ========================================================================
DROP POSTGRES INSTANCE IF EXISTS MY_EPOWER_PORTAL;

-- ========================================================================
-- STEP 4: DROP NETWORK POLICY AND RULE (Module 2)
-- Now safe — policy is no longer attached to any entity.
-- ========================================================================
DROP NETWORK POLICY IF EXISTS EPOWER_PG_POLICY;
DROP NETWORK RULE IF EXISTS EPOWER_PG_INGRESS;

-- ========================================================================
-- STEP 5: DROP INTEGRATIONS
-- ========================================================================
DROP CATALOG INTEGRATION IF EXISTS PORTAL_POSTGRES_CATALOG;
DROP EXTERNAL ACCESS INTEGRATION IF EXISTS Energy_ExternalAccess;
DROP EXTERNAL ACCESS INTEGRATION IF EXISTS energy_charts_integration;
DROP API INTEGRATION IF EXISTS git_api_integration_energy;

-- ========================================================================
-- STEP 6: DROP DATABASE (includes all schemas, tables, views, stages, etc.)
-- ========================================================================
DROP DATABASE IF EXISTS EPOWER_DEMO;

-- ========================================================================
-- STEP 7: DROP WAREHOUSE
-- ========================================================================
DROP WAREHOUSE IF EXISTS EPOWER_COMPUTE;

-- ========================================================================
-- STEP 8: DROP ROLE
-- ========================================================================
SET current_user_name = CURRENT_USER();
ALTER USER IDENTIFIER($current_user_name) SET DEFAULT_ROLE = 'SYSADMIN';
DROP ROLE IF EXISTS EPOWER_ROLE;

-- ========================================================================
-- VERIFICATION
-- ========================================================================
SHOW DATABASES LIKE 'EPOWER%';
SHOW WAREHOUSES LIKE 'EPOWER%';
SHOW ROLES LIKE 'EPOWER%';
SHOW INTEGRATIONS LIKE '%energy%';
SHOW INTEGRATIONS LIKE '%PORTAL%';
SHOW NETWORK POLICIES LIKE 'EPOWER%';

SELECT 'EPOWER Demo cleanup completed!' AS status;
