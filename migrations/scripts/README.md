pyproject configuration, with an async dbapi.

# Generate fresh initial migration OR Apply changes
$ alembic revision --autogenerate -m "initial schema"


# Apply the migration
- head refers to the most recent script
$ alembic upgrade head


# Manually set database to the head division
$ alembic stamp head