pyproject configuration, with an async dbapi.

# Generate fresh initial migration
$ alembic revision --autogenerate -m "initial schema"


# Apply the migration
- head refers to the most recent script
$ alembic upgrade head