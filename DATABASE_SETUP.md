# Database Setup Instructions

## Automatic Table Creation

Tables should be created automatically when the FastAPI application starts up through the `@app.on_event("startup")` handler in `main.py`.

**Why this was failing:**

- The database models weren't being imported before `Base.metadata.create_all()` was called
- SQLAlchemy needs all model classes imported to register their table definitions

**Fix applied:**

- Added explicit model imports at the top of `main.py`
- Added error handling and logging to the startup event

## Manual Database Initialization (If Needed)

If automatic table creation doesn't work, run the initialization script manually:

```bash
python init_db.py
```

This script:

1. Imports all database models to register them with Base metadata
2. Creates all tables in the database
3. Provides detailed logging of the process

## Troubleshooting

### Issue: "relation 'organizations' does not exist"

**Solution 1: Restart the application**

- The startup event should run when the app starts
- Check the logs for the message: "Database tables created successfully."

**Solution 2: Run the init script**

```bash
python init_db.py
```

**Solution 3: Check database connection**

- Verify DATABASE_URL in `.env` is correct
- Test connection to PostgreSQL/Neon database
- Ensure the user has permissions to create tables

### Issue: SSL certificate errors

The application uses SSL certificates by default. If you need to disable SSL:

1. Edit `src/database/sessionmaker.py`
2. Change `connect_args={"ssl": ssl_context}` to `connect_args={"ssl": False}`
3. Restart the application

## Database Structure

Tables created:

- `organizations` - Organization accounts
- `users` - User accounts
- `subscriptions` - Subscription plans
- `payments` - Payment records
- `patients` - Patient information
- `scans` - Skin scan records
- `detections` - Disease detections from scans
- `recommendations` - Medical recommendations
- `reports` - Generated medical reports
- `scan_usage` - Scan quota tracking

All tables have UUIDs for primary keys and are properly related with foreign keys.
