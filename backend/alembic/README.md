This directory contains Alembic migration environment.

To generate a migration locally:

1. Install alembic in your backend virtualenv:
   pip install alembic

2. Set `DATABASE_URL` in `.env` or export it in your shell.

3. Run:
   alembic revision --autogenerate -m "initial"
   alembic upgrade head

In CI or production, use the same commands to apply migrations before running the app.
