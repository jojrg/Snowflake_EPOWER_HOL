---
name: "fix-module2-postgres-notebook"
created: "2026-05-08T17:17:49.953Z"
status: pending
---

# Plan: Fix Module 2 Notebook for Snowflake Postgres

## Problem Summary

The notebook `hol-module2.ipynb` has two critical issues:

1. **`CREATE POSTGRES INSTANCE`** uses 3-part names (`EPOWER_DEMO.EPOWER_OPS.MEIN_EPOWER_PORTAL`) — Postgres instances are **account-level objects** and only accept simple names
2. **`EXECUTE POSTGRES ... $$ ... $$`** is a private preview feature not available on the account — it fails with `syntax error ... unexpected 'POSTGRES'`

Additionally, the CREATE statement uses invalid parameters (`POSTGRES_SIZE`, `AUTO_SUSPEND`, `AUTO_RESUME`) instead of the correct ones (`COMPUTE_FAMILY`, `STORAGE_SIZE_GB`, `AUTHENTICATION_AUTHORITY`).

## Approach: psycopg2 via Python

Replace all `EXECUTE POSTGRES` usage with **psycopg2** (Python PostgreSQL adapter) running inside notebook cells. This:

- Preserves the full Postgres story (real instance, real PG SQL, real pg\_lake)
- Keeps the notebook self-contained (no external tooling beyond pip)
- Works in Snowsight notebooks (psycopg2 is available)

## Changes Required

### 1. Fix CREATE POSTGRES INSTANCE (Cells 5, 39)

**Before:**

```
CREATE POSTGRES INSTANCE IF NOT EXISTS EPOWER_DEMO.EPOWER_OPS.MEIN_EPOWER_PORTAL
    POSTGRES_SIZE = 'XSMALL'
    AUTO_SUSPEND = 600
    AUTO_RESUME = TRUE
    COMMENT = '...';
```

**After:**

```
CREATE POSTGRES INSTANCE IF NOT EXISTS MEIN_EPOWER_PORTAL
    COMPUTE_FAMILY = 'STANDARD_M'
    STORAGE_SIZE_GB = 10
    AUTHENTICATION_AUTHORITY = POSTGRES
    AUTO_SUSPEND_SECS = 600
    COMMENT = '...';
```

Same fix for `EPULSE_DISPATCH` (cell 39).

### 2. Add Network Policy + Connection Setup (new cells after 5/39)

A Postgres instance requires a network policy before it can accept connections. Add cells:

```
-- Create network rule allowing Snowflake internal access
CREATE NETWORK RULE IF NOT EXISTS EPOWER_PG_INGRESS
    TYPE = IPV4
    VALUE_LIST = ('0.0.0.0/0')  -- For demo; restrict in production
    MODE = POSTGRES_INGRESS;

CREATE NETWORK POLICY IF NOT EXISTS EPOWER_PG_POLICY
    ALLOWED_NETWORK_RULE_LIST = ('EPOWER_PG_INGRESS');

ALTER POSTGRES INSTANCE MEIN_EPOWER_PORTAL
    SET NETWORK_POLICY = 'EPOWER_PG_POLICY';
```

Then a Python cell to get connection details:

```
# Get connection details from DESCRIBE
result = session.sql("DESCRIBE POSTGRES INSTANCE MEIN_EPOWER_PORTAL").collect()
pg_host = [r for r in result if r['property'] == 'host'][0]['value']
pg_port = 5432
pg_db = 'postgres'
# User will need to set credentials from the CREATE output
```

### 3. Add Helper Function Cell (new cell near top)

```
import psycopg2

def pg_connect(host, port=5432, dbname='postgres', user='snowflake_admin', password=None):
    """Connect to the Snowflake Postgres instance."""
    return psycopg2.connect(
        host=host, port=port, dbname=dbname,
        user=user, password=password, sslmode='require'
    )

def pg_execute(conn, sql, fetch=True):
    """Execute SQL on Postgres and optionally return results."""
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
        if fetch and cur.description:
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
            return cols, rows
    return None
```

### 4. Replace EXECUTE POSTGRES Cells (many cells)

**Before (%%sql cell):**

```
%%sql
EXECUTE POSTGRES EPOWER_DEMO.EPOWER_OPS.MEIN_EPOWER_PORTAL $$
    CREATE TABLE IF NOT EXISTS portal_users (...);
$$;
```

**After (Python cell):**

```
pg_execute(portal_conn, """
CREATE TABLE IF NOT EXISTS portal_users (...);
""")
print("✓ Portal schema created")
```

### 5. Replace session.sql("EXECUTE POSTGRES ...") in Python cells

**Before:**

```
session.sql(f"EXECUTE POSTGRES EPOWER_DEMO.EPOWER_OPS.MEIN_EPOWER_PORTAL $${sql}$$").collect()
```

**After:**

```
pg_execute(portal_conn, sql)
```

### 6. Fix Catalog Integration (Cells 20, 53)

The `CREATE CATALOG INTEGRATION` syntax should use the correct instance reference. Since instances are account-level, the reference in `REST_CONFIG` should just be the instance name:

```
CREATE OR REPLACE CATALOG INTEGRATION PORTAL_POSTGRES_CATALOG
    CATALOG_SOURCE = SNOWFLAKE_POSTGRES
    TABLE_FORMAT = ICEBERG
    CATALOG_NAMESPACE = 'public'
    REST_CONFIG = (
        POSTGRES_INSTANCE = 'MEIN_EPOWER_PORTAL'
        CATALOG_NAME = 'postgres'
        ACCESS_DELEGATION_MODE = VENDED_CREDENTIALS
    )
    ENABLED = TRUE;
```

### 7. Credential Handling

The notebook will need the password from the CREATE output. Options:

- **Option A (recommended for demos):** Add a cell that prompts the user to paste the password into a `getpass` call
- **Option B:** Use `ALTER POSTGRES INSTANCE ... RESET ACCESS FOR 'snowflake_admin'` to get fresh credentials

```
import getpass
pg_password = getpass.getpass("Enter Postgres password (from CREATE output): ")
portal_conn = pg_connect(host=pg_host, password=pg_password)
```

### 8. DESCRIBE / SHOW fixes

Replace `DESCRIBE POSTGRES INSTANCE EPOWER_DEMO.EPOWER_OPS.X` with just the instance name.

## Summary of Cell Changes

| Cell  | Current                               | New                           |
| ----- | ------------------------------------- | ----------------------------- |
| 5     | CREATE POSTGRES (bad syntax)          | Fixed CREATE + network policy |
| 6     | DESCRIBE (bad name)                   | Fixed DESCRIBE                |
| 8     | EXECUTE POSTGRES (schema)             | psycopg2 call                 |
| 11    | session.sql(EXECUTE POSTGRES ...)     | psycopg2 batch                |
| 13    | session.sql(EXECUTE POSTGRES ...)     | psycopg2 batch                |
| 14    | EXECUTE POSTGRES (verify)             | psycopg2 query                |
| 16-18 | EXECUTE POSTGRES (pg\_lake)           | psycopg2 calls                |
| 20    | CREATE CATALOG INTEGRATION (bad name) | Fixed syntax                  |
| 31    | EXECUTE POSTGRES (live demo)          | psycopg2 insert               |
| 39    | CREATE POSTGRES (bad syntax)          | Fixed CREATE                  |
| 42-51 | EXECUTE POSTGRES (VPP schema/data)    | psycopg2 calls                |
| 53    | CREATE CATALOG INTEGRATION            | Fixed syntax                  |
| 68    | EXECUTE POSTGRES (live demo)          | psycopg2 insert               |

## Dependencies

- **psycopg2**: Should be available in Snowsight notebook environments. If not, add `!pip install psycopg2-binary` cell.
- **Network policy**: Required for any connection to the instance.
- **Credentials**: User must save the password from CREATE output (shown only once).

## Risk Assessment

- **Low risk**: Snowflake SQL syntax fixes are straightforward
- **Medium risk**: psycopg2 availability in Snowsight notebooks (may need `psycopg2-binary`)
- **Medium risk**: Network policy `0.0.0.0/0` is permissive for demo — note this in markdown
