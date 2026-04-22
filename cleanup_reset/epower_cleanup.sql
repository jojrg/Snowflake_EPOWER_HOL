-- ========================================================================
-- EPOWER Energy Demo - Cleanup Script
-- Run with ACCOUNTADMIN role to ensure all objects can be dropped
-- ========================================================================

USE ROLE accountadmin;
USE WAREHOUSE EPOWER_COMPUTE;

-- ========================================================================
-- REMOVE AGENT FROM SNOWFLAKE INTELLIGENCE
-- ========================================================================
BEGIN
    ALTER SNOWFLAKE INTELLIGENCE snowflake_intelligence_object_default 
        DROP AGENT EPOWER_DEMO.EPOWER_GOLD.EPOWER_AGENT;
EXCEPTION
    WHEN OTHER THEN NULL;
END;

-- ========================================================================
-- DROP INTEGRATIONS
-- ========================================================================
DROP EXTERNAL ACCESS INTEGRATION IF EXISTS Energy_ExternalAccess;
DROP EXTERNAL ACCESS INTEGRATION IF EXISTS energy_charts_integration;
DROP API INTEGRATION IF EXISTS git_api_integration_energy;

-- ========================================================================
-- DROP DATABASE (includes all schemas, tables, views, stages, etc.)
-- ========================================================================
DROP DATABASE IF EXISTS EPOWER_DEMO;

-- ========================================================================
-- DROP WAREHOUSE
-- ========================================================================
DROP WAREHOUSE IF EXISTS EPOWER_COMPUTE;

-- ========================================================================
-- DROP ROLE
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

SELECT 'EPOWER Demo cleanup completed!' AS status;
