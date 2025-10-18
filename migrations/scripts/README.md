pyproject configuration, with an async dbapi.

# Generate fresh initial migration OR Apply changes
$ alembic revision --autogenerate -m "initial schema/change of schema description"

# Remove bad migration
$ rm backend/migrations/scripts/versions/{latest-migration-file.py}

# Apply the migration
- head refers to the most recent script
$ alembic upgrade head

- upgrade to a specific revision:
$ alembic upgrade <revision_id>

# Manually set database to the head division
- Stamp DB without appying migration
- Useful if you want Alembic to think the DB
is up-to-date without actually running migration
$ alembic stamp head

# Downgrade Migrations
- Reverse last migration
$ alembic downgrade -1

- Donwgrade to specific migration
$ alembic downgrade <revision_id>

# View Current DV Version
$ alembic current

# Check History of Migrations
$ alembic history

# Show Detailed Info of a Migration
$ alembic show <revision_id>



