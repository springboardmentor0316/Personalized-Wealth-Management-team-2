# PostgreSQL Migration Guide

## Overview
This guide provides step-by-step instructions for migrating the Wealth Management application from SQLite to PostgreSQL.

---

## Prerequisites

### 1. Install PostgreSQL
**Windows:**
- Download from: https://www.postgresql.org/download/windows/
- Run the installer and follow the setup wizard
- Note the password you set for the `postgres` user

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

### 2. Install Python Dependencies
```bash
pip install psycopg2-binary
```

### 3. Verify PostgreSQL Installation
```bash
# Check PostgreSQL version
psql --version

# Connect to PostgreSQL
psql -U postgres
```

---

## Migration Steps

### Step 1: Create PostgreSQL Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE wealth_management;

# Create user (optional, for better security)
CREATE USER wealth_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE wealth_management TO wealth_user;

# Exit
\q
```

### Step 2: Update Database Configuration
Create or update `.env` file in `backend/` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/wealth_management

# Alternative with dedicated user
# DATABASE_URL=postgresql://wealth_user:your_secure_password@localhost:5432/wealth_management
```

### Step 3: Initialize PostgreSQL Database
```bash
# Navigate to project root
cd d:\infosys

# Run initialization script
python init_postgresql_database.py
```

**What this does:**
- Creates all required tables
- Sets up proper relationships
- Creates indexes for performance
- Configures data types correctly

### Step 4: Migrate Data from SQLite
```bash
# Update migration script with your PostgreSQL credentials
# Edit migrate_to_postgresql.py and update postgres_config

# Run migration script
python migrate_to_postgresql.py
```

**What this does:**
- Reads data from SQLite database
- Transforms data for PostgreSQL compatibility
- Inserts data into PostgreSQL tables
- Maintains data integrity and relationships

### Step 5: Update Database Connection in Application
Edit `backend/database.py`:

```python
# Update the DATABASE_URL to use PostgreSQL
# The .env file will be used automatically
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:your_password@localhost:5432/wealth_management")

# Update engine creation
engine = create_engine(DATABASE_URL)
```

### Step 6: Test the Migration
```bash
# Start the backend server
cd backend
python main.py

# Test authentication
python test_api.py

# Test all endpoints
python test_register.py
```

---

## Migration Scripts

### 1. Database Initialization Script
**File**: `init_postgresql_database.py`

**Usage:**
```python
# Update postgres_config with your credentials
postgres_config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'wealth_management',
    'user': 'postgres',
    'password': 'your_password_here'
}

# Run initialization
python init_postgresql_database.py
```

### 2. Data Migration Script
**File**: `migrate_to_postgresql.py`

**Usage:**
```python
# Update postgres_config with your credentials
postgres_config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'wealth_management',
    'user': 'postgres',
    'password': 'your_password_here'
}

# Run migration
python migrate_to_postgresql.py
```

---

## Data Type Mapping

### SQLite to PostgreSQL Mapping

| SQLite Type | PostgreSQL Type | Notes |
|-------------|----------------|-------|
| INTEGER | SERIAL | Auto-increment primary keys |
| VARCHAR | VARCHAR(n) | String with length limit |
| TEXT | TEXT | Unlimited length text |
| REAL | NUMERIC(15,4) | High precision decimal |
| FLOAT | NUMERIC(15,4) | High precision decimal |
| DATETIME | TIMESTAMP | Date and time |
| DATE | DATE | Date only |
| BOOLEAN | BOOLEAN | True/False values |
| JSON | JSONB | Binary JSON with indexing |

### Special Considerations

1. **Enum Values**: SQLite stores enums as strings, PostgreSQL can use ENUM types
2. **JSON Data**: PostgreSQL JSONB is more efficient than SQLite JSON
3. **Auto-increment**: Use SERIAL instead of INTEGER PRIMARY KEY AUTOINCREMENT
4. **Foreign Keys**: PostgreSQL enforces foreign key constraints by default

---

## Performance Optimizations

### 1. Connection Pooling
Update `backend/database.py`:

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30
)
```

### 2. Indexes
The initialization script creates indexes for:
- User email lookups
- Foreign key relationships
- Date-based queries
- Symbol searches

### 3. Query Optimization
```python
# Use EXPLAIN ANALYZE to analyze query performance
result = db.execute("EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com'")
print(result.fetchall())
```

---

## Backup and Recovery

### Backup PostgreSQL Database
```bash
# Full backup
pg_dump -U postgres -d wealth_management > backup.sql

# Compressed backup
pg_dump -U postgres -d wealth_management | gzip > backup.sql.gz

# Schema-only backup
pg_dump -U postgres -d wealth_management --schema-only > schema.sql
```

### Restore PostgreSQL Database
```bash
# Restore from backup
psql -U postgres -d wealth_management < backup.sql

# Restore from compressed backup
gunzip -c backup.sql.gz | psql -U postgres -d wealth_management
```

### Backup SQLite Database (Before Migration)
```bash
# Copy SQLite database
cp backend/wealth_management.db backup_wealth_management.db
```

---

## Troubleshooting

### Common Issues

#### 1. Connection Refused
**Error**: `psycopg2.OperationalError: could not connect to server`

**Solution**:
- Verify PostgreSQL is running: `sudo service postgresql status`
- Check host and port in connection string
- Verify firewall settings

#### 2. Database Already Exists
**Error**: `database "wealth_management" already exists`

**Solution**:
```bash
# Drop existing database (WARNING: This deletes all data!)
psql -U postgres -c "DROP DATABASE wealth_management;"

# Then recreate it
psql -U postgres -c "CREATE DATABASE wealth_management;"
```

#### 3. Permission Denied
**Error**: `permission denied for database`

**Solution**:
```bash
# Grant privileges
psql -U postgres
GRANT ALL PRIVILEGES ON DATABASE wealth_management TO your_user;
```

#### 4. Data Type Mismatch
**Error**: `column "amount" is of type numeric but expression is of type text`

**Solution**:
- Ensure proper data type conversion in migration script
- Check column definitions match data types

---

## Validation Steps

### 1. Verify Table Creation
```bash
psql -U postgres -d wealth_management -c "\dt"
```

Expected output:
```
               List of relations
 Schema |        Name         | Type  |  Owner
--------+---------------------+-------+----------
 public | asset_allocations   | table | postgres
 public | goals               | table | postgres
 public | investments         | table | postgres
 public | market_insights     | table | postgres
 public | market_prices       | table | postgres
 public | performance_metrics | table | postgres
 public | portfolio_snapshots | table | postgres
 public | recommendations     | table | postgres
 public | simulations         | table | postgres
 public | transactions        | table | postgres
 public | user_alerts         | table | postgres
 public | user_preferences    | table | postgres
 public | users               | table | postgres
```

### 2. Verify Data Migration
```bash
# Count records in each table
psql -U postgres -d wealth_management -c "
SELECT 
    schemaname,
    tablename,
    n_tup_ins as total_records
FROM pg_stat_user_tables 
ORDER BY tablename;
"
```

### 3. Verify Data Integrity
```bash
# Check foreign key constraints
psql -U postgres -d wealth_management -c "
SELECT 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';
"
```

### 4. Test Application
```bash
# Start backend
cd backend
python main.py

# Test API endpoints
python test_api.py
python test_register.py
python test_login.py
```

---

## Rollback Plan

If migration fails, rollback to SQLite:

### 1. Stop Using PostgreSQL
```bash
# Update .env file
DATABASE_URL=sqlite:///./wealth_management.db
```

### 2. Restore SQLite Database
```bash
# If you have a backup
cp backup_wealth_management.db backend/wealth_management.db
```

### 3. Restart Application
```bash
cd backend
python main.py
```

---

## Production Deployment

### 1. Use Environment Variables
```bash
# Set production database URL
export DATABASE_URL="postgresql://user:password@production-host:5432/wealth_management"
```

### 2. Enable SSL
```python
# Update DATABASE_URL with SSL
DATABASE_URL="postgresql://user:password@production-host:5432/wealth_management?sslmode=require"
```

### 3. Connection Pooling
```python
# Configure connection pool for production
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
    pool_recycle=3600
)
```

---

## Security Best Practices

1. **Use Strong Passwords**: Generate secure passwords for database users
2. **Limit User Privileges**: Create users with minimal required permissions
3. **Enable SSL**: Use SSL for database connections in production
4. **Regular Backups**: Schedule automated backups
5. **Monitor Logs**: Monitor PostgreSQL logs for suspicious activity
6. **Update Regularly**: Keep PostgreSQL updated with security patches

---

## Maintenance

### Regular Tasks

1. **Vacuum Database**: Reclaim space and optimize performance
```bash
psql -U postgres -d wealth_management -c "VACUUM ANALYZE;"
```

2. **Reindex**: Rebuild indexes for better performance
```bash
psql -U postgres -d wealth_management -c "REINDEX DATABASE wealth_management;"
```

3. **Update Statistics**: Update query planner statistics
```bash
psql -U postgres -d wealth_management -c "ANALYZE;"
```

---

## Summary

✅ **Migration Benefits**:
- Better performance for large datasets
- Concurrent write support
- Advanced features (JSONB, full-text search)
- Better data integrity
- Scalability for production

⚠️ **Migration Risks**:
- Data loss if not backed up
- Downtime during migration
- Application compatibility issues
- Learning curve for PostgreSQL

📋 **Checklist**:
- [ ] Install PostgreSQL
- [ ] Create database and user
- [ ] Update environment variables
- [ ] Initialize PostgreSQL schema
- [ ] Backup SQLite database
- [ ] Run migration script
- [ ] Verify data integrity
- [ ] Test application
- [ ] Set up backups
- [ ] Document migration

---

## Support

For issues or questions:
1. Check PostgreSQL logs: `/var/log/postgresql/`
2. Review migration script logs
3. Test with small dataset first
4. Contact database administrator

**Migration Status**: Ready to execute
**Estimated Time**: 30-60 minutes
**Downtime**: 5-10 minutes (during migration)
